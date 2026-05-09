import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="session")
async def auth_headers(client):
    await client.post("/api/v1/auth/register", json={
        "name": "Test Officer", "email": "test@raw.ai", "password": "test123", "role": "officer"
    })
    resp = await client.post("/api/v1/auth/login", data={"username": "test@raw.ai", "password": "test123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
