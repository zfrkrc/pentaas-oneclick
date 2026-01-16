FROM projectdiscovery/nuclei:latest

WORKDIR /app
COPY requirements.txt .
RUN apk add --no-cache python3 py3-pip && pip install --no-cache-dir -r requirements.txt
COPY . /app/

EXPOSE 8000
CMD ["python3", "services/nuclei/service.py"]
