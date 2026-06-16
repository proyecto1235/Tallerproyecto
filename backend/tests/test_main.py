"""Tests for main.py API routes using FastAPI TestClient.

Covers ~30 representative routes across all tag groups.
Services are mocked at module level to avoid real DB/ML dependencies.
"""

import os

# Skip ProactorEventLoopPolicy in tests (Python 3.14 uses it by default)
os.environ.setdefault("_SKIP_PROACTOR", "1")

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt

# ── Env is set by conftest.py (SECRET_KEY=test-secret-key, etc.) ──

# ── Mock PostgresConnection class methods before routes are called ──
from infrastructure.adapters.output.postgres.connection import PostgresConnection

# Shared DB cursor — default fetchone returns a tuple so row[0] never crashes
db_cursor = MagicMock()
db_cursor.fetchone.return_value = (0,) * 20
db_cursor.fetchall.return_value = []
db_cursor.execute.return_value = None
db_cursor.description = None


@contextmanager
def mock_get_cursor():
    yield db_cursor


_pg_cursor_patcher = patch.object(PostgresConnection, 'get_cursor', mock_get_cursor)
_pg_init_patcher = patch.object(PostgresConnection, 'init_pool')
_pg_close_patcher = patch.object(PostgresConnection, 'close_pool')
_pg_cursor_patcher.start()
_pg_init_patcher.start()
_pg_close_patcher.start()


@pytest.fixture(autouse=True, scope="module")
def _stop_pg_patches():
    yield
    _pg_cursor_patcher.stop()
    _pg_init_patcher.stop()
    _pg_close_patcher.stop()


# ── Now import main (singletons created but not connected) ──
from app.main import app
from config.settings import settings

# ── Mock ai_cache to avoid real Redis connections ──
_ai_cache_get_patcher = patch("app.main.ai_cache.get", AsyncMock(return_value=None))
_ai_cache_set_patcher = patch("app.main.ai_cache.set", AsyncMock(return_value=None))
_ai_cache_get_patcher.start()
_ai_cache_set_patcher.start()
from domain.entities.user import User, UserRole

# Disable lifespan so DB init / pool / scheduler are never started
app.router.lifespan_context = None

# ── Mock EventRepository class methods ──
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository

_evt_log_event = patch.object(EventRepository, 'log_event', AsyncMock(return_value="evt_123"))
_evt_chat = patch.object(EventRepository, 'log_chat_interaction', AsyncMock(return_value=None))
_evt_get_db = patch.object(EventRepository, 'get_db', AsyncMock(return_value=MagicMock()))
_evt_close = patch.object(EventRepository, 'close', MagicMock())
_evt_user_events = patch.object(EventRepository, 'get_user_events', AsyncMock(return_value=[]))
_evt_log_event.start()
_evt_chat.start()
_evt_get_db.start()
_evt_close.start()
_evt_user_events.start()


@pytest.fixture(autouse=True, scope="module")
def _stop_evt_patches():
    yield
    for _p in [_evt_log_event, _evt_chat, _evt_get_db, _evt_close, _evt_user_events]:
        _p.stop()

# ── Mock module-level singletons in app.main ──
import app.main as main_module

# Repositories
main_module.user_repository = MagicMock()
main_module.user_repository.get_by_id = AsyncMock()
main_module.user_repository.get_by_email = AsyncMock()
main_module.user_repository.create = AsyncMock()
main_module.user_repository.get_by_public_id = AsyncMock()
main_module.user_repository.get_all = AsyncMock(return_value=[])

main_module.module_repository = MagicMock()
main_module.module_repository.get_by_id = AsyncMock()
main_module.module_repository.get_all = AsyncMock(return_value=[])
main_module.module_repository.create = AsyncMock()
main_module.module_repository.update = AsyncMock()
main_module.module_repository.delete = AsyncMock()

main_module.enrollment_repository = MagicMock()
main_module.enrollment_repository.get_by_student = AsyncMock(return_value=[])
main_module.enrollment_repository.create = AsyncMock()

main_module.teacher_repository = MagicMock()
main_module.teacher_repository.get_teacher_metrics = AsyncMock(
    return_value={"success": True, "metrics": {}}
)
main_module.teacher_repository.get_teacher_students = AsyncMock(return_value=[])
main_module.teacher_repository.get_student_details = AsyncMock(
    return_value={"success": True, "student": {}}
)

main_module.event_repository = MagicMock()
main_module.event_repository.log_event = AsyncMock(return_value="evt_123")
main_module.event_repository.log_chat_interaction = AsyncMock(return_value=None)
main_module.event_repository.get_user_events = AsyncMock(return_value=[])
main_module.event_repository.get_db = AsyncMock(return_value=MagicMock())
main_module.event_repository.get_user_exercise_history = AsyncMock(
    return_value=[]
)

# AI / ML services
main_module.ai_service = MagicMock()
main_module.ai_service.detect_learning_path = AsyncMock(return_value={})
main_module.ai_service.predict_student_performance = AsyncMock(
    return_value=0.75
)
main_module.ai_service.chat_with_dialogflow = AsyncMock(
    return_value="Hello from Dialogflow"
)
main_module.ai_service.is_fallback_response = MagicMock(return_value=False)
main_module.ai_service.get_recommendations = AsyncMock(return_value=[])

main_module.ml_orchestrator = MagicMock()
main_module.ml_orchestrator.predict_student = MagicMock(return_value={})
main_module.ml_orchestrator.predict_class = MagicMock(return_value={})
main_module.ml_orchestrator.reload_models = MagicMock(
    return_value={
        "engagement": True,
        "performance": True,
        "dropout": True,
        "frustration": True,
        "clustering": True,
        "anomaly": True,
    }
)
main_module.ml_orchestrator._df = None
main_module.ml_orchestrator.anomaly = MagicMock()
main_module.ml_orchestrator.anomaly.predict = MagicMock(
    return_value={"is_anomaly": False, "anomaly_score": 0.1, "risk": "low"}
)
main_module.ml_orchestrator.clustering = MagicMock()
main_module.ml_orchestrator.clustering.get_summary = MagicMock(return_value=[])
main_module.ml_orchestrator.clustering.batch_predict = MagicMock(
    return_value=[]
)
main_module.ml_orchestrator.clustering.get_pca_projection = MagicMock(
    return_value={"pca1": [], "pca2": [], "labels": []}
)
main_module.ml_orchestrator.clustering._is_trained = True
main_module.ml_orchestrator.clustering._model = MagicMock()
main_module.ml_orchestrator.clustering._model.inertia_ = 0

main_module.intelligent_tutor = MagicMock()
main_module.intelligent_tutor.generate_response = AsyncMock(
    return_value={
        "response": "Mock tutor response",
        "source": "tutor",
        "intent": "help",
        "student_level": "beginner",
    }
)
main_module.intelligent_tutor.generate_hint = AsyncMock(
    return_value="Try using a loop here"
)
main_module.intelligent_tutor.detect_intent = MagicMock(
    return_value={"concept": "variables"}
)
main_module.intelligent_tutor.get_student_level = AsyncMock(
    return_value="beginner"
)
main_module.intelligent_tutor._detect_concept = MagicMock(
    return_value="variables"
)
main_module.intelligent_tutor._get_adapted_explanation = MagicMock(
    return_value="Mock explanation"
)

main_module.behavioral_repo = MagicMock()
main_module.behavioral_repo.get_student_behavioral_profile = AsyncMock(
    return_value={
        "user_id": 1,
        "performance_score": 0.75,
        "engagement_score": 0.6,
    }
)
main_module.behavioral_repo.log_exercise_action = AsyncMock(return_value=None)
main_module.behavioral_repo.get_db = AsyncMock(return_value=MagicMock())

main_module.difficulty_adapter = MagicMock()
main_module.difficulty_adapter.adapt_difficulty = AsyncMock(
    return_value={
        "suggested_difficulty": "Intermedio",
        "reason": "Good progress",
    }
)

main_module.error_pattern_analyzer = MagicMock()
main_module.error_pattern_analyzer.analyze = AsyncMock(
    return_value={"patterns": [], "summary": {"total": 0}}
)

main_module.sandbox_service = MagicMock()
main_module.sandbox_service.execute_and_compare = AsyncMock(
    return_value={
        "passed": True,
        "score": 1.0,
        "output": "mock output",
        "error": None,
    }
)

main_module.metrics_service = MagicMock()
main_module.metrics_service.track_event = AsyncMock(return_value=None)

main_module.alerts_service = MagicMock()
main_module.alerts_service.generate_alerts = AsyncMock(return_value=[])

main_module.exercise_generator_service = MagicMock()

main_module.ai_tutor_service = MagicMock()
main_module.ai_tutor_service.answer_question = AsyncMock(
    return_value="Mock tutor answer"
)
main_module.ai_tutor_service.llm = MagicMock()
main_module.ai_tutor_service.llm.chat = AsyncMock(
    return_value="Mock LLM explanation"
)

main_module.analytics_scheduler = MagicMock()
main_module.analytics_scheduler.start = MagicMock()
main_module.analytics_scheduler.stop = MagicMock()

# ── TestClient ──
client = TestClient(app)


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def make_token(
    user_id: int = 1,
    email: str = "test@test.com",
    role: str = "student",
) -> str:
    return jwt.encode(
        {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def auth_headers(
    user_id: int = 1,
    email: str = "test@test.com",
    role: str = "student",
) -> dict:
    return {"Cookie": f"auth-token={make_token(user_id, email, role)}"}


def make_user(
    id: int = 1,
    email: str = "test@test.com",
    full_name: str = "Test User",
    role: UserRole = UserRole.STUDENT,
    password_hash: str = "$2b$12$mockhash",
) -> User:
    return User(
        id=id,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role=role,
        is_active=True,
        points=100,
        streak_days=5,
        public_id=str(uuid4()),
    )


@pytest.fixture(autouse=True)
def _reset_mocks():
    """Reset shared mocks before each test so side_effects don't leak."""
    main_module.user_repository.get_by_id.reset_mock()
    main_module.user_repository.get_by_email.reset_mock()
    main_module.user_repository.create.reset_mock()
    main_module.module_repository.get_by_id.reset_mock()
    main_module.module_repository.get_all.reset_mock()
    main_module.enrollment_repository.get_by_student.reset_mock()
    main_module.ml_orchestrator.predict_student.reset_mock()


# ═══════════════════════════════════════════════════════════════════
# Health
# ═══════════════════════════════════════════════════════════════════


class TestHealth:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Robolearn API running"
        assert data["version"] == "1.0.0"

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


# ═══════════════════════════════════════════════════════════════════
# Auth
# ═══════════════════════════════════════════════════════════════════


class TestAuth:
    def test_register_success(self):
        main_module.user_repository.get_by_email = AsyncMock(return_value=None)
        new_user = make_user(id=5, email="new@test.com")
        main_module.user_repository.create = AsyncMock(return_value=new_user)

        resp = client.post(
            "/api/auth/register",
            json={
                "email": "new@test.com",
                "password": "secret123",
                "full_name": "New User",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["user"]["email"] == "new@test.com"
        assert "auth-token" in resp.cookies

    def test_register_duplicate_email(self):
        existing = make_user(email="dup@test.com")
        main_module.user_repository.get_by_email = AsyncMock(
            return_value=existing
        )

        resp = client.post(
            "/api/auth/register",
            json={
                "email": "dup@test.com",
                "password": "secret123",
                "full_name": "Dup",
            },
        )
        body = resp.json()
        assert resp.status_code == 400, f"Expected 400 got {resp.status_code}: {body}"
        # Response body may be {"detail": ...} (HTTPException) or
        # {"success": False, "error": ...} (JSONResponse)
        detail = body.get("detail") or body.get("error", "")
        assert "registrado" in detail or "registered" in detail

    def test_register_short_password(self):
        main_module.user_repository.get_by_email = AsyncMock(return_value=None)

        resp = client.post(
            "/api/auth/register",
            json={
                "email": "a@b.com",
                "password": "12",
                "full_name": "Short",
            },
        )
        assert resp.status_code == 400

    def test_register_missing_fields(self):
        resp = client.post(
            "/api/auth/register",
            json={"email": "incomplete@test.com"},
        )
        assert resp.status_code == 422

    def test_login_success(self):
        user = make_user(
            id=1,
            email="login@test.com",
            password_hash="$2b$12$abcdefghijklmnopqrstuv",
        )
        main_module.user_repository.get_by_email = AsyncMock(return_value=user)

        with patch("app.main.verify_password_async", return_value=True):
            resp = client.post(
                "/api/auth/login",
                json={"email": "login@test.com", "password": "correct"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "auth-token" in resp.cookies

    def test_login_wrong_password(self):
        user = make_user(
            id=1,
            email="fail@test.com",
            password_hash="$2b$12$abcdefghijklmnopqrstuv",
        )
        main_module.user_repository.get_by_email = AsyncMock(return_value=user)

        with patch("app.main.verify_password_async", return_value=False):
            resp = client.post(
                "/api/auth/login",
                json={"email": "fail@test.com", "password": "wrong"},
            )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self):
        main_module.user_repository.get_by_email = AsyncMock(return_value=None)

        resp = client.post(
            "/api/auth/login",
            json={"email": "nobody@test.com", "password": "whatever"},
        )
        assert resp.status_code == 401

    def test_logout(self):
        resp = client.post(
            "/api/auth/logout",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        set_cookie = resp.headers.get("set-cookie", "")
        assert "auth-token=" in set_cookie


# ═══════════════════════════════════════════════════════════════════
# Users
# ═══════════════════════════════════════════════════════════════════


class TestUsers:
    def test_get_profile_success(self):
        user = make_user(id=1, email="prof@test.com")
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        resp = client.get("/api/users/profile", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["user"]["email"] == "prof@test.com"

    def test_get_profile_no_auth(self):
        resp = client.get("/api/users/profile")
        assert resp.status_code == 401

    def test_get_profile_invalid_token(self):
        resp = client.get(
            "/api/users/profile",
            headers={"Cookie": "auth-token=invalidtoken"},
        )
        assert resp.status_code == 401

    def test_get_profile_not_found(self):
        main_module.user_repository.get_by_id = AsyncMock(return_value=None)

        resp = client.get("/api/users/profile", headers=auth_headers())
        assert resp.status_code == 404

    def test_get_user_by_public_id(self):
        user = make_user(id=2, email="pub@test.com")
        main_module.user_repository.get_by_public_id = AsyncMock(
            return_value=user
        )

        resp = client.get(f"/api/users/by-public-id/{user.public_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["public_id"] == user.public_id

    def test_get_user_by_id_success(self):
        user = make_user(id=42)
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        resp = client.get("/api/users/42")
        assert resp.status_code == 200
        assert resp.json()["user"]["id"] == 42

    def test_get_user_by_id_not_found(self):
        main_module.user_repository.get_by_id = AsyncMock(return_value=None)

        resp = client.get("/api/users/999")
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════
# Modules
# ═══════════════════════════════════════════════════════════════════


class TestModules:
    def test_list_modules_empty(self):
        resp = client.get("/api/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["modules"] == []

    def test_get_module_success(self):
        mod = MagicMock()
        mod.to_dict.return_value = {
            "id": 1,
            "title": "Test Module",
            "description": "A module",
        }
        main_module.module_repository.get_by_id = AsyncMock(return_value=mod)

        resp = client.get("/api/modules/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["module"]["id"] == 1

    def test_get_module_not_found(self):
        main_module.module_repository.get_by_id = AsyncMock(return_value=None)

        resp = client.get("/api/modules/999")
        assert resp.status_code == 404

    def test_enrolled_modules(self):
        user = make_user()
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        now = datetime.now()
        db_cursor.fetchall.return_value = [
            (1, "My Module", "desc", None, 1, "approved", 1, True, False, "beginner",
             5, now, "active", now)
        ]
        db_cursor.execute.return_value = None

        resp = client.get(
            "/api/modules/enrolled",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["modules"]) == 1
        db_cursor.fetchall.return_value = []


# ═══════════════════════════════════════════════════════════════════
# AI / ML (student)
# ═══════════════════════════════════════════════════════════════════


class TestAIML:
    def test_recommendations(self):
        user = make_user()
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        resp = client.get("/api/recommendations", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_learning_path(self):
        resp = client.get("/api/learning-path", headers=auth_headers())
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_performance_prediction(self):
        resp = client.get(
            "/api/performance-prediction/1",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["prediction"]["module_id"] == 1
        assert data["prediction"]["score"] == 0.75


# ═══════════════════════════════════════════════════════════════════
# AI Analytics (teacher)
# ═══════════════════════════════════════════════════════════════════


class TestAIAnalytics:
    @pytest.fixture(autouse=True)
    def _setup_teacher(self):
        teacher = make_user(id=2, role=UserRole.TEACHER)
        main_module.user_repository.get_by_id = AsyncMock(return_value=teacher)
        yield
        main_module.user_repository.get_by_id.reset_mock()

    def _teacher_headers(self):
        return auth_headers(user_id=2, role="teacher")

    def test_student_metrics(self):
        main_module.ml_orchestrator.predict_student.return_value = {
            "predictions": {
                "engagement_projected": {"value": 0.7, "label": "alto"},
                "performance_projected": {"value": 0.8, "label": "alto"},
                "dropout_risk": {"probability": 0.05, "label": "bajo"},
                "frustration_projected": {"class": 0, "value": 0.2},
            },
            "cluster": {"label": "Activo", "id": 1},
            "anomaly": {"is_anomaly": False},
            "recommendations": [],
        }

        resp = client.get(
            "/api/analytics/student/1/metrics",
            headers=self._teacher_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["student_id"] == 1

    def test_analytics_dashboard(self):
        resp = client.get(
            "/api/analytics/dashboard?days=30",
            headers=self._teacher_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_risk_factors(self):
        main_module.ml_orchestrator.predict_student.return_value = {
            "predictions": {
                "engagement_projected": {"value": 0.3, "label": "bajo"},
                "performance_projected": {"value": 0.2, "label": "bajo"},
                "dropout_risk": {"probability": 0.8, "label": "alto"},
                "frustration_projected": {"class": 3, "value": 0.9},
            },
            "cluster": {},
            "anomaly": {},
            "recommendations": ["Review session recommended"],
        }

        resp = client.get(
            "/api/analytics/student/1/risk-factors",
            headers=self._teacher_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["risk_factors"]) > 0


# ═══════════════════════════════════════════════════════════════════
# Intelligent Tutor
# ═══════════════════════════════════════════════════════════════════


class TestTutor:
    def test_tutor_ask_with_auth(self):
        resp = client.post(
            "/api/tutor/ask",
            headers=auth_headers(),
            json={"message": "How do I write a loop?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "response" in data

    def test_tutor_ask_without_auth(self):
        # verify_token requires auth, but verify_token_optional can handle anon.
        # This route uses verify_token which raises 401 without a cookie.
        resp = client.post(
            "/api/tutor/ask",
            json={"message": "Explain variables", "session_id": "anon_sess"},
        )
        assert resp.status_code == 401

    def test_tutor_explain(self):
        resp = client.post(
            "/api/tutor/explain",
            headers=auth_headers(),
            json={"concept": "variables"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "explanation" in data

    def test_tutor_student_level(self):
        resp = client.get(
            "/api/tutor/student-level",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "student_level" in data


# ═══════════════════════════════════════════════════════════════════
# Interactive — Code Execution
# ═══════════════════════════════════════════════════════════════════


class TestCodeExecution:
    def test_execute_simple_code(self):
        resp = client.post(
            "/api/execute-code",
            headers=auth_headers(),
            json={"code": "print('hello')"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "hello" in data["output"]

    def test_execute_syntax_error(self):
        resp = client.post(
            "/api/execute-code",
            headers=auth_headers(),
            json={"code": "print(}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "Syntax Error" in data["error"]

    def test_execute_dangerous_code_blocked(self):
        resp = client.post(
            "/api/execute-code",
            headers=auth_headers(),
            json={"code": "import os; os.system('rm -rf /')"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert "not allowed" in data["error"]

    def test_execute_missing_auth(self):
        resp = client.post(
            "/api/execute-code",
            json={"code": "print('hi')"},
        )
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════
# Exercises
# ═══════════════════════════════════════════════════════════════════


class TestExercises:
    def test_exercise_not_found(self):
        user = make_user()
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)
        db_cursor.fetchone.return_value = None

        resp = client.get(
            "/api/exercises/999/solution-explanation",
            headers=auth_headers(),
        )
        assert resp.status_code == 404
        db_cursor.fetchone.return_value = (0,) * 20

    def test_exercise_attempts_empty(self):
        user = make_user()
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        resp = client.get(
            "/api/exercises/1/attempts",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["attempts"] == []

    def test_exercises_list(self):
        resp = client.get("/api/exercises")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════
# Student Dashboard
# ═══════════════════════════════════════════════════════════════════


class TestStudentDashboard:
    def test_student_dashboard(self):
        user = make_user(id=1)
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        resp = client.get(
            "/api/dashboard/student",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        dashboard = data["dashboard"]
        assert "points" in dashboard
        assert "progress" in dashboard


# ═══════════════════════════════════════════════════════════════════
# Admin
# ═══════════════════════════════════════════════════════════════════


class TestAdmin:
    def _admin_headers(self):
        return auth_headers(user_id=99, role="admin")

    def test_admin_list_users(self):
        resp = client.get("/api/admin/users", headers=self._admin_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["users"] == []

    def test_admin_list_users_forbidden_as_student(self):
        resp = client.get("/api/admin/users", headers=auth_headers())
        assert resp.status_code == 403

    def test_admin_update_role(self):
        resp = client.put(
            "/api/admin/users/1/role",
            headers=self._admin_headers(),
            json={"role": "teacher"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_admin_update_role_invalid(self):
        resp = client.put(
            "/api/admin/users/1/role",
            headers=self._admin_headers(),
            json={"role": "invalid_role"},
        )
        assert resp.status_code == 400

    def test_admin_pending_teachers(self):
        resp = client.get(
            "/api/admin/teachers/pending",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["requests"] == []

    def test_admin_approve_teacher(self):
        resp = client.post(
            "/api/admin/teachers/approve/2",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_admin_approve_module_deletion(self):
        mod = MagicMock()
        mod.title = "Module to delete"
        main_module.module_repository.get_by_id = AsyncMock(return_value=mod)

        resp = client.post(
            "/api/admin/modules/1/approve-deletion",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_admin_dashboard(self):
        resp = client.get(
            "/api/dashboard/admin",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_ml_reload_models_admin(self):
        resp = client.post(
            "/api/ml/reload-models",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════
# Teacher routes
# ═══════════════════════════════════════════════════════════════════


class TestTeacher:
    @pytest.fixture(autouse=True)
    def _setup(self):
        teacher = make_user(id=5, role=UserRole.TEACHER)
        main_module.user_repository.get_by_id = AsyncMock(return_value=teacher)

    def _headers(self):
        return auth_headers(user_id=5, role="teacher")

    def test_teacher_dashboard(self):
        resp = client.get(
            "/api/teacher/dashboard",
            headers=self._headers(),
        )
        assert resp.status_code == 200

    def test_teacher_students(self):
        resp = client.get(
            "/api/teacher/students",
            headers=self._headers(),
        )
        assert resp.status_code == 200

    def test_teacher_alerts(self):
        resp = client.get(
            "/api/teacher/alerts",
            headers=self._headers(),
        )
        assert resp.status_code == 200

    def test_exercise_difficulty_analysis(self):
        resp = client.get(
            "/api/exercises/difficulty-analysis",
            headers=self._headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_teacher_student_detail(self):
        resp = client.get(
            "/api/teacher/students/1",
            headers=self._headers(),
        )
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# Enrollments
# ═══════════════════════════════════════════════════════════════════


class TestEnrollments:
    def test_enroll_module(self):
        user = make_user()
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        mod = MagicMock()
        mod.is_published = True
        mod.title = "Test Module"
        main_module.module_repository.get_by_id = AsyncMock(return_value=mod)

        main_module.enrollment_repository.get_by_student_and_module = (
            AsyncMock(return_value=None)
        )

        enrollment_mock = MagicMock()
        enrollment_mock.to_dict.return_value = {
            "id": 1,
            "student_id": 1,
            "module_id": 1,
            "status": "active",
        }
        main_module.enrollment_repository.create = AsyncMock(
            return_value=enrollment_mock
        )

        resp = client.post(
            "/api/modules/1/enroll",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════
# Chatbot
# ═══════════════════════════════════════════════════════════════════


class TestChatbot:
    def test_chat_public(self):
        resp = client.post(
            "/api/chatbot/public",
            json={
                "message": "Hello",
                "session_id": "test-session",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_chat_authenticated(self):
        user = make_user()
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)

        resp = client.post(
            "/api/chatbot",
            headers=auth_headers(),
            json={"message": "Hello from auth user"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════
# Extra routes — small CRUD / simple handlers
# ═══════════════════════════════════════════════════════════════════


class TestExtraStudentRoutes:
    """Covers small simple routes accessible by any authenticated student."""

    def test_update_profile(self):
        user = make_user(id=1)
        main_module.user_repository.get_by_id = AsyncMock(return_value=user)
        resp = client.put(
            "/api/users/profile",
            headers=auth_headers(),
            json={"full_name": "Updated Name", "bio": "New bio"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_update_profile_not_found(self):
        main_module.user_repository.get_by_id = AsyncMock(return_value=None)
        resp = client.put(
            "/api/users/profile",
            headers=auth_headers(),
            json={"full_name": "Ghost"},
        )
        assert resp.status_code == 404

    def test_modules_create(self):
        """POST /api/modules – teacher creates a module."""
        main_module.user_repository.get_by_id = AsyncMock(
            return_value=make_user(id=5, role=UserRole.TEACHER),
        )
        main_module.module_repository.create = AsyncMock(
            return_value=MagicMock(id=1, to_dict=lambda: {"id": 1, "title": "New"}),
        )
        resp = client.post(
            "/api/modules",
            headers=auth_headers(user_id=5, role="teacher"),
            json={"title": "New Module", "description": "desc"},
        )
        body = resp.json()
        assert resp.status_code == 200, f"Expected 200 got {resp.status_code}: {body}"
        assert body["success"] is True

    def test_modules_update(self):
        main_module.user_repository.get_by_id = AsyncMock(
            return_value=make_user(id=5, role=UserRole.TEACHER),
        )
        mod = MagicMock()
        mod.teacher_id = 5
        mod.to_dict = lambda: {"id": 1, "title": "Updated"}
        main_module.module_repository.get_by_id = AsyncMock(return_value=mod)
        main_module.module_repository.update = AsyncMock(
            return_value=MagicMock(to_dict=lambda: {"id": 1, "title": "Updated"}),
        )
        resp = client.put(
            "/api/modules/1",
            headers=auth_headers(user_id=5, role="teacher"),
            json={"title": "Updated", "description": "new desc"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_modules_update_not_found(self):
        main_module.user_repository.get_by_id = AsyncMock(
            return_value=make_user(id=5, role=UserRole.TEACHER),
        )
        main_module.module_repository.get_by_id = AsyncMock(return_value=None)
        resp = client.put(
            "/api/modules/999",
            headers=auth_headers(user_id=5, role="teacher"),
            json={"title": "Ghost"},
        )
        assert resp.status_code == 404

    def test_tutor_feedback(self):
        mock_db = MagicMock()
        main_module.behavioral_repo.get_db = AsyncMock(return_value=mock_db)
        resp = client.post(
            "/api/tutor/feedback",
            headers=auth_headers(),
            json={"helpful": True, "message": "Great!"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_lessons_complete(self):
        db_cursor.fetchone.return_value = (1,)
        resp = client.post(
            "/api/lessons/1/complete",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        db_cursor.fetchone.return_value = (0,) * 20

    def test_lessons_complete_not_found(self):
        db_cursor.fetchone.return_value = None
        resp = client.post(
            "/api/lessons/999/complete",
            headers=auth_headers(),
        )
        assert resp.status_code == 404
        db_cursor.fetchone.return_value = (0,) * 20

    def test_achievements_list(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchall.side_effect = [
            [(1, "First Steps", "desc", "star", 10, '{"type":"login"}')],
            [(1, fake_dt)],
        ]
        resp = client.get("/api/achievements", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["achievements"]) == 1
        db_cursor.fetchall.side_effect = None
        db_cursor.fetchall.return_value = []

    def test_achievements_recent(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchall.return_value = [
            (1, "Star", "desc", "star", 10, fake_dt),
        ]
        resp = client.get("/api/achievements/recent", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["achievements"]) == 1
        db_cursor.fetchall.return_value = []

    def test_modules_search(self):
        db_cursor.fetchall.return_value = [
            (1, "Python 101", "Intro", 5, "Teacher Name"),
        ]
        resp = client.get("/api/modules/search?q=python", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["results"]) == 1
        db_cursor.fetchall.return_value = []

    def test_module_exercises(self):
        db_cursor.fetchall.return_value = [
            (1, 1, "Ex1", "desc", None, "do X", 1, 10, 0),
        ]
        resp = client.get("/api/modules/1/exercises")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["exercises"]) == 1
        db_cursor.fetchall.return_value = []

    def test_log_event(self):
        resp = client.post(
            "/api/events?event_type=test",
            json={"key": "val"},
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_user_history(self):
        main_module.event_repository.get_user_events = AsyncMock(
            return_value=[{"type": "login", "timestamp": "2024-01-01"}],
        )
        resp = client.get("/api/user-history", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["history"]) == 1


class TestExtraTeacherRoutes:
    """Routes requiring teacher role — module/exercise/lesson CRUD, classes."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        teacher = make_user(id=5, role=UserRole.TEACHER)
        main_module.user_repository.get_by_id = AsyncMock(return_value=teacher)

    def _h(self):
        return auth_headers(user_id=5, role="teacher")

    def test_create_module_lesson(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.post(
            "/api/modules/1/lessons",
            headers=self._h(),
            json={"title": "New Lesson", "theory_content": "content", "order": 1},
        )
        assert resp.status_code == 200
        assert resp.json()["lesson_id"] is not None
        db_cursor.fetchone.return_value = (0,) * 20

    def test_create_module_lesson_forbidden(self):
        db_cursor.fetchone.return_value = (99,)
        resp = client.post(
            "/api/modules/1/lessons",
            headers=self._h(),
            json={"title": "X"},
        )
        assert resp.status_code == 403
        db_cursor.fetchone.return_value = (0,) * 20

    def test_create_module_lesson_not_found(self):
        db_cursor.fetchone.return_value = None
        resp = client.post(
            "/api/modules/1/lessons",
            headers=self._h(),
            json={"title": "X"},
        )
        assert resp.status_code == 404
        db_cursor.fetchone.return_value = (0,) * 20

    def test_delete_module_lesson(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.delete(
            "/api/modules/1/lessons/1",
            headers=self._h(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        db_cursor.fetchone.return_value = (0,) * 20

    def test_create_module_exercise(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.post(
            "/api/modules/1/exercises",
            headers=self._h(),
            json={"title": "Ex1", "difficulty": 2, "points": 10},
        )
        assert resp.status_code == 200
        assert resp.json()["exercise_id"] is not None
        db_cursor.fetchone.return_value = (0,) * 20

    def test_delete_module_exercise(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.delete(
            "/api/modules/1/exercises/1",
            headers=self._h(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        db_cursor.fetchone.return_value = (0,) * 20

    def test_delete_module_exercise_not_found(self):
        db_cursor.fetchone.return_value = None
        resp = client.delete(
            "/api/modules/1/exercises/1",
            headers=self._h(),
        )
        assert resp.status_code == 404
        db_cursor.fetchone.return_value = (0,) * 20

    def test_create_class(self):
        resp = client.post(
            "/api/classes",
            headers=self._h(),
            json={"title": "New Class", "description": "desc"},
        )
        assert resp.status_code == 200
        assert resp.json()["class_id"] is not None

    def test_delete_class(self):
        resp = client.delete(
            "/api/classes/1",
            headers=self._h(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_enroll_class_new(self):
        db_cursor.fetchone.side_effect = [None, (123,)]
        resp = client.post(
            "/api/classes/1/enroll",
            headers=auth_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["enrollment_id"] is not None
        db_cursor.fetchone.side_effect = None
        db_cursor.fetchone.return_value = (0,) * 20

    def test_enroll_class_already_approved(self):
        db_cursor.fetchone.side_effect = [("approved",), (999,)]
        resp = client.post(
            "/api/classes/1/enroll",
            headers=auth_headers(),
        )
        assert resp.status_code == 400
        db_cursor.fetchone.side_effect = None
        db_cursor.fetchone.return_value = (0,) * 20


class TestExtraAdminRoutes:
    """Admin routes not yet covered."""

    def _admin_headers(self):
        return auth_headers(user_id=99, role="admin")

    def test_reject_teacher(self):
        resp = client.post(
            "/api/admin/teachers/reject/2",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_approve_module(self):
        resp = client.post(
            "/api/admin/modules/1/approve",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_reject_module_deletion(self):
        mod = MagicMock()
        mod.status = "approved"
        main_module.module_repository.get_by_id = AsyncMock(return_value=mod)
        main_module.module_repository.update = AsyncMock()
        resp = client.post(
            "/api/admin/modules/1/reject-deletion",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_reject_module_deletion_not_found(self):
        main_module.module_repository.get_by_id = AsyncMock(return_value=None)
        resp = client.post(
            "/api/admin/modules/999/reject-deletion",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 404

    def test_audit_logs_success(self):
        mock_db = MagicMock()
        mock_evt = MagicMock()
        mock_evt["_id"] = "abc123"
        mock_evt["timestamp"] = "2024-01-01T00:00:00"
        mock_db.events.find.return_value.sort.return_value.limit.return_value = [mock_evt]
        main_module.event_repository.get_db = AsyncMock(return_value=mock_db)
        resp = client.get(
            "/api/admin/audit-logs",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["events"]) == 1

    def test_audit_logs_error(self):
        main_module.event_repository.get_db = AsyncMock(
            side_effect=Exception("DB error"),
        )
        resp = client.get(
            "/api/admin/audit-logs",
            headers=self._admin_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is False


class TestChallenges:
    """Challenge routes accessible to students."""

    def test_list_challenges_as_student(self):
        db_cursor.fetchall.return_value = [
            (1, "Challenge 1", "desc", "easy", 50, "Teacher",
             "base_code", None, True, False, 0),
        ]
        resp = client.get("/api/challenges", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["challenges"]) == 1
        db_cursor.fetchall.return_value = []

    def test_get_challenge_found(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchone.side_effect = [
            (
                1, "Challenge 1", "desc", "instructions", "easy", 50,
                5, "Teacher", "base", "sol", "output", "expected", "test",
                None, True, 3, fake_dt,
            ),
            None,  # second fetchone for challenge_attempts (student query returns nothing)
        ]
        resp = client.get("/api/challenges/1", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["challenge"]["title"] == "Challenge 1"
        db_cursor.fetchone.side_effect = None
        db_cursor.fetchone.return_value = (0,) * 20

    def test_get_challenge_not_found(self):
        db_cursor.fetchone.return_value = None
        resp = client.get("/api/challenges/999", headers=auth_headers())
        assert resp.status_code == 404
        db_cursor.fetchone.return_value = (0,) * 20


class TestExtraTeacherRoutes2:
    """Additional teacher routes — pending enrollments, class views, etc."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        teacher = make_user(id=5, role=UserRole.TEACHER)
        main_module.user_repository.get_by_id = AsyncMock(return_value=teacher)

    def _h(self):
        return auth_headers(user_id=5, role="teacher")

    def test_list_challenges_as_teacher(self):
        db_cursor.fetchall.return_value = [
            (1, "Challenge 1", "desc", "easy", 50, "Teacher",
             "base", None, True, False, 0),
        ]
        resp = client.get("/api/challenges", headers=self._h())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["challenges"]) == 1
        db_cursor.fetchall.return_value = []

    def test_pending_enrollments(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchall.return_value = [
            (1, 10, 1, "pending", fake_dt, "Student", "s@t.com", "Class 1"),
        ]
        resp = client.get("/api/teacher/pending-enrollments", headers=self._h())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["requests"]) == 1
        db_cursor.fetchall.return_value = []

    def test_approve_enrollment_by_id(self):
        resp = client.post(
            "/api/teacher/enrollments/approve",
            headers=self._h(),
            json={"enrollment_id": 1},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_approve_enrollment_by_class_student(self):
        resp = client.post(
            "/api/teacher/enrollments/approve",
            headers=self._h(),
            json={"class_id": 1, "student_id": 10},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_approve_enrollment_missing_params(self):
        resp = client.post(
            "/api/teacher/enrollments/approve",
            headers=self._h(),
            json={},
        )
        assert resp.status_code == 400

    def test_reject_enrollment_by_id(self):
        resp = client.post(
            "/api/teacher/enrollments/reject",
            headers=self._h(),
            json={"enrollment_id": 1},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_reject_enrollment_by_class_student(self):
        resp = client.post(
            "/api/teacher/enrollments/reject",
            headers=self._h(),
            json={"class_id": 1, "student_id": 10},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_reject_enrollment_missing_params(self):
        resp = client.post(
            "/api/teacher/enrollments/reject",
            headers=self._h(),
            json={},
        )
        assert resp.status_code == 400

    def test_unenroll_student(self):
        db_cursor.fetchone.return_value = (1,)
        resp = client.post(
            "/api/classes/1/unenroll/10",
            headers=self._h(),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        db_cursor.fetchone.return_value = (0,) * 20

    def test_unenroll_student_forbidden(self):
        db_cursor.fetchone.return_value = None
        resp = client.post(
            "/api/classes/1/unenroll/10",
            headers=self._h(),
        )
        assert resp.status_code == 403
        db_cursor.fetchone.return_value = (0,) * 20

    def test_list_classes_teacher(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchall.return_value = [
            (1, "Class 1", "desc", "cat", "easy", 5, True, fake_dt, "Teacher", 3, 10),
        ]
        resp = client.get("/api/classes", headers=self._h())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["classes"]) == 1
        db_cursor.fetchall.return_value = []

    def test_list_classes_student(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchall.return_value = [
            (1, "Class 1", "desc", "cat", "easy", 5, True, fake_dt, "Teacher", 3, 10),
        ]
        resp = client.get("/api/classes", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["classes"]) == 1
        db_cursor.fetchall.return_value = []

    def test_my_classes(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchall.return_value = [
            (1, "Class 1", "desc", "cat", "easy", 5, True, fake_dt, 3, 10),
        ]
        resp = client.get("/api/classes/my-classes", headers=self._h())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["classes"]) == 1
        db_cursor.fetchall.return_value = []

    def test_enrolled_classes(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchall.return_value = [
            (1, "Class 1", "desc", "cat", "easy", 5, "Teacher", "approved", fake_dt, fake_dt),
        ]
        resp = client.get("/api/classes/enrolled", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["classes"]) == 1
        db_cursor.fetchall.return_value = []

    def test_get_class_found(self):
        from datetime import datetime
        fake_dt = datetime(2024, 1, 1)
        db_cursor.fetchone.side_effect = [
            (1, "Class 1", "desc", "cat", "easy", 5, True, fake_dt, "Teacher"),
            None,  # no enrollment
        ]
        db_cursor.fetchall.return_value = [
            (1, "Module 1", "desc", "theory", 0, fake_dt, 5),
        ]
        resp = client.get("/api/classes/1", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["class"]["title"] == "Class 1"
        db_cursor.fetchone.side_effect = None
        db_cursor.fetchone.return_value = (0,) * 20
        db_cursor.fetchall.return_value = []

    def test_get_class_not_found(self):
        db_cursor.fetchone.return_value = None
        resp = client.get("/api/classes/999")
        assert resp.status_code == 404
        db_cursor.fetchone.return_value = (0,) * 20

    def test_update_class(self):
        resp = client.put(
            "/api/classes/1",
            headers=self._h(),
            json={"title": "Updated Class", "difficulty": "Avanzado"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_update_module_lesson(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.put(
            "/api/modules/1/lessons/1",
            headers=self._h(),
            json={"title": "Updated", "theory_content": "new"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        db_cursor.fetchone.return_value = (0,) * 20

    def test_update_module_lesson_forbidden(self):
        db_cursor.fetchone.return_value = (99,)
        resp = client.put(
            "/api/modules/1/lessons/1",
            headers=self._h(),
            json={"title": "X"},
        )
        assert resp.status_code == 403
        db_cursor.fetchone.return_value = (0,) * 20

    def test_update_module_exercise(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.put(
            "/api/modules/1/exercises/1",
            headers=self._h(),
            json={"title": "Updated Ex", "difficulty": 2},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        db_cursor.fetchone.return_value = (0,) * 20

    def test_request_module_deletion(self):
        mod = MagicMock()
        mod.teacher_id = 5
        main_module.module_repository.get_by_id = AsyncMock(return_value=mod)
        main_module.module_repository.update = AsyncMock()
        resp = client.delete("/api/modules/1", headers=self._h())
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_request_module_deletion_not_found(self):
        main_module.module_repository.get_by_id = AsyncMock(return_value=None)
        resp = client.delete("/api/modules/999", headers=self._h())
        assert resp.status_code == 404

    def test_get_module_lessons(self):
        from datetime import datetime
        db_cursor.fetchall.side_effect = [
            [(1, "Lesson 1", "theory", 0)],       # lessons query
            [],                                      # exercises for lesson
        ]
        db_cursor.fetchone.return_value = (1, "Module 1", 5)
        resp = client.get("/api/modules/1/lessons", headers=auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert len(data["lessons"]) == 1
        db_cursor.fetchall.side_effect = None
        db_cursor.fetchall.return_value = []
        db_cursor.fetchone.return_value = (0,) * 20

    def test_update_module_lesson_add_order(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.put(
            "/api/modules/1/lessons/1",
            headers=self._h(),
            json={"title": "X", "order": 2},
        )
        assert resp.status_code == 200
        db_cursor.fetchone.return_value = (0,) * 20

    def test_update_module_exercise_add_order(self):
        db_cursor.fetchone.return_value = (5,)
        resp = client.put(
            "/api/modules/1/exercises/1",
            headers=self._h(),
            json={"title": "X", "order": 1},
        )
        assert resp.status_code == 200
        db_cursor.fetchone.return_value = (0,) * 20

    def test_update_class_no_fields(self):
        resp = client.put(
            "/api/classes/1",
            headers=self._h(),
            json={},
        )
        assert resp.status_code == 400


class TestAIRoutes:
    """AI route tests (rag, tutor, exercise suggestions)."""

    def setup_method(self):
        main_module.rag_service = MagicMock()
        main_module.rag_service.index_content = AsyncMock()
        main_module.rag_service.search = AsyncMock(return_value=[])

    def test_rag_index(self):
        teacher = make_user(id=5, role=UserRole.TEACHER)
        main_module.user_repository.get_by_id = AsyncMock(return_value=teacher)
        resp = client.post(
            "/api/ai/rag/index",
            headers=auth_headers(user_id=5, role="teacher"),
            json={"text": "doc text", "source_type": "manual", "source_id": "1"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_rag_search(self):
        resp = client.post(
            "/api/ai/rag/search",
            headers=auth_headers(),
            json={"query": "hello", "top_k": 3},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_ai_tutor_ask_v2(self):
        resp = client.post(
            "/api/ai/tutor/ask-v2",
            headers=auth_headers(),
            json={"message": "Help me", "student_level": "beginner"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_ai_tutor_hint(self):
        main_module.ai_tutor_service.generate_hint = AsyncMock(
            return_value="Try using a loop here",
        )
        resp = client.post(
            "/api/ai/tutor/hint",
            headers=auth_headers(),
            json={"title": "Loop", "description": "make a loop", "attempts": 2},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_ai_exercises_suggest(self):
        teacher = make_user(id=5, role=UserRole.TEACHER)
        main_module.user_repository.get_by_id = AsyncMock(return_value=teacher)
        main_module.exercise_generator_service.generate_suggestions = AsyncMock(
            return_value=[{
                "suggested_title": "Var 1",
                "suggested_description": "desc",
                "suggested_instructions": "instr",
                "suggested_solution": "sol",
                "rationale": "good",
            }],
        )
        main_module.exercise_generator_service.save_suggestion = AsyncMock(
            return_value=42,
        )
        resp = client.post(
            "/api/ai/exercises/suggest",
            headers=auth_headers(user_id=5, role="teacher"),
            json={"exercise_id": 1, "title": "Ex1", "description": "desc",
                  "instructions": "do it", "solution": "sol", "difficulty": 2},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert len(resp.json()["suggestions"]) == 1

    def test_ai_list_suggestions(self):
        main_module.exercise_generator_service.list_pending_suggestions = AsyncMock(
            return_value=[{"id": 1, "title": "Suggestion 1"}],
        )
        resp = client.get(
            "/api/ai/exercises/suggestions",
            headers=auth_headers(user_id=99, role="admin"),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_ai_approve_suggestion(self):
        main_module.exercise_generator_service.approve_suggestion = AsyncMock(
            return_value=True,
        )
        resp = client.post(
            "/api/ai/exercises/suggestions/1/approve",
            headers=auth_headers(user_id=99, role="admin"),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_ai_approve_suggestion_not_found(self):
        main_module.exercise_generator_service.approve_suggestion = AsyncMock(
            return_value=False,
        )
        resp = client.post(
            "/api/ai/exercises/suggestions/999/approve",
            headers=auth_headers(user_id=99, role="admin"),
        )
        assert resp.status_code == 404

    def test_ai_reject_suggestion(self):
        main_module.exercise_generator_service.reject_suggestion = AsyncMock()
        resp = client.post(
            "/api/ai/exercises/suggestions/1/reject",
            headers=auth_headers(user_id=99, role="admin"),
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True
