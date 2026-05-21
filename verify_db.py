import asyncio
from app.db.session import engine
from sqlalchemy import text

async def verify_db():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT email, is_email_verified FROM users WHERE email = 'test.migration@esi-sba.dz'"))
        user = result.fetchone()
        
        if user:
            print("SUCCESS: User found in PostgreSQL database!")
            print(f"User: {user}")
        else:
            print("ERROR: User not found in database.")

if __name__ == "__main__":
    asyncio.run(verify_db())
