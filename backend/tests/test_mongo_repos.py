import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone


_await = lambda c: asyncio.run(c)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_mongo_state():
    for cls in (None,):
        pass


from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository
from infrastructure.adapters.output.mongo.behavioral_repository import BehavioralRepository
from infrastructure.adapters.output.mongo.ml_predictions_repository import MLPredictionsRepository
from infrastructure.adapters.output.mongo.student_metrics_repository import StudentMetricsRepository
from infrastructure.adapters.output.mongo.weekly_metrics_repository import WeeklyMetricsRepository


@pytest.fixture(autouse=True)
def reset_mongo():
    """Reset class-level mongo state before each test."""
    for cls in [EventRepository, BehavioralRepository, MLPredictionsRepository,
                StudentMetricsRepository, WeeklyMetricsRepository]:
        cls._client = None
        cls._db = None
        cls._available = None
    yield


@pytest.fixture
def mock_db():
    return MagicMock(name="mock_db")


@pytest.fixture
def mock_mongo_event(mock_db):
    with patch('infrastructure.adapters.output.mongo.event_repository_impl.MongoClient') as mc:
        with patch.object(EventRepository, '_try_connect', new_callable=AsyncMock, return_value=True):
            with patch.object(EventRepository, 'get_db', new_callable=AsyncMock, return_value=mock_db):
                yield mock_db


@pytest.fixture
def mock_mongo_behavioral(mock_db):
    with patch('infrastructure.adapters.output.mongo.behavioral_repository.MongoClient') as mc:
        with patch.object(BehavioralRepository, '_try_connect', new_callable=AsyncMock, return_value=True):
            with patch.object(BehavioralRepository, 'get_db', new_callable=AsyncMock, return_value=mock_db):
                yield mock_db


@pytest.fixture
def mock_mongo_ml(mock_db):
    with patch('infrastructure.adapters.output.mongo.ml_predictions_repository.MongoClient') as mc:
        with patch.object(MLPredictionsRepository, '_try_connect', new_callable=AsyncMock, return_value=True):
            with patch.object(MLPredictionsRepository, 'get_db', new_callable=AsyncMock, return_value=mock_db):
                yield mock_db


@pytest.fixture
def mock_mongo_metrics(mock_db):
    with patch('infrastructure.adapters.output.mongo.student_metrics_repository.MongoClient') as mc:
        with patch.object(StudentMetricsRepository, '_try_connect', new_callable=AsyncMock, return_value=True):
            with patch.object(StudentMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=mock_db):
                yield mock_db


@pytest.fixture
def mock_mongo_weekly(mock_db):
    with patch('infrastructure.adapters.output.mongo.weekly_metrics_repository.MongoClient') as mc:
        with patch.object(WeeklyMetricsRepository, '_try_connect', new_callable=AsyncMock, return_value=True):
            with patch.object(WeeklyMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=mock_db):
                yield mock_db


# ===================================================================
# EventRepository
# ===================================================================

class TestEventRepository:

    def make(self):
        return EventRepository()

    def test_log_event(self, mock_mongo_event):
        mock_mongo_event.events.insert_one.return_value.inserted_id = "abc123"
        repo = self.make()
        result = _await(repo.log_event("login", 1, {"ip": "127.0.0.1"}))
        assert result == "abc123"

    def test_log_event_db_none(self):
        repo = self.make()
        with patch.object(EventRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.log_event("login", 1, {}))
            assert result is None

    def test_log_exercise_attempt(self, mock_mongo_event):
        mock_mongo_event.exercise_attempts.insert_one.return_value.inserted_id = "def456"
        repo = self.make()
        result = _await(repo.log_exercise_attempt(1, 10, True, 0.95))
        assert result == "def456"

    def test_log_exercise_attempt_db_none(self):
        repo = self.make()
        with patch.object(EventRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.log_exercise_attempt(1, 10, True, 0.95))
            assert result is None

    def test_get_user_events(self, mock_mongo_event):
        mock_mongo_event.events.find.return_value.sort.return_value = [
            {"_id": "x", "event_type": "login", "user_id": 1},
        ]
        repo = self.make()
        result = _await(repo.get_user_events(1))
        assert len(result) == 1
        assert result[0]["_id"] == "x"

    def test_get_user_exercise_history(self, mock_mongo_event):
        mock_mongo_event.exercise_attempts.find.return_value.sort.return_value.limit.return_value = [
            {"_id": "y", "user_id": 1},
        ]
        repo = self.make()
        result = _await(repo.get_user_exercise_history(1))
        assert len(result) == 1

    def test_save_progress_snapshot(self, mock_mongo_event):
        mock_mongo_event.progress_snapshots.insert_one.return_value.inserted_id = "snap1"
        repo = self.make()
        result = _await(repo.save_progress_snapshot(1, {"score": 80}))
        assert result == "snap1"

    def test_log_chat_interaction(self, mock_mongo_event):
        mock_mongo_event.chat_interactions.insert_one.return_value.inserted_id = "chat1"
        repo = self.make()
        result = _await(repo.log_chat_interaction(1, "hi", "hello", "sess1"))
        assert result == "chat1"

    def test_event_exception_returns_none(self, mock_mongo_event):
        mock_mongo_event.events.insert_one.side_effect = Exception("mongo error")
        repo = self.make()
        result = _await(repo.log_event("login", 1, {}))
        assert result is None

    def test_get_user_events_filtered(self, mock_mongo_event):
        mock_mongo_event.events.find.return_value.sort.return_value = [
            {"_id": "z", "event_type": "logout", "user_id": 1},
        ]
        repo = self.make()
        result = _await(repo.get_user_events(1, "logout"))
        assert len(result) == 1


# ===================================================================
# BehavioralRepository
# ===================================================================

class TestBehavioralRepository:

    def make(self):
        return BehavioralRepository()

    def test_log_session_start(self, mock_mongo_behavioral):
        repo = self.make()
        _await(repo.log_session_start(1, "sess1"))
        mock_mongo_behavioral.sessions.insert_one.assert_called_once()

    def test_log_session_start_db_none(self):
        repo = self.make()
        with patch.object(BehavioralRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.log_session_start(1, "sess1"))
            assert result is None

    def test_log_session_activity(self, mock_mongo_behavioral):
        repo = self.make()
        _await(repo.log_session_activity(1, "sess1"))
        mock_mongo_behavioral.sessions.update_one.assert_called_once()

    def test_log_session_activity_db_none(self):
        repo = self.make()
        with patch.object(BehavioralRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.log_session_activity(1, "sess1"))
            assert result is None

    def test_log_session_end(self, mock_mongo_behavioral):
        mock_mongo_behavioral.sessions.find_one_and_update.return_value = {
            "started_at": datetime.now(timezone.utc),
            "ended_at": datetime.now(timezone.utc),
            "events_count": 5,
        }
        repo = self.make()
        result = _await(repo.log_session_end(1, "sess1"))
        assert result > 0

    def test_log_session_end_no_session(self, mock_mongo_behavioral):
        mock_mongo_behavioral.sessions.find_one_and_update.return_value = None
        repo = self.make()
        result = _await(repo.log_session_end(1, "sess1"))
        assert result == 0

    def test_log_session_end_db_none(self):
        repo = self.make()
        with patch.object(BehavioralRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.log_session_end(1, "sess1"))
            assert result == 0

    def test_log_exercise_action(self, mock_mongo_behavioral):
        repo = self.make()
        _await(repo.log_exercise_action(1, 10, 1, "run", {"key": "val"}))
        mock_mongo_behavioral.behavioral_events.insert_one.assert_called_once()

    def test_log_frustration_signal(self, mock_mongo_behavioral):
        repo = self.make()
        _await(repo.log_frustration_signal(1, 10, "timeout", "too slow"))
        mock_mongo_behavioral.frustration_signals.insert_one.assert_called_once()

    def test_log_code_analysis(self, mock_mongo_behavioral):
        repo = self.make()
        _await(repo.log_code_analysis(1, 10, "print(1)", "syntax", "SyntaxError"))
        mock_mongo_behavioral.code_analysis.insert_one.assert_called_once()

    def test_update_engagement_score(self, mock_mongo_behavioral):
        mock_mongo_behavioral.behavioral_events.count_documents.return_value = 10
        mock_mongo_behavioral.session_metrics.find.return_value.sort.return_value = [
            {"duration_seconds": 600, "date": datetime.now(timezone.utc)},
        ]
        mock_mongo_behavioral.frustration_signals.count_documents.return_value = 2
        repo = self.make()
        result = _await(repo.update_engagement_score(1))
        assert "engagement_score" in result

    def test_update_engagement_score_db_none(self):
        repo = self.make()
        with patch.object(BehavioralRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.update_engagement_score(1))
            assert result == {"user_id": 1, "engagement_score": 0.5}

    def test_update_engagement_score_exception(self, mock_mongo_behavioral):
        mock_mongo_behavioral.behavioral_events.count_documents.side_effect = Exception("err")
        repo = self.make()
        result = _await(repo.update_engagement_score(1))
        assert result == {"engagement_score": 0.5}

    def test_get_student_behavioral_profile(self, mock_mongo_behavioral):
        mock_mongo_behavioral.behavioral_events.find.return_value.sort.return_value = []
        mock_mongo_behavioral.session_metrics.find.return_value.sort.return_value = []
        mock_mongo_behavioral.frustration_signals.find.return_value.sort.return_value = []
        mock_mongo_behavioral.code_analysis.find.return_value.sort.return_value = []
        mock_mongo_behavioral.engagement_scores.find_one.return_value = {"engagement_score": 0.7}
        mock_mongo_behavioral.exercise_attempts.find.return_value.sort.return_value = []
        repo = self.make()
        result = _await(repo.get_student_behavioral_profile(1))
        assert result["user_id"] == 1
        assert "engagement_score" in result

    def test_get_student_behavioral_profile_db_none(self):
        repo = self.make()
        with patch.object(BehavioralRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_student_behavioral_profile(1))
            assert result == {"user_id": 1, "engagement_score": 0.5}

    def test_get_student_behavioral_profile_exception(self, mock_mongo_behavioral):
        mock_mongo_behavioral.behavioral_events.find.side_effect = Exception("err")
        repo = self.make()
        result = _await(repo.get_student_behavioral_profile(1))
        assert result == {"user_id": 1, "engagement_score": 0.5}

    def test_count_exercise_attempts_30d(self, mock_mongo_behavioral):
        mock_mongo_behavioral.exercise_attempts.count_documents.return_value = 15
        repo = self.make()
        import types
        result = _await(repo._count_exercise_attempts_30d(1))
        assert result == 15

    def test_count_exercise_attempts_30d_db_none(self):
        repo = self.make()
        with patch.object(BehavioralRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo._count_exercise_attempts_30d(1))
            assert result == 0

    def test_count_exercise_attempts_30d_exception(self, mock_mongo_behavioral):
        mock_mongo_behavioral.exercise_attempts.count_documents.side_effect = Exception("err")
        repo = self.make()
        result = _await(repo._count_exercise_attempts_30d(1))
        assert result == 0


# ===================================================================
# MLPredictionsRepository
# ===================================================================

class TestMLPredictionsRepository:

    def make(self):
        return MLPredictionsRepository()

    def test_save_predictions(self, mock_mongo_ml):
        from domain.analytics.ml_predictions import MLPrediction
        pred = MLPrediction(student_id=1, week_number=5)
        repo = self.make()
        result = _await(repo.save_predictions(pred))
        assert result is True
        mock_mongo_ml.ml_predictions.update_one.assert_called_once()

    def test_save_predictions_db_none(self):
        from domain.analytics.ml_predictions import MLPrediction
        pred = MLPrediction(student_id=1, week_number=5)
        repo = self.make()
        with patch.object(MLPredictionsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.save_predictions(pred))
            assert result is False

    def test_save_predictions_exception(self, mock_mongo_ml):
        from domain.analytics.ml_predictions import MLPrediction
        mock_mongo_ml.ml_predictions.update_one.side_effect = Exception("err")
        pred = MLPrediction(student_id=1, week_number=5)
        repo = self.make()
        result = _await(repo.save_predictions(pred))
        assert result is False

    def test_get_latest_found(self, mock_mongo_ml):
        mock_mongo_ml.ml_predictions.find_one.return_value = {
            "student_id": 1, "week_number": 10,
        }
        repo = self.make()
        result = _await(repo.get_latest(1))
        assert result is not None
        assert result.student_id == 1

    def test_get_latest_not_found(self, mock_mongo_ml):
        mock_mongo_ml.ml_predictions.find_one.return_value = None
        repo = self.make()
        result = _await(repo.get_latest(1))
        assert result is None

    def test_get_latest_db_none(self):
        repo = self.make()
        with patch.object(MLPredictionsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_latest(1))
            assert result is None

    def test_get_history(self, mock_mongo_ml):
        mock_mongo_ml.ml_predictions.find.return_value.sort.return_value.limit.return_value = [
            {"student_id": 1, "week_number": 5},
            {"student_id": 1, "week_number": 4},
        ]
        repo = self.make()
        result = _await(repo.get_history(1))
        assert len(result) == 2

    def test_get_history_db_none(self):
        repo = self.make()
        with patch.object(MLPredictionsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_history(1))
            assert result == []

    def test_get_all_latest(self, mock_mongo_ml):
        mock_mongo_ml.ml_predictions.aggregate.return_value = [
            {"student_id": 1, "week_number": 10},
            {"student_id": 2, "week_number": 8},
        ]
        repo = self.make()
        result = _await(repo.get_all_latest())
        assert len(result) == 2

    def test_get_all_latest_db_none(self):
        repo = self.make()
        with patch.object(MLPredictionsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_all_latest())
            assert result == []


# ===================================================================
# StudentMetricsRepository
# ===================================================================

class TestStudentMetricsRepository:

    def make(self):
        return StudentMetricsRepository()

    def test_upsert_metrics(self, mock_mongo_metrics):
        repo = self.make()
        result = _await(repo.upsert_metrics(1, {"session_days": 5}))
        assert result is True
        mock_mongo_metrics.student_metrics.update_one.assert_called_once()

    def test_upsert_metrics_db_none(self):
        repo = self.make()
        with patch.object(StudentMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.upsert_metrics(1, {"session_days": 5}))
            assert result is False

    def test_upsert_metrics_exception(self, mock_mongo_metrics):
        mock_mongo_metrics.student_metrics.update_one.side_effect = Exception("err")
        repo = self.make()
        result = _await(repo.upsert_metrics(1, {"session_days": 5}))
        assert result is False

    def test_increment_metrics(self, mock_mongo_metrics):
        repo = self.make()
        result = _await(repo.increment_metrics(1, {"exercise_attempts": 1}))
        assert result is True

    def test_increment_metrics_db_none(self):
        repo = self.make()
        with patch.object(StudentMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.increment_metrics(1, {"exercise_attempts": 1}))
            assert result is False

    def test_set_fields(self, mock_mongo_metrics):
        repo = self.make()
        result = _await(repo.set_fields(1, {"full_name": "Test"}))
        assert result is True

    def test_set_fields_db_none(self):
        repo = self.make()
        with patch.object(StudentMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.set_fields(1, {"full_name": "Test"}))
            assert result is False

    def test_get_metrics_found(self, mock_mongo_metrics):
        mock_mongo_metrics.student_metrics.find_one.return_value = {
            "student_id": 1, "session_days": 5,
        }
        repo = self.make()
        result = _await(repo.get_metrics(1))
        assert result is not None
        assert result.student_id == 1

    def test_get_metrics_not_found(self, mock_mongo_metrics):
        mock_mongo_metrics.student_metrics.find_one.return_value = None
        repo = self.make()
        result = _await(repo.get_metrics(1))
        assert result is None

    def test_get_metrics_db_none(self):
        repo = self.make()
        with patch.object(StudentMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_metrics(1))
            assert result is None

    def test_get_all_metrics(self, mock_mongo_metrics):
        mock_mongo_metrics.student_metrics.find.return_value = [
            {"student_id": 1}, {"student_id": 2},
        ]
        repo = self.make()
        result = _await(repo.get_all_metrics())
        assert len(result) == 2

    def test_get_all_metrics_db_none(self):
        repo = self.make()
        with patch.object(StudentMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_all_metrics())
            assert result == []

    def test_get_metrics_batch(self, mock_mongo_metrics):
        mock_mongo_metrics.student_metrics.find.return_value = [
            {"student_id": 1}, {"student_id": 2},
        ]
        repo = self.make()
        result = _await(repo.get_metrics_batch([1, 2]))
        assert len(result) == 2

    def test_get_metrics_batch_db_none(self):
        repo = self.make()
        with patch.object(StudentMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_metrics_batch([1, 2]))
            assert result == []


# ===================================================================
# WeeklyMetricsRepository
# ===================================================================

class TestWeeklyMetricsRepository:

    def make(self):
        return WeeklyMetricsRepository()

    def test_save_snapshot(self, mock_mongo_weekly):
        from domain.analytics.weekly_metrics import WeeklyStudentMetrics
        m = WeeklyStudentMetrics(student_id=1, week_number=5, year=2025)
        repo = self.make()
        result = _await(repo.save_snapshot(m))
        assert result is True
        mock_mongo_weekly.weekly_student_metrics.update_one.assert_called_once()

    def test_save_snapshot_db_none(self):
        from domain.analytics.weekly_metrics import WeeklyStudentMetrics
        m = WeeklyStudentMetrics(student_id=1, week_number=5, year=2025)
        repo = self.make()
        with patch.object(WeeklyMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.save_snapshot(m))
            assert result is False

    def test_save_snapshot_exception(self, mock_mongo_weekly):
        from domain.analytics.weekly_metrics import WeeklyStudentMetrics
        mock_mongo_weekly.weekly_student_metrics.update_one.side_effect = Exception("err")
        m = WeeklyStudentMetrics(student_id=1, week_number=5, year=2025)
        repo = self.make()
        result = _await(repo.save_snapshot(m))
        assert result is False

    def test_get_student_history(self, mock_mongo_weekly):
        mock_mongo_weekly.weekly_student_metrics.find.return_value.sort.return_value.sort.return_value.limit.return_value = [
            {"student_id": 1, "week_number": 5, "year": 2025},
        ]
        repo = self.make()
        result = _await(repo.get_student_history(1))
        assert len(result) == 1

    def test_get_student_history_db_none(self):
        repo = self.make()
        with patch.object(WeeklyMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_student_history(1))
            assert result == []

    def test_get_class_trends(self, mock_mongo_weekly):
        mock_mongo_weekly.weekly_student_metrics.find.return_value.sort.return_value.sort.return_value.limit.return_value = [
            {"student_id": 1, "week_number": 5, "year": 2025},
        ]
        repo = self.make()
        result = _await(repo.get_class_trends([1], 4))
        assert len(result) == 1

    def test_get_class_trends_db_none(self):
        repo = self.make()
        with patch.object(WeeklyMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_class_trends([1], 4))
            assert result == []

    def test_get_latest_snapshot_found(self, mock_mongo_weekly):
        mock_mongo_weekly.weekly_student_metrics.find_one.return_value = {
            "student_id": 1, "week_number": 10, "year": 2025,
        }
        repo = self.make()
        result = _await(repo.get_latest_snapshot(1))
        assert result is not None
        assert result.student_id == 1

    def test_get_latest_snapshot_not_found(self, mock_mongo_weekly):
        mock_mongo_weekly.weekly_student_metrics.find_one.return_value = None
        repo = self.make()
        result = _await(repo.get_latest_snapshot(1))
        assert result is None

    def test_get_latest_snapshot_db_none(self):
        repo = self.make()
        with patch.object(WeeklyMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_latest_snapshot(1))
            assert result is None

    def test_get_all_latest_snapshots(self, mock_mongo_weekly):
        mock_mongo_weekly.weekly_student_metrics.aggregate.return_value = [
            {"student_id": 1, "week_number": 10, "year": 2025},
        ]
        repo = self.make()
        result = _await(repo.get_all_latest_snapshots())
        assert len(result) == 1

    def test_get_all_latest_snapshots_db_none(self):
        repo = self.make()
        with patch.object(WeeklyMetricsRepository, 'get_db', new_callable=AsyncMock, return_value=None):
            result = _await(repo.get_all_latest_snapshots())
            assert result == []


# ===================================================================
# Infrastructure tests (_try_connect / get_db / close / _exec)
# ===================================================================

class _MongoInfraMixin:
    """Mixin: test helpers for _try_connect / get_db / close / _exec."""

    repo_cls = None   # set by subclass
    _mod_path = ""    # e.g. "event_repository_impl"

    def test_try_connect_success(self):
        mock_client = MagicMock()
        self.repo_cls._available = None
        patch_path = f"infrastructure.adapters.output.mongo.{self._mod_path}.MongoClient"
        with patch(patch_path, return_value=mock_client):
            result = _await(self.repo_cls._try_connect())
        assert result is True
        assert self.repo_cls._available is True

    def test_try_connect_cached(self):
        self.repo_cls._available = True
        result = _await(self.repo_cls._try_connect())
        assert result is True

    def test_try_connect_cached_false(self):
        self.repo_cls._available = False
        result = _await(self.repo_cls._try_connect())
        assert result is False

    def test_try_connect_failure(self):
        self.repo_cls._available = None
        patch_path = f"infrastructure.adapters.output.mongo.{self._mod_path}.MongoClient"
        with patch(patch_path, side_effect=Exception("conn refused")):
            result = _await(self.repo_cls._try_connect())
        assert result is False
        assert self.repo_cls._available is False

    def test_get_db_available_false(self):
        self.repo_cls._available = False
        result = _await(self.repo_cls.get_db())
        assert result is None

    def test_get_db_from_cache(self):
        mock_db = MagicMock()
        self.repo_cls._db = mock_db
        result = _await(self.repo_cls.get_db())
        assert result is mock_db

    def test_get_db_triggers_try_connect_when_none(self):
        self.repo_cls._db = None
        self.repo_cls._available = None
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        patch_path = f"infrastructure.adapters.output.mongo.{self._mod_path}.MongoClient"
        with patch(patch_path, return_value=mock_client):
            result = _await(self.repo_cls.get_db())
        assert result is mock_db

    def test_get_db_triggers_try_connect_and_fails(self):
        self.repo_cls._db = None
        self.repo_cls._available = None
        patch_path = f"infrastructure.adapters.output.mongo.{self._mod_path}.MongoClient"
        with patch(patch_path, side_effect=Exception("fail")):
            result = _await(self.repo_cls.get_db())
        assert result is None

    def test_close_resets_state(self):
        mock_cl = MagicMock()
        self.repo_cls._client = mock_cl
        self.repo_cls._db = MagicMock()
        self.repo_cls._available = True
        self.repo_cls.close()
        assert self.repo_cls._client is None
        assert self.repo_cls._db is None
        assert self.repo_cls._available is None
        mock_cl.close.assert_called_once()

    def test_close_noop_when_no_client(self):
        self.repo_cls._client = None
        self.repo_cls.close()

    def test_exec_returns_none_when_no_db(self):
        repo = self.repo_cls()
        with patch.object(self.repo_cls, 'get_db', new_callable=AsyncMock, return_value=None):
            if hasattr(repo, '_exec'):
                result = _await(repo._exec(lambda: "ok"))
            else:
                result = _await(repo._run(lambda db: "ok"))
        assert result is None

    def test_exec_runs_fn(self):
        repo = self.repo_cls()
        mock_db = MagicMock()
        with patch.object(self.repo_cls, 'get_db', new_callable=AsyncMock, return_value=mock_db):
            if hasattr(repo, '_exec'):
                result = _await(repo._exec(lambda: "done"))
            else:
                result = _await(repo._run(lambda db: "done"))
        assert result == "done"

    def test_exec_exception_returns_none(self):
        repo = self.repo_cls()
        mock_db = MagicMock()
        with patch.object(self.repo_cls, 'get_db', new_callable=AsyncMock, return_value=mock_db):
            if hasattr(repo, '_exec'):
                result = _await(repo._exec(lambda: (_ for _ in ()).throw(Exception("err"))))
            else:
                result = _await(repo._run(lambda db: (_ for _ in ()).throw(Exception("err"))))
        assert result is None


class TestEventRepoInfrastructure(_MongoInfraMixin):
    repo_cls = EventRepository
    _mod_path = "event_repository_impl"

class TestBehavioralRepoInfrastructure(_MongoInfraMixin):
    repo_cls = BehavioralRepository
    _mod_path = "behavioral_repository"

class TestMLPredictionsRepoInfrastructure(_MongoInfraMixin):
    repo_cls = MLPredictionsRepository
    _mod_path = "ml_predictions_repository"

class TestStudentMetricsRepoInfrastructure(_MongoInfraMixin):
    repo_cls = StudentMetricsRepository
    _mod_path = "student_metrics_repository"

class TestWeeklyMetricsRepoInfrastructure(_MongoInfraMixin):
    repo_cls = WeeklyMetricsRepository
    _mod_path = "weekly_metrics_repository"


# ===================================================================
# Graceful degradation tests (MongoDB unavailable)
# ===================================================================

class TestGracefulDegradation:

    def test_event_repo_all_methods_return_safe_defaults(self):
        repo = EventRepository()
        with patch.object(EventRepository, '_try_connect', new_callable=AsyncMock, return_value=False):
            assert _await(repo.log_event("x", 1, {})) is None
            assert _await(repo.log_exercise_attempt(1, 1, True, 1.0)) is None
            assert _await(repo.get_user_events(1)) is None
            assert _await(repo.get_user_exercise_history(1)) is None
            assert _await(repo.save_progress_snapshot(1, {})) is None
            assert _await(repo.log_chat_interaction(1, "m", "r", "s")) is None

    def test_behavioral_repo_returns_safe_defaults(self):
        repo = BehavioralRepository()
        with patch.object(BehavioralRepository, '_try_connect', new_callable=AsyncMock, return_value=False):
            assert _await(repo.log_session_start(1, "s")) is None
            assert _await(repo.log_session_activity(1, "s")) is None
            assert _await(repo.log_session_end(1, "s")) == 0
            assert _await(repo.log_exercise_action(1, 1, 1, "run")) is None
            assert _await(repo.log_frustration_signal(1, 1, "timeout")) is None
            assert _await(repo.log_code_analysis(1, 1, "c", "e", "t")) is None
            eng = _await(repo.update_engagement_score(1))
            assert eng == {"user_id": 1, "engagement_score": 0.5}
            prof = _await(repo.get_student_behavioral_profile(1))
            assert prof == {"user_id": 1, "engagement_score": 0.5}

    def test_ml_predictions_repo_returns_safe_defaults(self):
        from domain.analytics.ml_predictions import MLPrediction
        repo = MLPredictionsRepository()
        with patch.object(MLPredictionsRepository, '_try_connect', new_callable=AsyncMock, return_value=False):
            assert _await(repo.save_predictions(MLPrediction(1, 5))) is False
            assert _await(repo.get_latest(1)) is None
            assert _await(repo.get_history(1)) == []
            assert _await(repo.get_all_latest()) == []

    def test_student_metrics_repo_returns_safe_defaults(self):
        repo = StudentMetricsRepository()
        with patch.object(StudentMetricsRepository, '_try_connect', new_callable=AsyncMock, return_value=False):
            assert _await(repo.upsert_metrics(1, {})) is False
            assert _await(repo.increment_metrics(1, {})) is False
            assert _await(repo.set_fields(1, {})) is False
            assert _await(repo.get_metrics(1)) is None
            assert _await(repo.get_all_metrics()) == []
            assert _await(repo.get_metrics_batch([1])) == []

    def test_weekly_metrics_repo_returns_safe_defaults(self):
        from domain.analytics.weekly_metrics import WeeklyStudentMetrics
        repo = WeeklyMetricsRepository()
        with patch.object(WeeklyMetricsRepository, '_try_connect', new_callable=AsyncMock, return_value=False):
            assert _await(repo.save_snapshot(WeeklyStudentMetrics(1, 1, 2025))) is False
            assert _await(repo.get_student_history(1)) == []
            assert _await(repo.get_class_trends([1])) == []
            assert _await(repo.get_latest_snapshot(1)) is None
            assert _await(repo.get_all_latest_snapshots()) == []
