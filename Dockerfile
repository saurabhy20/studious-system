# Use Python 3.10 base image
FROM python:3.10-slim

# Install build dependencies and network tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    iproute2 \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build tools
RUN apt-get purge -y --auto-remove gcc python3-dev build-essential

# Set DNS cache (reduces DNS lookup time)
RUN echo "options single-request-reopen" >> /etc/resolv.conf && \
    echo "options use-vc" >> /etc/resolv.conf

# Set entrypoint
CMD ["python", "main.py"]
