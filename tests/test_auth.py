import pytest

@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/v1/auth/register", json={
        "name": "Officer A", "email": "officer_a@raw.ai", "password": "secure123", "role": "officer"
    })
    assert resp.status_code == 200
    assert resp.json()["email"] == "officer_a@raw.ai"

@pytest.mark.asyncio
async def test_login(client):
    resp = await client.post("/api/v1/auth/login", data={"username": "officer_a@raw.ai", "password": "secure123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    resp = await client.post("/api/v1/auth/login", data={"username": "officer_a@raw.ai", "password": "wrong"})
    assert resp.status_code == 401
