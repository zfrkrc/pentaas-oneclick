FROM python:3.11-slim

# docker + compose plugin
RUN apt-get update && \
  apt-get install -y ca-certificates curl gnupg lsb-release openvpn iproute2 && \
  curl -fsSL https://get.docker.com | sh && \
  mkdir -p /usr/lib/docker/cli-plugins && \
  curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 \
  -o /usr/lib/docker/cli-plugins/docker-compose && \
  chmod +x /usr/lib/docker/cli-plugins/docker-compose && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
