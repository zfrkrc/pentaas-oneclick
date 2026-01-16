FROM python:3.11-slim
RUN apt-get update && \
    apt-get install -y git perl libnet-ssleay-perl openssl libauthen-pam-perl libio-pty-perl && \
    git clone --depth 1 https://github.com/sullo/nikto.git /opt/nikto && \
    ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto && \
    chmod +x /opt/nikto/program/nikto.pl && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../base /app/services/base/
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
