import pytest
import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["POSTGRES_PASSWORD"] = "test"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["OLLAMA_URL"] = "http://localhost:11434"
os.environ["DEBUG"] = "False"

from application.services.ml.synthetic_dataset import (
    generate_dataset, build_training_data, FEATURE_NAMES,
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
