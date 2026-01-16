FROM golang:1.23-bookworm AS builder
RUN go install github.com/hahwul/dalfox/v2@latest

FROM python:3.11-slim
COPY --from=builder /go/bin/dalfox /usr/local/bin/dalfox

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
