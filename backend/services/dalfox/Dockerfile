FROM hahwul/dalfox:latest
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python3", "service.py"]
