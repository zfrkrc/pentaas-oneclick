FROM python:3.11-slim

# Install git-dumper and dependencies
RUN pip install --no-cache-dir git-dumper requests beautifulsoup4

WORKDIR /app
COPY services/gittools/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/base /app/services/base/
COPY services/gittools /app/
EXPOSE 8000
CMD ["python", "service.py"]
