FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y default-jre wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN wget --no-check-certificate -O /tmp/zap.tar.gz https://github.com/zaproxy/zaproxy/releases/download/v2.17.0/ZAP_2.17.0_Linux.tar.gz && \
    mkdir -p /opt && \
    tar -xzf /tmp/zap.tar.gz -C /opt && \
    mv /opt/ZAP_* /opt/zap && \
    rm /tmp/zap.tar.gz

RUN printf '#!/bin/bash\n/opt/zap/zap.sh -cmd -quickurl "$@" -quickprogress\n' > /usr/local/bin/zap && \
    chmod +x /usr/local/bin/zap

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../base /app/services/base/
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
