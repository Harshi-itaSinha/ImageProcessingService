from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
import uuid, csv, io, datetime, re, httpx

app = FastAPI()

DATABASE_URL = "sqlite:///./image_processing.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

WEBHOOK_URL = "https://example.com/webhook"  # Replace with actual webhook endpoint


class ProcessingRequest(Base):
    __tablename__ = "processing_requests"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, unique=True, index=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    output_csv = Column(String, nullable=True)
    products = relationship("Product", back_populates="processing_request")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, ForeignKey("processing_requests.request_id"))
    serial_number = Column(String)
    product_name = Column(String)
    input_image_urls = Column(Text)
    output_image_urls = Column(Text)
    processing_request = relationship("ProcessingRequest", back_populates="products")


Base.metadata.create_all(bind=engine)

IMAGE_URL_REGEX = re.compile(r"^(https?:\/\/.*\.(?:png|jpg|jpeg|gif|bmp|webp))$", re.IGNORECASE)


def compress_image(input_url: str) -> str:
    return input_url + "?compressed=50"


async def send_webhook_notification(request_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(WEBHOOK_URL, json={"request_id": request_id, "status": "completed"})
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Webhook failed: {e}")


async def process_images(request_id: str):
    db = SessionLocal()
    try:
        pr = db.query(ProcessingRequest).filter(ProcessingRequest.request_id == request_id).first()
        if not pr:
            return
        pr.status = "processing"
        pr.updated_at = datetime.datetime.utcnow()
        db.commit()
        for product in pr.products:
            input_urls = [url.strip() for url in product.input_image_urls.split(",") if url.strip()]
            output_urls = [compress_image(url) for url in input_urls]
            product.output_image_urls = ", ".join(output_urls)
        pr.status = "completed"
        pr.updated_at = datetime.datetime.utcnow()
        db.commit()

        # Generate Output CSV
        output_csv = io.StringIO()
        writer = csv.writer(output_csv)
        writer.writerow(["S. No.", "Product Name", "Input Image Urls", "Output Image Urls"])
        for product in pr.products:
            writer.writerow(
                [product.serial_number, product.product_name, product.input_image_urls, product.output_image_urls])
        output_csv_path = f"./output_{request_id}.csv"
        with open(output_csv_path, "w", newline="") as f:
            f.write(output_csv.getvalue())
        pr.output_csv = output_csv_path
        db.commit()

        # Trigger Webhook
        await send_webhook_notification(request_id)

    except Exception:
        db.rollback()
    finally:
        db.close()


@app.post("/upload")
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    content = await file.read()
    decoded = content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(decoded))
    rows = list(csv_reader)

    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="CSV file must contain a header and at least one data row.")

    # Validate header
    expected_header = ["S. No.", "Product Name", "Input Image Urls"]
    if rows[0] != expected_header:
        raise HTTPException(status_code=400, detail=f"CSV must have headers {expected_header}, but found {rows[0]}")

    request_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        pr = ProcessingRequest(request_id=request_id, status="pending")
        db.add(pr)
        db.commit()
        db.refresh(pr)
        for row in rows[1:]:
            if len(row) < 3:
                continue
            serial_number = row[0].strip()
            product_name = row[1].strip()
            input_image_urls = row[2].strip()

            # Validate URLs using regex
            urls = [url.strip() for url in input_image_urls.split(",") if url.strip()]
            invalid_urls = [url for url in urls if not IMAGE_URL_REGEX.match(url)]
            if invalid_urls:
                raise HTTPException(status_code=400, detail=f"Invalid image URLs found: {invalid_urls}")

            product = Product(
                request_id=request_id,
                serial_number=serial_number,
                product_name=product_name,
                input_image_urls=", ".join(urls),
                output_image_urls=""
            )
            db.add(product)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error during CSV upload.")
    finally:
        db.close()

    background_tasks.add_task(process_images, request_id)
    return {"request_id": request_id}


@app.get("/status/{request_id}")
async def get_status(request_id: str):
    db = SessionLocal()
    try:
        pr = db.query(ProcessingRequest).filter(ProcessingRequest.request_id == request_id).first()
        if not pr:
            raise HTTPException(status_code=404, detail="Request ID not found.")
        products = []
        for product in pr.products:
            products.append({
                "serial_number": product.serial_number,
                "product_name": product.product_name,
                "input_image_urls": product.input_image_urls,
                "output_image_urls": product.output_image_urls
            })
        return {
            "request_id": request_id,
            "status": pr.status,
            "products": products,
            "output_csv": pr.output_csv
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
