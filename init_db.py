import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.db.session import engine, Base
import app.models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB OK")

if __name__ == "__main__":
    asyncio.run(init_db())