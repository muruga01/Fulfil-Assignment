FROM python:3.12-slim

# Install system dependencies needed to build psycopg2 from source
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000 for uvicorn
EXPOSE 8000

# Start uvicorn on port 8000 and celery worker, wait for both
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & celery -A app.tasks.celery worker --loglevel=info & wait"]