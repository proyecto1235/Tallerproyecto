import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-1234567890"
os.environ["NODE_ENV"] = "test"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["OLLAMA_URL"] = "http://localhost:11434"
os.environ["DEBUG"] = "False"

from app.main import app
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository

# ── ML fixtures ──
from application.services.ml.synthetic_dataset import (
    generate_dataset, build_training_data,
    extract_features_for_engagement, extract_features_for_performance,
    extract_features_for_dropout, extract_features_for_frustration,
    extract_features_for_clustering, extract_features_for_anomaly,
)
from application.services.ml.orchestrator import MLOrchestrator
from application.services.ml.engagement_predictor import EngagementPredictor
from application.services.ml.performance_predictor import PerformancePredictor
from application.services.ml.dropout_predictor import DropoutPredictor
from application.services.ml.frustration_predictor import FrustrationPredictor
from application.services.ml.clustering import LearningClustering
from application.services.ml.anomaly_detector import AnomalyDetector
from application.services.ml.recommender import Recommender


@pytest.fixture(scope="session")
def synthetic_dataset() -> pd.DataFrame:
    return generate_dataset(n_students=500, n_weeks=6, seed=123)


@pytest.fixture(scope="session")
def training_data(synthetic_dataset):
    return build_training_data(synthetic_dataset, target_week=5)


@pytest.fixture(scope="session")
def orchestrator():
    orch = MLOrchestrator()
    if not orch.engagement._is_trained:
        orch.train_all()
    return orch


@pytest.fixture(scope="function")
def engagement_predictor():
    return EngagementPredictor()


@pytest.fixture(scope="function")
def performance_predictor():
    return PerformancePredictor()


@pytest.fixture(scope="function")
def dropout_predictor():
    return DropoutPredictor()


@pytest.fixture(scope="function")
def frustration_predictor():
    return FrustrationPredictor()


@pytest.fixture(scope="function")
def clustering():
    return LearningClustering()


@pytest.fixture(scope="function")
def anomaly_detector():
    return AnomalyDetector()


@pytest.fixture(scope="function")
def recommender():
    return Recommender()


@pytest.fixture
def sample_student_week():
    return {
        "session_days": 5,
        "total_sessions": 12,
        "total_time_minutes": 480,
        "exercise_attempts": 15,
        "passed_exercises": 12,
        "error_rate": 0.20,
        "forum_interactions": 4,
        "content_views": 10,
    }


# ── Integration test fixtures ──

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
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
    from httpx import ASGITransport, AsyncClient
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def auth_headers():
    return {"Cookie": "auth-token=mock_token"}
