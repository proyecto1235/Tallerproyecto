import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-1234567890")
os.environ.setdefault("NODE_ENV", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.main import app
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def mock_external_services():
    mock_cursor = MagicMock()
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.execute.return_value = None

    with patch.object(PostgresConnection, "init_pool", return_value=None), \
         patch.object(PostgresConnection, "close_pool", return_value=None), \
         patch.object(PostgresConnection, "get_cursor", return_value=mock_cursor), \
         patch.object(EventRepository, "close", return_value=None), \
         patch.object(EventRepository, "log_event", new_callable=AsyncMock) as mock_log, \
         patch.object(EventRepository, "get_user_events", new_callable=AsyncMock) as mock_history, \
         patch.object(EventRepository, "get_db", new_callable=AsyncMock) as mock_db:
        mock_log.return_value = "mock_event_id"
        mock_history.return_value = []
        mock_db.return_value = None
        yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def auth_headers():
    return {"Cookie": "auth-token=mock_token"}
