FROM python:3.11-slim

# Install Wapiti3
RUN pip install --no-cache-dir wapiti3

WORKDIR /app
COPY services/wapiti/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/wapiti /app/
EXPOSE 8000
CMD ["python", "service.py"]
