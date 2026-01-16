FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ruby-full build-essential libcurl4-openssl-dev libxml2 libxml2-dev libxslt1-dev ruby-dev libgmp-dev zlib1g-dev && \
    gem install wpscan && \
    wpscan --update && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ../base /app/services/base/
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
