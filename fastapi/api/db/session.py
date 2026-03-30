from core.config import DATABASE_URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

import asyncio

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def wait_for_db(engine: AsyncEngine, retries: int = 15, delay: int = 2):
    for attempt in range(retries):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            print(f"⚠ Attempt {attempt + 1}/{retries} failed: {e}")
            await asyncio.sleep(delay)
    raise RuntimeError("Cannot connect to the database after multiple attempts")