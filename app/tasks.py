import csv
import os
import json
from celery import Celery
from app.database import engine
from app.models import Product, Webhook
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import asyncio

celery=Celery(__name__,broker=os.getenv("REDIS_URL","redis://localhost:6379/0"))
@celery.task(bind=True)
def import_products_from_csv(self, file_path: str, task_id: str):
    total_processed = 0
    batch_size=1000
    batch=[]
    expected = {"sku", "name", "description", "price"}
    batch=[]
    
    with open(file_path,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        for row in reader:
            if expected - row.keys():
                continue
            sku=row['sku'].strip()
            if not sku:
                continue
            
            batch.append({
                'sku': sku,
                'name': row['name'].strip()[:255],
                'description': row.get('description','').strip()[:1000],
                'price': float(row['price']) if row.get('price') else 0.0
            })

            if len(batch)>=batch_size:
                process_batch(batch,task_id)
                total_processed+=len(batch)
                self.update_state(state="PROGRESS",
                                  meta={"current": total_processed, "total": 500000, "status": "Importing..."})
                batch=[]
        
        if batch:
            process_batch(batch,task_id)
            total_processed+=len(batch)

    asyncio.run(trigger_webhooks(total_processed))

    os.unlink(file_path)
def process_batch(batch,task_id):
    from sqlalchemy import create_engine
    engine_sync = create_engine(os.getenv("DATABASE_URL").replace("asyncpg","psycopg2"))
    insert_stmt = pg_insert(Product).values(batch)
    stmt = insert_stmt.on_conflict_do_update(
        index_elements=['sku_upper'],
        set_={
            'name': insert_stmt.excluded.name,
            'description': insert_stmt.excluded.description,
            'price': insert_stmt.excluded.price,
            'active': True
        })
    with engine_sync.begin() as conn:
        conn.execute(stmt)
    with engine_sync.begin() as conn:
        conn.execute(stmt)

async def trigger_webhooks(count):
    async with AsyncSession(engine) as db:
        result= await db.execute(select(Webhook).where(Webhook.enabled))
        hooks=result.scalars().all()

        payload = {
            "event": "products.imported",
            "total": count,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            for hook in hooks:
                try:
                    await client.post(hook.url, json=payload)
                except:
                    pass