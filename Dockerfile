FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Install Python dependencies with psycopg (psycopg3) using precompiled binary wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000 for uvicorn
EXPOSE 8000

# Start uvicorn on port 8000 and celery worker, wait for both
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & celery -A app.tasks.celery worker --loglevel=info & wait"]
