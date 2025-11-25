import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Heroku provides DATABASE_URL automatically
if os.getenv("DATABASE_URL"):
    # Convert for asyncpg (Heroku uses psycopg2 by default)
    DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql+asyncpg://")
else:
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/acme"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session