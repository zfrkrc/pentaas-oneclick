FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y default-jre wget unzip && \
    wget -qO /tmp/zap.tar.gz https://github.com/zaproxy/zaproxy/releases/download/v2.15.0/ZAP_2.15.0_Linux.tar.gz && \
    mkdir -p /opt/zap && \
    tar -xf /tmp/zap.tar.gz -C /opt/zap --strip-components=1 && \
    printf '#!/bin/bash\n/opt/zap/zap.sh -cmd -quickurl "$@" -quickprogress' > /usr/local/bin/zap && \
    chmod +x /usr/local/bin/zap && \
    rm /tmp/zap.tar.gz && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
