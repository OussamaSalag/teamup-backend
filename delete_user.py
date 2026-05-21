import asyncio
from app.db.session import engine
from sqlalchemy import text

async def run():
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM users WHERE email = 'test@esi-sba.dz' OR username = 'testuser'"))
        print("Deleted old test user")

if __name__ == '__main__':
    asyncio.run(run())
