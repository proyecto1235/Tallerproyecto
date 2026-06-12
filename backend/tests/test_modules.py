import pytest


@pytest.mark.asyncio
async def test_modules_endpoint_accessible(client):
    response = await client.get("/api/modules")
    assert response.status_code in (200, 401, 403)
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "modules" in data
