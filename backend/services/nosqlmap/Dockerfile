FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone NoSQLMap
RUN git clone --depth 1 https://github.com/codingo/NoSQLMap.git /opt/nosqlmap

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r /opt/nosqlmap/requirements.txt
COPY services/nosqlmap/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/nosqlmap /app/
EXPOSE 8000
CMD ["python", "service.py"]
