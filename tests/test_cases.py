import pytest

@pytest.mark.asyncio
async def test_create_case(client, auth_headers):
    resp = await client.post("/api/v1/cases", json={"title": "Test Murder Case", "crime_type": "homicide"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Murder Case"
    assert resp.json()["status"] == "open"

@pytest.mark.asyncio
async def test_list_cases(client, auth_headers):
    resp = await client.get("/api/v1/cases", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
