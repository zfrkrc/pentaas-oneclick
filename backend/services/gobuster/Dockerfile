FROM golang:alpine AS builder

# Install gobuster
RUN go install github.com/OJ/gobuster/v3@latest

FROM python:3.11-slim

# Copy gobuster binary from builder
COPY --from=builder /go/bin/gobuster /usr/local/bin/gobuster

# Install CA certificates for HTTPS
RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create wordlist directory
RUN mkdir -p /usr/share/wordlists

# Copy wordlist
COPY services/gobuster/wordlist.txt /usr/share/wordlists/common.txt

WORKDIR /app

COPY services/gobuster/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/gobuster /app/
EXPOSE 8000
CMD ["python", "service.py"]
