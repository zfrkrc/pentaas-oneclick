FROM python:3.11-slim
RUN pip install dnspython netaddr lxml dnsrecon
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
