# Use Python 3.10 base image
FROM python:3.10-slim

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build tools
RUN apt-get purge -y --auto-remove gcc python3-dev build-essential

# Set entrypoint
CMD ["python", "main.py"]
