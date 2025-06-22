# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /app

# Install Python dependencies (keep build tools during installation)
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build tools AFTER installation
RUN apt-get purge -y --auto-remove gcc python3-dev build-essential

# Set entrypoint
CMD ["python", "main.py"]
