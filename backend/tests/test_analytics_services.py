"""Tests for analytics services: MetricsService, AnalyticsScheduler, analytics_router."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock


def _await(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# MetricsService
# ---------------------------------------------------------------------------

class TestMetricsService:
    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock()
        repo.increment_metrics = AsyncMock(return_value=True)
        repo.set_fields = AsyncMock(return_value=True)
        repo.get_metrics = AsyncMock(return_value=None)
        repo.get_all_metrics = AsyncMock(return_value=[])
        return repo

    def make(self, repo):
        from application.services.analytics.metrics_service import MetricsService
        svc = MetricsService()
        svc._repo = repo
        return svc

    def test_track_session_start(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "session_start"))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"session_days": 1, "total_sessions": 1})

    def test_track_session_activity(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "session_activity"))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"total_sessions": 1})

    def test_track_exercise_view(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "exercise_view"))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"exercise_attempts": 1})

    def test_track_exercise_submit_passed(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "exercise_submit", {"passed": True}))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"exercise_attempts": 1, "passed_exercises": 1})

    def test_track_exercise_submit_failed(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "exercise_submit", {"passed": False}))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"exercise_attempts": 1})

    def test_track_exercise_attempt_with_error_rate(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "exercise_attempt", {"error_rate": 0.3}))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"exercise_attempts": 1})
        mock_repo.set_fields.assert_called_once_with(1, {"error_rate": 0.3})

    def test_track_exercise_attempt_no_error_rate(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "exercise_attempt", {}))
        assert result is True
        mock_repo.set_fields.assert_not_called()

    def test_track_forum_post(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "forum_post"))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"forum_interactions": 1})

    def test_track_forum_view(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "forum_view"))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"forum_interactions": 1})

    def test_track_content_view(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "content_view"))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"content_views": 1})

    def test_track_session_end_with_duration(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "session_end", {"duration_minutes": 45}))
        assert result is True
        mock_repo.increment_metrics.assert_called_once_with(1, {"total_time_minutes": 45})

    def test_track_session_end_zero_duration(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "session_end", {"duration_minutes": 0}))
        assert result is True
        mock_repo.increment_metrics.assert_not_called()

    def test_track_code_error(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "code_error", {"error_rate": 0.8}))
        assert result is True
        mock_repo.set_fields.assert_called_once_with(1, {"error_rate": 0.8})

    def test_track_code_error_default_rate(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "code_error", {}))
        assert result is True
        mock_repo.set_fields.assert_called_once_with(1, {"error_rate": 0.5})

    def test_track_unknown_event(self, mock_repo):
        svc = self.make(mock_repo)
        result = _await(svc.track_event(1, "unknown_event"))
        assert result is True
        mock_repo.increment_metrics.assert_not_called()
        mock_repo.set_fields.assert_not_called()

    def test_get_student_metrics_found(self, mock_repo):
        from domain.analytics.student_metrics import StudentMetrics
        fake = StudentMetrics(student_id=1, session_days=3)
        mock_repo.get_metrics = AsyncMock(return_value=fake)
        svc = self.make(mock_repo)
        result = _await(svc.get_student_metrics(1))
        assert result["student_id"] == 1
        assert result["session_days"] == 3

    def test_get_student_metrics_not_found(self, mock_repo):
        mock_repo.get_metrics = AsyncMock(return_value=None)
        svc = self.make(mock_repo)
        result = _await(svc.get_student_metrics(1))
        assert result is None

    def test_get_all_students_metrics(self, mock_repo):
        from domain.analytics.student_metrics import StudentMetrics
        fake1 = StudentMetrics(student_id=1, session_days=2)
        fake2 = StudentMetrics(student_id=2, session_days=5)
        mock_repo.get_all_metrics = AsyncMock(return_value=[fake1, fake2])
        svc = self.make(mock_repo)
        result = _await(svc.get_all_students_metrics())
        assert len(result) == 2
        assert result[0]["student_id"] == 1
        assert result[0]["session_days"] == 2
        assert result[1]["student_id"] == 2
        assert result[1]["session_days"] == 5

    def test_get_all_students_metrics_empty(self, mock_repo):
        mock_repo.get_all_metrics = AsyncMock(return_value=[])
        svc = self.make(mock_repo)
        result = _await(svc.get_all_students_metrics())
        assert result == []


# ---------------------------------------------------------------------------
# AnalyticsScheduler
# ---------------------------------------------------------------------------

class TestAnalyticsScheduler:
    @pytest.fixture
    def mock_repos(self):
        class FakeRepos:
            student = AsyncMock()
            weekly = AsyncMock()
            ml = AsyncMock()
        r = FakeRepos()
        r.student.get_all_metrics = AsyncMock(return_value=[])
        r.weekly.save_snapshot = AsyncMock(return_value=True)
        r.ml.save_predictions = AsyncMock(return_value=True)
        return r

    @pytest.fixture
    def mock_orchestrator(self):
        o = MagicMock()
        o.predict_student.return_value = {
            "predictions": {
                "engagement_projected": {"value": 0.7},
                "performance_projected": {"value": 0.6},
                "dropout_risk": {"probability": 0.2},
                "frustration_projected": {"class": 1},
            },
            "cluster": {"cluster_id": 2, "cluster_name": "Avanzado"},
            "anomaly": {"anomaly_score": 0.1, "is_anomaly": False},
        }
        o.get_feature_importances.return_value = {"engagement": []}
        return o

    def make(self, mock_repos, orchestrator=None):
        from application.services.analytics.scheduler_service import AnalyticsScheduler
        svc = AnalyticsScheduler(orchestrator=orchestrator)
        svc._student_metrics_repo = mock_repos.student
        svc._weekly_repo = mock_repos.weekly
        svc._ml_repo = mock_repos.ml
        return svc

    def test_start_adds_jobs(self, mock_repos):
        from application.services.analytics.scheduler_service import AnalyticsScheduler
        svc = AnalyticsScheduler()
        svc._student_metrics_repo = mock_repos.student
        svc._weekly_repo = mock_repos.weekly
        svc._ml_repo = mock_repos.ml
        svc._scheduler = MagicMock()
        svc._scheduler.running = False
        svc.start()
        assert svc._scheduler.add_job.call_count == 2
        svc._scheduler.start.assert_called_once()

    def test_start_skips_if_running(self, mock_repos):
        svc = self.make(mock_repos)
        svc._scheduler = MagicMock()
        svc._scheduler.running = True
        svc.start()
        svc._scheduler.add_job.assert_not_called()
        svc._scheduler.start.assert_not_called()

    def test_stop_shuts_down(self, mock_repos):
        svc = self.make(mock_repos)
        svc._scheduler = MagicMock()
        svc._scheduler.running = True
        svc.stop()
        svc._scheduler.shutdown.assert_called_once_with(wait=False)

    def test_stop_skips_if_not_running(self, mock_repos):
        svc = self.make(mock_repos)
        svc._scheduler = MagicMock()
        svc._scheduler.running = False
        svc.stop()
        svc._scheduler.shutdown.assert_not_called()

    def test_generate_weekly_snapshot_no_metrics(self, mock_repos):
        mock_repos.student.get_all_metrics = AsyncMock(return_value=[])
        svc = self.make(mock_repos)
        _await(svc._generate_weekly_snapshot())
        mock_repos.weekly.save_snapshot.assert_not_called()

    def test_generate_weekly_snapshot_with_metrics(self, mock_repos, mock_orchestrator):
        from domain.analytics.student_metrics import StudentMetrics
        sm = StudentMetrics(student_id=1, session_days=5, total_sessions=10, total_time_minutes=300.0,
                            exercise_attempts=20, passed_exercises=15, error_rate=0.2,
                            forum_interactions=3, content_views=8)
        mock_repos.student.get_all_metrics = AsyncMock(return_value=[sm])
        svc = self.make(mock_repos, orchestrator=mock_orchestrator)
        _await(svc._generate_weekly_snapshot())
        mock_repos.weekly.save_snapshot.assert_called_once()
        saved = mock_repos.weekly.save_snapshot.call_args[0][0]
        assert saved.student_id == 1
        assert saved.avg_session_days == 5.0
        mock_repos.ml.save_predictions.assert_called_once()

    def test_generate_weekly_snapshot_orchestrator_error(self, mock_repos, mock_orchestrator):
        from domain.analytics.student_metrics import StudentMetrics
        sm = StudentMetrics(student_id=1)
        mock_repos.student.get_all_metrics = AsyncMock(return_value=[sm])
        mock_orchestrator.predict_student.side_effect = Exception("ML fail")
        svc = self.make(mock_repos, orchestrator=mock_orchestrator)
        _await(svc._generate_weekly_snapshot())
        mock_repos.weekly.save_snapshot.assert_called_once()
        mock_repos.ml.save_predictions.assert_not_called()

    def test_generate_weekly_snapshot_no_orchestrator(self, mock_repos):
        from domain.analytics.student_metrics import StudentMetrics
        sm = StudentMetrics(student_id=1)
        mock_repos.student.get_all_metrics = AsyncMock(return_value=[sm])
        svc = self.make(mock_repos, orchestrator=None)
        _await(svc._generate_weekly_snapshot())
        mock_repos.weekly.save_snapshot.assert_called_once()
        mock_repos.ml.save_predictions.assert_not_called()

    def test_generate_daily_snapshot(self, mock_repos):
        from domain.analytics.student_metrics import StudentMetrics
        mock_repos.student.get_all_metrics = AsyncMock(return_value=[StudentMetrics(student_id=1)])
        svc = self.make(mock_repos)
        _await(svc._generate_daily_snapshot())

    def test_generate_daily_snapshot_empty(self, mock_repos):
        mock_repos.student.get_all_metrics = AsyncMock(return_value=[])
        svc = self.make(mock_repos)
        _await(svc._generate_daily_snapshot())

    def test_trigger_weekly_now(self, mock_repos, mock_orchestrator):
        from domain.analytics.student_metrics import StudentMetrics
        mock_repos.student.get_all_metrics = AsyncMock(return_value=[StudentMetrics(student_id=1)])
        svc = self.make(mock_repos, orchestrator=mock_orchestrator)
        _await(svc.trigger_weekly_now())
        mock_repos.weekly.save_snapshot.assert_called_once()


# ---------------------------------------------------------------------------
# AnalyticsRouter
# ---------------------------------------------------------------------------

class TestAnalyticsRouter:
    @pytest.fixture
    def mock_metrics(self):
        m = MagicMock()
        m.get_student_metrics = AsyncMock(return_value={"session_days": 5})
        return m

    @pytest.fixture
    def mock_weekly(self):
        w = MagicMock()
        w.get_student_history = AsyncMock(return_value=[])
        w.get_class_trends = AsyncMock(return_value=[])
        return w

    @pytest.fixture
    def mock_ml(self):
        m = MagicMock()
        m.get_history = AsyncMock(return_value=[])
        return m

    @pytest.fixture
    def mock_orch(self):
        o = MagicMock()
        o.predict_student.return_value = {
            "predictions": {"dropout_risk": {"probability": 0.3, "label": "bajo"},
                            "frustration_projected": {"class": 0, "label": "baja"},
                            "engagement_projected": {"value": 0.7, "label": "medio"},
                            "performance_projected": {"value": 0.6}},
            "cluster": {"cluster_id": 1, "cluster_name": "Regular"},
            "anomaly": {"anomaly_score": 0.0, "is_anomaly": False},
            "recommendations": [],
            "has_historical_data": False,
        }
        o.predict_class.return_value = {
            "students": [],
            "averages": {"engagement": 0.6, "performance": 0.5},
            "at_risk": {"count": 0, "students": []},
            "high_frustration": {"count": 0, "students": []},
            "cluster_distribution": [],
            "insights": [],
        }
        o.get_clustering_pca.return_value = {"x": [1], "y": [2]}
        return o

    @pytest.fixture
    def patch_router(self, mock_metrics, mock_weekly, mock_ml, mock_orch):
        patches = [
            patch("application.services.analytics.analytics_router._metrics_service", mock_metrics),
            patch("application.services.analytics.analytics_router._weekly_repo", mock_weekly),
            patch("application.services.analytics.analytics_router._ml_repo", mock_ml),
            patch("application.services.analytics.analytics_router.get_orchestrator", return_value=mock_orch),
        ]
        for p in patches:
            p.start()
        yield
        for p in patches:
            p.stop()

    @pytest.fixture
    def patch_postgres(self):
        fake_cursor = MagicMock()
        fake_cursor.__enter__ = MagicMock(return_value=fake_cursor)
        fake_cursor.__exit__ = MagicMock(return_value=None)
        fake_cursor.fetchall.return_value = [(1,), (2,)]
        conn = MagicMock()
        conn.get_cursor.return_value = fake_cursor
        patch_path = "infrastructure.adapters.output.postgres.connection.PostgresConnection"
        with patch(patch_path, conn):
            yield fake_cursor

    # /api/analytics/student/{student_id}
    def test_get_student_analytics(self, patch_router):
        from application.services.analytics.analytics_router import analytics_router
        student_id = 42
        result = _await(analytics_router.routes[0].endpoint(student_id=42, token_data=None))
        assert result["success"] is True
        assert result["student_id"] == 42
        assert result["metrics"] == {"session_days": 5}

    # /api/analytics/class/{class_id}
    def test_get_class_analytics(self, patch_router, patch_postgres):
        from application.services.analytics.analytics_router import analytics_router
        result = _await(analytics_router.routes[1].endpoint(class_id=10, token_data=None))
        assert result["success"] is True
        assert result["class_id"] == 10
        assert result["total_students"] == 2

    def test_get_class_analytics_no_students(self, patch_router):
        fake_cursor = MagicMock()
        fake_cursor.__enter__ = MagicMock(return_value=fake_cursor)
        fake_cursor.__exit__ = MagicMock(return_value=None)
        fake_cursor.fetchall.return_value = []
        conn = MagicMock()
        conn.get_cursor.return_value = fake_cursor
        with patch("infrastructure.adapters.output.postgres.connection.PostgresConnection", conn):
            from application.services.analytics.analytics_router import analytics_router
            result = _await(analytics_router.routes[1].endpoint(class_id=99, token_data=None))
        assert result["total_students"] == 0

    # /api/analytics/risk-students
    def test_get_risk_students(self, patch_router, patch_postgres):
        from application.services.analytics.analytics_router import analytics_router
        result = _await(analytics_router.routes[2].endpoint(min_dropout_risk=0.5, token_data=None))
        assert result["success"] is True
        assert "risk_students" in result

    def test_get_risk_students_no_rows(self, patch_router):
        fake_cursor = MagicMock()
        fake_cursor.__enter__ = MagicMock(return_value=fake_cursor)
        fake_cursor.__exit__ = MagicMock(return_value=None)
        fake_cursor.fetchall.return_value = []
        conn = MagicMock()
        conn.get_cursor.return_value = fake_cursor
        with patch("infrastructure.adapters.output.postgres.connection.PostgresConnection", conn):
            from application.services.analytics.analytics_router import analytics_router
            result = _await(analytics_router.routes[2].endpoint(min_dropout_risk=0.5, token_data=None))
        assert result["total_count"] == 0

    # /api/analytics/clusters
    def test_get_clusters(self, patch_router):
        from application.services.analytics.analytics_router import analytics_router
        result = _await(analytics_router.routes[3].endpoint(token_data=None))
        assert result["success"] is True
        assert result["cluster_info"]["n_clusters"] == 4

    # /api/analytics/anomalies
    def test_get_anomalies(self, patch_router, patch_postgres):
        from application.services.analytics.analytics_router import analytics_router
        result = _await(analytics_router.routes[4].endpoint(min_score=0.0, token_data=None))
        assert result["success"] is True
        assert "anomalies" in result

    def test_get_anomalies_no_rows(self, patch_router):
        fake_cursor = MagicMock()
        fake_cursor.__enter__ = MagicMock(return_value=fake_cursor)
        fake_cursor.__exit__ = MagicMock(return_value=None)
        fake_cursor.fetchall.return_value = []
        conn = MagicMock()
        conn.get_cursor.return_value = fake_cursor
        with patch("infrastructure.adapters.output.postgres.connection.PostgresConnection", conn):
            from application.services.analytics.analytics_router import analytics_router
            result = _await(analytics_router.routes[4].endpoint(min_score=0.0, token_data=None))
        assert result["total_count"] == 0
