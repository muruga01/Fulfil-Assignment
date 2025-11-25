GitHub: https://github.com/muruga01/Fulfil-Assignment

What It Does (All Requirements Done)

Upload huge CSV files (500K+ rows)
Real-time progress bar
SKU is unique (case-insensitive) - duplicates get overwritten
View, search, edit, delete products
Bulk delete all products (with confirmation)
Add, test, delete webhooks
Clean and simple UI

Tech Stack

FastAPI (Python)
PostgreSQL
Redis
Celery (background jobs)
HTMX + Tailwind (no React)
Deployed on Render (free tier)

How to Run Locally (1 Command)
Bashgit clone https://github.com/yourusername/acme-product-importer.git
cd acme-product-importer
docker-compose up --build
Open → http://localhost:8000
Test CSV (100K rows)
https://raw.githubusercontent.com/devjared/acme-product-importer/main/sample_100k.csv
Deploy Yourself (Free on Render)

Fork this repo
Go to render.com → New Web Service → Connect your fork
Add free PostgreSQL + free Redis (Key Value)
Add 2 environment variables (use internal URLs):
DATABASE_URL → change postgres:// to postgresql+asyncpg://
REDIS_URL → copy from Redis

Deploy → Done!

That’s it.
Simple, fast, works perfectly, 100% free.
