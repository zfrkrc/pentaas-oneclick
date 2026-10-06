FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone Commix
RUN git clone --depth 1 https://github.com/commixproject/commix.git /opt/commix

WORKDIR /app
COPY services/commix/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/commix /app/
EXPOSE 8000
CMD ["python", "service.py"]
