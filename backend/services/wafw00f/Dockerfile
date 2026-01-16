FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt wafw00f
COPY . /app/
EXPOSE 8000
CMD ["python", "service.py"]
