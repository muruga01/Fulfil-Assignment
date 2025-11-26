import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Heroku provides DATABASE_URL automatically
if os.getenv("DATABASE_URL"):
    # Adjust for psycopg URL scheme
    DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql+psycopg://")
else:
    DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost/acme"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session