FROM python:3.11-slim

# Copy dalfox binary from official image
COPY --from=hahwul/dalfox:latest /app/dalfox /usr/local/bin/dalfox

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
