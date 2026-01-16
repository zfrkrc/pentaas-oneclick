FROM wpscanteam/wpscan:latest
RUN apk add python3 py3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python3", "service.py"]
