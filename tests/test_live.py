import pytest

@pytest.mark.asyncio
async def test_live_summary(client):
    s = await client.post("/api/sessions", json={"title": "Planning"})
    sid = s.json()["id"]
    await client.post(f"/api/sessions/{sid}/bullets", json={"text": "Ship batch upgrades this week"})
    await client.post(f"/api/sessions/{sid}/decisions", json={"text": "Use mock LLM in CI"})
    r = await client.post(f"/api/sessions/{sid}/summarize")
    assert r.status_code == 200
    assert r.json()["summary"]
