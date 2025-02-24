# Image Processing API

## Overview
This FastAPI-based service allows users to upload CSV files containing product details and image URLs. The system processes the images and provides the processed image URLs, along with a status API for tracking progress.

## Features
- CSV Upload API for bulk processing.
- Image file upload support.
- Background task execution for image compression.
- Status API for tracking processing requests.
- Webhook notifications when processing is complete.
- Uses SQLite for request and product storage.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/image-processing-api.git
   cd image-processing-api
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate     # For Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the FastAPI application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## API Documentation
FastAPI provides interactive documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

To download the OpenAPI JSON:
```bash
curl -o openapi.json http://127.0.0.1:8000/openapi.json
```

## Flow Diagram
![Flow Diagram](docs/flow_diagram.png)
<img width="1175" alt="Screenshot 2025-02-25 at 1 34 07 AM" src="https://github.com/user-attachments/assets/2fa5995b-5bf6-4a22-9939-aac6cd123c84" />


## Sequence Diagram
![Sequence Diagram](docs/sequence_diagram.png)
<img width="1171" alt="Screenshot 2025-02-25 at 1 33 41 AM" src="https://github.com/user-attachments/assets/d09bc96c-4033-4dd7-9f00-d15459a4ab9c" />

## Class Diagram
![Class Diagram](docs/class_diagram.png)<img width="736" alt="Screenshot 2025-02-25 at 1 32 36 AM" src="https://github.com/user-attachments/assets/7f957da8-6525-46ad-90dd-6d00cb183eaf" />


## Postman Collection
To test the API endpoints using Postman:
1. Download the Postman collection: [Postman Collection](docs/postman_collection.json)
2. Import it into Postman by clicking **Import** and selecting the downloaded file.
3. Configure the base URL as `https://imageprocessingservice-4di9.onrender.com`.

Alternatively, you can access the shared Postman workspace: [Postman Workspace](https://www.postman.com/altimetry-meteorologist-83164959/workspace/image-processing/request/42352105-96690377-91a1-47c1-a94e-dbbdd8fb7d17?action=share&creator=42352105&ctx=documentation)

## API Endpoints
### 1. Upload CSV
**Endpoint:** `POST /upload`
- Accepts a CSV file with product details.
- Stores request in the database and starts background processing.
- Returns a `request_id` for tracking.

**Response:**
```json
{
    "request_id": "e2b43657-3f23-4ae3-8865-6309dda7e02f"
}
```

**cURL Example:**
```bash
curl --location 'https://imageprocessingservice-4di9.onrender.com/upload' \
--header 'accept: application/json' \
--form 'file=@"postman-cloud:///1eff2cbc-7df7-4c90-ab5b-fa5fc2334f21"'
```

### 2. Upload Image
**Endpoint:** `POST /upload-image/`
- Accepts an image file (JPEG, PNG, GIF, WebP).
- Stores the uploaded image and returns a URL.

**Response:**
```json
{
    "filename": "e2b43657-3f23-4ae3-8865-6309dda7e02f.png",
    "url": "/images/e2b43657-3f23-4ae3-8865-6309dda7e02f.png"
}
```

### 3. Get Processing Status
**Endpoint:** `GET /status/{request_id}`
- Fetches the status of an image processing request.
- Returns processed image URLs when ready.

**Response:**
```json
{
    "request_id": "e2b43657-3f23-4ae3-8865-6309dda7e02f",
    "status": "completed",
    "products": [...],
    "output_csv": "./output_e2b43657-3f23-4ae3-8865-6309dda7e02f.csv"
}
```

**cURL Example:**
```bash
curl --location 'https://imageprocessingservice-4di9.onrender.com/status/e37d2359-3d09-47db-a668-2'
```

## Future Improvements
### Push File to Image Processing Service via Queue
Instead of processing images directly in the FastAPI service, we can:
- Integrate **Celery + Redis** or **AWS SQS** to push tasks to an external image processing service.
- This makes the system more scalable and fault-tolerant.

### Optimizing Status Retrieval
- **Polling:** Clients can regularly poll `/status/{request_id}` to check processing progress.
- **Webhooks:** Instead of polling, clients can provide a webhook URL, and the system will notify them when processing is complete.

## License
This project is licensed under the MIT License.

