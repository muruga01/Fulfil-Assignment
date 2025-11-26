from fastapi import FastAPI, Request, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from app.database import engine, get_db
from app.models import Base, Product, Webhook
from app.tasks import import_csv_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
import os, uuid, shutil, redis, json

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def startup():
    # Retry connecting to DB on startup
    for i in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except OperationalError:
            if i == 9:
                raise
            await asyncio.sleep(3)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Upload + Start Task
@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), background: BackgroundTasks = None):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    task = import_csv_task.delay(file_path, str(uuid.uuid4()))
    return {"task_id": task.id}

# SSE Progress
@app.get("/progress/{task_id}")
async def progress(task_id: str):
    def event_stream():
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        p = r.pubsub()
        p.subscribe("import_progress")
        yield f"data: {json.dumps({'percent': 0, 'status': 'Starting...'})}\n\n"
        for message in p.listen():
            if message["type"] == "message":
                yield f"data: {message['data'].decode()}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# Product List + CRUD
@app.get("/products", response_class=HTMLResponse)
async def list_products(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).order_by(Product.id.desc()).limit(100))
    products = result.scalars().all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products})

@app.post("/products/bulk-delete")
async def bulk_delete(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Product))
    await db.commit()
    return {"status": "deleted"}

# Webhooks
@app.get("/webhooks", response_class=HTMLResponse)
async def webhooks_ui(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Webhook))
    hooks = result.scalars().all()
    return templates.TemplateResponse("webhooks.html", {"request": request, "hooks": hooks})