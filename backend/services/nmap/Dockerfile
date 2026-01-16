FROM python:3.11-slim

# Install Nmap
RUN apt-get update && \
    apt-get install -y nmap && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . /app/

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "services/nmap/service.py"]
