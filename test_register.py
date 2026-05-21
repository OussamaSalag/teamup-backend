import asyncio
import httpx

async def test_register():
    base_url = "http://127.0.0.1:8000/api/v1/auth"
    
    async with httpx.AsyncClient() as client:
        print("Testing Fast Register...")
        r = await client.post(f"{base_url}/register", json={
            "email": "test@esi-sba.dz",
            "password": "test1234",
            "full_name": "Test User",
            "username": "testuser"
        })
        print("Register Status:", r.status_code)
        try:
            resp = r.json()
            print("Response:", resp)
            if "access_token" in resp:
                print("Token successfully returned!")
        except Exception as e:
            print("Response text:", r.text)

if __name__ == "__main__":
    asyncio.run(test_register())
