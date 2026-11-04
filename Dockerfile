FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize database on startup
ENV DATABASE_PATH=/data/vocabulary.db

# Create data directory
RUN mkdir -p /data

EXPOSE 8080

CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && gunicorn --bind 0.0.0.0:8080 app:app"]
