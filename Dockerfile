# Use official Python base image
FROM python:3.10

# Set working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn httpx sqlalchemy sqlite3 csv python-multipart

# Expose port (FastAPI default: 8000)
EXPOSE 8000

# Command to run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
