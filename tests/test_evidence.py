import pytest, io

@pytest.mark.asyncio
async def test_evidence_upload(client, auth_headers):
    case_resp = await client.post("/api/v1/cases", json={"title": "Pipeline Test", "crime_type": "fraud"}, headers=auth_headers)
    case_id = case_resp.json()["id"]
    fake_doc = io.BytesIO(b"Suspect John Doe was seen at Market Street transferring $50,000.")
    resp = await client.post(
        "/api/v1/evidence/upload",
        data={"case_id": case_id, "type": "document"},
        files={"file": ("test.txt", fake_doc, "text/plain")},
        headers=auth_headers
    )
    assert resp.status_code == 200
    assert "evidence_id" in resp.json()

@pytest.mark.asyncio
async def test_evidence_hash_consistency(client, auth_headers):
    case_resp = await client.post("/api/v1/cases", json={"title": "Hash Test", "crime_type": "test"}, headers=auth_headers)
    case_id = case_resp.json()["id"]
    content = b"Consistent content for hash test."
    r1 = await client.post("/api/v1/evidence/upload", data={"case_id": case_id, "type": "doc"}, files={"file": ("f1.txt", io.BytesIO(content), "text/plain")}, headers=auth_headers)
    r2 = await client.post("/api/v1/evidence/upload", data={"case_id": case_id, "type": "doc"}, files={"file": ("f2.txt", io.BytesIO(content), "text/plain")}, headers=auth_headers)
    assert r1.json()["hash"] == r2.json()["hash"]
