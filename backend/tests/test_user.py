import pytest


@pytest.mark.asyncio
async def test_root_endpoint_returns_version(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0"
