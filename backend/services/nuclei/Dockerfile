FROM golang:1.23-bookworm AS builder
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

FROM python:3.11-slim
COPY --from=builder /go/bin/nuclei /usr/local/bin/nuclei

RUN apt-get update && \
    apt-get install -y git && \
    nuclei -update-templates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

EXPOSE 8000
CMD ["python", "service.py"]
