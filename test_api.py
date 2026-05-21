import asyncio
import httpx

async def test_auth():
    base_url = "http://127.0.0.1:8000/api/v1/auth"
    email = "test.migration@esi-sba.dz"
    password = "password123"
    
    async with httpx.AsyncClient() as client:
        print("1. Testing Register...")
        r1 = await client.post(f"{base_url}/register", json={
            "email": email,
            "password": password,
            "full_name": "Test Migration",
            "username": "test_mig"
        })
        print("Register Status:", r1.status_code)
        try:
            print("Response:", r1.json())
        except:
            print("Response text:", r1.text)
            
        print("\n2. Testing Verify Email...")
        r2 = await client.post(f"{base_url}/verify-email", json={
            "email": email,
            "otp_code": "123456" # Using default dummy OTP from earlier code context
        })
        print("Verify Status:", r2.status_code)
        try:
            print("Response:", r2.json())
        except:
            print("Response text:", r2.text)
            
        print("\n3. Testing Login...")
        r3 = await client.post(f"{base_url}/login", data={
            "username": email,
            "password": password,
            "grant_type": "password"
        })
        print("Login Status:", r3.status_code)
        try:
            print("Response:", r3.json())
            if "access_token" in r3.json():
                print("Login successful! Got access token.")
        except:
            print("Response text:", r3.text)

if __name__ == "__main__":
    asyncio.run(test_auth())
