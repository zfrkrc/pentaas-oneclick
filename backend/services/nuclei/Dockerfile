FROM golang:latest AS builder
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

FROM python:3.11-slim
COPY --from=builder /go/bin/nuclei /usr/local/bin/nuclei

RUN apt-get update && \
    apt-get install -y git && \
    nuclei -update-templates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY services/nuclei/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/nuclei /app/

EXPOSE 8000
CMD ["python", "service.py"]
