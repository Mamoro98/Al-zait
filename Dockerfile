# Al Zait News Agent - Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Expose port (Google Cloud Run uses PORT env variable)
EXPOSE 8080

# Start command - use GCP start script if available, otherwise regular start script
CMD ["python", "start-gcp.py"]
