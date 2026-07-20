FROM golang:latest AS builder
RUN go install github.com/hahwul/dalfox/v2@v2.12.0

FROM python:3.11-slim
COPY --from=builder /go/bin/dalfox /usr/local/bin/dalfox

WORKDIR /app
COPY services/dalfox/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/dalfox /app/
EXPOSE 8000
CMD ["python", "service.py"]
