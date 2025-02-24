# Image Processing API

## Overview
This FastAPI-based service allows users to upload CSV files containing product details and image URLs. The system processes the images and provides the processed image URLs, along with a status API for tracking progress.

## Features
- CSV Upload API for bulk processing.
- Background task execution for image compression.
- Status API for tracking processing requests.
- Webhook notifications when processing is complete.
- Uses SQLite for request and product storage.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone [git repo link](https://github.com/Harshi-itaSinha/ImageProcessingService.git)
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

## Sequence Diagram
![Sequence Diagram](docs/sequence_diagram.png)

## Class Diagram
![Class Diagram](docs/class_diagram.png)

## Postman Collection
you can access the shared Postman workspace:([Postman Workspace](https://www.postman.com/altimetry-meteorologist-83164959/workspace/image-processing/collection/42352105-7bac7468-4591-40f1-a638-f58b753520b1?action=share&creator=42352105))

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

### 2. Get Processing Status
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

