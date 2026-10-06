FROM golang:1.25-alpine AS builder

RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest

FROM python:3.11-slim

COPY --from=builder /go/bin/httpx /usr/local/bin/httpx

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY services/httpx/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/httpx /app/
EXPOSE 8000
CMD ["python", "service.py"]
