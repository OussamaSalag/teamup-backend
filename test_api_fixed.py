import asyncio
import httpx
from app.db.session import engine
from sqlalchemy import text

async def get_otp(email):
    async with engine.begin() as conn:
        result = await conn.execute(text(f"SELECT email_verify_code FROM users WHERE email = '{email}'"))
        user = result.fetchone()
        return user[0] if user else None

async def test_auth():
    base_url = "http://127.0.0.1:8000/api/v1/auth"
    email = "test.migration2@esi-sba.dz"
    password = "password123"
    
    async with httpx.AsyncClient() as client:
        print("1. Testing Register...")
        r1 = await client.post(f"{base_url}/register", json={
            "email": email,
            "password": password,
            "full_name": "Test Migration 2",
            "username": "test_mig2"
        })
        print("Register Status:", r1.status_code)
        
        print("\nFetching OTP from DB...")
        otp = await get_otp(email)
        print("OTP:", otp)
            
        print("\n2. Testing Verify Email...")
        r2 = await client.post(f"{base_url}/verify-email", json={
            "email": email,
            "code": otp
        })
        print("Verify Status:", r2.status_code)
        if r2.status_code == 200:
            print("Token received after verify:", "access_token" in r2.json())
            
        print("\n3. Testing Login...")
        r3 = await client.post(f"{base_url}/login", json={
            "email": email,
            "password": password
        })
        print("Login Status:", r3.status_code)
        if r3.status_code == 200:
            print("Login successful! Got access token:", "access_token" in r3.json())

if __name__ == "__main__":
    asyncio.run(test_auth())
