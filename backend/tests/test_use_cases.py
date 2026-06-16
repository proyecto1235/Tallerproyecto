"""Tests for all 5 backend use cases: register_user, get_recommendations,
enroll_student, teacher_dashboard, generate_ai_alerts."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta


def _await(coro):
    return asyncio.run(coro)


class TestRegisterUserUseCase:
    """RegisterUserUseCase — validation, duplicate check, teacher request flag."""

    def make_repo(self):
        repo = MagicMock()
        repo.get_by_email = AsyncMock()
        repo.create = AsyncMock()
        return repo

    def test_missing_email(self):
        from application.useCases.register_user import RegisterUserUseCase
        uc = RegisterUserUseCase(self.make_repo())
        r = _await(uc.execute("", "pass123", "Name"))
        assert r == {"success": False, "error": "Todos los campos son requeridos"}

    def test_missing_password(self):
        from application.useCases.register_user import RegisterUserUseCase
        r = _await(RegisterUserUseCase(self.make_repo()).execute("a@b.com", "", "Name"))
        assert r["success"] is False

    def test_missing_full_name(self):
        from application.useCases.register_user import RegisterUserUseCase
        r = _await(RegisterUserUseCase(self.make_repo()).execute("a@b.com", "pass123", ""))
        assert r["success"] is False

    def test_short_password(self):
        from application.useCases.register_user import RegisterUserUseCase
        r = _await(RegisterUserUseCase(self.make_repo()).execute("a@b.com", "12345", "Name"))
        assert r["success"] is False
        assert "6 caracteres" in r["error"]

    def test_duplicate_email(self):
        from application.useCases.register_user import RegisterUserUseCase
        from domain.entities.user import User, UserRole
        repo = self.make_repo()
        repo.get_by_email.return_value = User(
            id=1, email="dup@test.com", password_hash="h", full_name="Dup",
            role=UserRole.STUDENT,
        )
        uc = RegisterUserUseCase(repo)
        r = _await(uc.execute("dup@test.com", "password123", "Dup"))
        assert r["success"] is False
        assert "ya est" in r["error"]

    def test_register_success(self, monkeypatch):
        from application.useCases.register_user import RegisterUserUseCase
        from domain.entities.user import User, UserRole
        monkeypatch.setattr(
            "application.useCases.register_user.hash_password",
            lambda p: "hashed_" + p,
        )
        repo = self.make_repo()
        repo.get_by_email.return_value = None
        repo.create.return_value = User(
            id=10, email="new@t.com", password_hash="hashed_pass",
            full_name="New User", role=UserRole.STUDENT,
        )
        r = _await(RegisterUserUseCase(repo).execute("new@t.com", "pass123", "New User"))
        assert r["success"] is True
        assert r["user"]["email"] == "new@t.com"
        assert r["user"]["full_name"] == "New User"
        assert r["user"]["role"] == "student"
        assert r["teacher_request_pending"] is False
        repo.create.assert_called_once()
        created = repo.create.call_args[0][0]
        assert created.teacher_request_status is None

    def test_register_request_teacher(self, monkeypatch):
        from application.useCases.register_user import RegisterUserUseCase, TeacherRequestStatus
        monkeypatch.setattr(
            "application.useCases.register_user.hash_password",
            lambda p: "hashed_" + p,
        )
        repo = self.make_repo()
        repo.get_by_email.return_value = None
        from domain.entities.user import User, UserRole
        repo.create.return_value = User(
            id=11, email="teach@t.com", password_hash="h", full_name="T",
            role=UserRole.STUDENT,
        )
        r = _await(RegisterUserUseCase(repo).execute(
            "teach@t.com", "pass123", "T", request_teacher=True))
        assert r["success"] is True
        assert r["teacher_request_pending"] is True
        created = repo.create.call_args[0][0]
        assert created.teacher_request_status == TeacherRequestStatus.PENDING


class TestGetRecommendationsUseCase:
    """GetRecommendationsUseCase — AI recommendations, enrichment, logging."""

    def make_deps(self):
        ai = MagicMock()
        ai.get_recommendations = AsyncMock()
        mod = MagicMock()
        mod.get_by_id = AsyncMock()
        evt = MagicMock()
        evt.get_user_exercise_history = AsyncMock()
        evt.log_event = AsyncMock()
        return ai, mod, evt

    def test_success_with_enrichment(self):
        from application.useCases.get_recommendations import GetRecommendationsUseCase
        from domain.entities.module import Module, ContentStatus
        ai, mod, evt = self.make_deps()
        evt.get_user_exercise_history.return_value = [{"exercise_id": 1, "passed": True}]
        ai.get_recommendations.return_value = [
            {"module_id": 1, "score": 0.9},
            {"module_id": 2, "score": 0.7},
        ]
        module_1 = Module(id=1, title="Mod A", description="Desc A", teacher_id=1,
                          is_published=True, status=ContentStatus.APPROVED)
        module_2 = Module(id=2, title="Mod B", description="Desc B", teacher_id=1,
                          is_published=True, status=ContentStatus.APPROVED)
        mod.get_by_id.side_effect = [module_1, module_2]

        uc = GetRecommendationsUseCase(ai, mod, evt)
        r = _await(uc.execute(42))
        assert r["success"] is True
        assert len(r["recommendations"]) == 2
        assert r["recommendations"][0]["module"]["title"] == "Mod A"
        assert r["recommendations"][1]["module"]["title"] == "Mod B"
        evt.log_event.assert_called_once_with(
            "recommendations_retrieved", 42, {"count": 2})

    def test_module_not_found_skipped(self):
        from application.useCases.get_recommendations import GetRecommendationsUseCase
        ai, mod, evt = self.make_deps()
        ai.get_recommendations.return_value = [
            {"module_id": 1, "score": 0.9},
            {"module_id": 99, "score": 0.5},
        ]
        mod.get_by_id.side_effect = [MagicMock(to_dict=lambda: {"id": 1, "title": "M"}), None]

        uc = GetRecommendationsUseCase(ai, mod, evt)
        r = _await(uc.execute(1))
        assert r["success"] is True
        assert len(r["recommendations"]) == 1

    def test_empty_recommendations(self):
        from application.useCases.get_recommendations import GetRecommendationsUseCase
        ai, mod, evt = self.make_deps()
        ai.get_recommendations.return_value = []
        uc = GetRecommendationsUseCase(ai, mod, evt)
        r = _await(uc.execute(1))
        assert r["success"] is True
        assert r["recommendations"] == []
        evt.log_event.assert_called_once_with(
            "recommendations_retrieved", 1, {"count": 0})

    def test_exception_in_execute(self):
        from application.useCases.get_recommendations import GetRecommendationsUseCase
        ai, mod, evt = self.make_deps()
        evt.get_user_exercise_history.side_effect = ValueError("db down")
        uc = GetRecommendationsUseCase(ai, mod, evt)
        r = _await(uc.execute(1))
        assert r["success"] is False
        assert "db down" in r["error"]


class TestEnrollStudentUseCase:
    """EnrollStudentUseCase — validation, duplicate, non-critical log failure."""

    def make_deps(self):
        user = MagicMock()
        user.get_by_id = AsyncMock()
        mod = MagicMock()
        mod.get_by_id = AsyncMock()
        evt = MagicMock()
        evt.log_event = AsyncMock()
        enroll = MagicMock()
        enroll.get_by_student_and_module = AsyncMock()
        enroll.create = AsyncMock()
        return user, mod, evt, enroll

    def test_student_not_found(self):
        from application.useCases.enroll_student import EnrollStudentUseCase
        user, mod, evt, enroll = self.make_deps()
        user.get_by_id.return_value = None
        uc = EnrollStudentUseCase(user, mod, evt, enroll)
        r = _await(uc.execute(1, 1))
        assert r == {"success": False, "error": "Estudiante no encontrado"}

    def test_module_not_found(self):
        from application.useCases.enroll_student import EnrollStudentUseCase
        from domain.entities.user import User, UserRole
        user, mod, evt, enroll = self.make_deps()
        user.get_by_id.return_value = User(id=1, email="s@t.com",
                                           password_hash="h", full_name="S",
                                           role=UserRole.STUDENT)
        mod.get_by_id.return_value = None
        uc = EnrollStudentUseCase(user, mod, evt, enroll)
        r = _await(uc.execute(1, 1))
        assert r == {"success": False, "error": "Módulo no encontrado"}

    def test_module_not_published(self):
        from application.useCases.enroll_student import EnrollStudentUseCase
        from domain.entities.user import User, UserRole
        from domain.entities.module import Module, ContentStatus
        user, mod, evt, enroll = self.make_deps()
        user.get_by_id.return_value = User(id=1, email="s@t.com",
                                           password_hash="h", full_name="S",
                                           role=UserRole.STUDENT)
        mod.get_by_id.return_value = Module(
            id=1, title="M", description="D", teacher_id=1, is_published=False,
            status=ContentStatus.DRAFT)
        uc = EnrollStudentUseCase(user, mod, evt, enroll)
        r = _await(uc.execute(1, 1))
        assert r == {"success": False, "error": "Módulo no está publicado"}

    def test_duplicate_enrollment(self):
        from application.useCases.enroll_student import EnrollStudentUseCase
        from domain.entities.user import User, UserRole
        from domain.entities.module import Module, ContentStatus
        from domain.entities.enrollment import Enrollment
        user, mod, evt, enroll = self.make_deps()
        user.get_by_id.return_value = User(id=1, email="s@t.com",
                                           password_hash="h", full_name="S",
                                           role=UserRole.STUDENT)
        mod.get_by_id.return_value = Module(
            id=1, title="M", description="D", teacher_id=1, is_published=True,
            status=ContentStatus.APPROVED)
        enroll.get_by_student_and_module.return_value = Enrollment(
            id=5, student_id=1, module_id=1, status="active",
            enrolled_at=None, completed_at=None)
        uc = EnrollStudentUseCase(user, mod, evt, enroll)
        r = _await(uc.execute(1, 1))
        assert r["success"] is False
        assert "matriculado" in r["error"]

    def test_success_with_log(self):
        from application.useCases.enroll_student import EnrollStudentUseCase
        from domain.entities.user import User, UserRole
        from domain.entities.module import Module, ContentStatus
        from domain.entities.enrollment import Enrollment
        user, mod, evt, enroll = self.make_deps()
        user.get_by_id.return_value = User(id=1, email="s@t.com",
                                           password_hash="h", full_name="S",
                                           role=UserRole.STUDENT)
        module = Module(id=1, title="Mod Title", description="D", teacher_id=1,
                        is_published=True, status=ContentStatus.APPROVED)
        mod.get_by_id.return_value = module
        enroll.get_by_student_and_module.return_value = None
        created = Enrollment(id=10, student_id=1, module_id=1, status="active",
                             enrolled_at=datetime.now(), completed_at=None)
        enroll.create.return_value = created

        uc = EnrollStudentUseCase(user, mod, evt, enroll)
        r = _await(uc.execute(1, 1))
        assert r["success"] is True
        assert r["enrollment"]["id"] == 10
        evt.log_event.assert_called_once_with(
            "enrollment_created", 1,
            {"module_id": 1, "module_title": "Mod Title", "status": "active"})

    def test_success_log_failure_non_critical(self):
        from application.useCases.enroll_student import EnrollStudentUseCase
        from domain.entities.user import User, UserRole
        from domain.entities.module import Module, ContentStatus
        from domain.entities.enrollment import Enrollment
        user, mod, evt, enroll = self.make_deps()
        user.get_by_id.return_value = User(id=1, email="s@t.com",
                                           password_hash="h", full_name="S",
                                           role=UserRole.STUDENT)
        mod.get_by_id.return_value = Module(id=1, title="M", description="D",
                                            teacher_id=1, is_published=True,
                                            status=ContentStatus.APPROVED)
        enroll.get_by_student_and_module.return_value = None
        enroll.create.return_value = Enrollment(
            id=11, student_id=1, module_id=1, status="active",
            enrolled_at=datetime.now(), completed_at=None)
        evt.log_event.side_effect = RuntimeError("Mongo down")

        uc = EnrollStudentUseCase(user, mod, evt, enroll)
        r = _await(uc.execute(1, 1))
        assert r["success"] is True

    def test_unexpected_exception(self):
        from application.useCases.enroll_student import EnrollStudentUseCase
        user, mod, evt, enroll = self.make_deps()
        user.get_by_id.side_effect = ValueError("crash")
        uc = EnrollStudentUseCase(user, mod, evt, enroll)
        r = _await(uc.execute(1, 1))
        assert r["success"] is False
        assert "crash" in r["error"]


class TestTeacherDashboardUseCase:
    """TeacherDashboardUseCase — get_students, get_metrics, get_student_detail."""

    def make_repo(self):
        repo = MagicMock()
        repo.get_teacher_students = AsyncMock()
        repo.get_teacher_metrics = AsyncMock()
        repo.get_student_details = AsyncMock()
        return repo

    def test_get_students_success(self):
        from application.useCases.teacher_dashboard import TeacherDashboardUseCase
        repo = self.make_repo()
        repo.get_teacher_students.return_value = [
            {"id": 1, "full_name": "A"}, {"id": 2, "full_name": "B"}]
        uc = TeacherDashboardUseCase(repo)
        r = _await(uc.get_students(1))
        assert r == {"success": True, "students": [{"id": 1, "full_name": "A"},
                                                    {"id": 2, "full_name": "B"}]}

    def test_get_students_exception(self):
        from application.useCases.teacher_dashboard import TeacherDashboardUseCase
        repo = self.make_repo()
        repo.get_teacher_students.side_effect = RuntimeError("db err")
        uc = TeacherDashboardUseCase(repo)
        r = _await(uc.get_students(1))
        assert r["success"] is False
        assert "db err" in r["error"]

    def test_get_metrics_success(self):
        from application.useCases.teacher_dashboard import TeacherDashboardUseCase
        repo = self.make_repo()
        repo.get_teacher_metrics.return_value = {"total_students": 10, "avg_progress": 45}
        uc = TeacherDashboardUseCase(repo)
        r = _await(uc.get_metrics(1))
        assert r == {"success": True, "metrics": {"total_students": 10, "avg_progress": 45}}

    def test_get_metrics_exception(self):
        from application.useCases.teacher_dashboard import TeacherDashboardUseCase
        repo = self.make_repo()
        repo.get_teacher_metrics.side_effect = RuntimeError("metrics err")
        uc = TeacherDashboardUseCase(repo)
        r = _await(uc.get_metrics(1))
        assert r["success"] is False
        assert "metrics err" in r["error"]

    def test_get_student_detail_found(self):
        from application.useCases.teacher_dashboard import TeacherDashboardUseCase
        repo = self.make_repo()
        repo.get_student_details.return_value = {"id": 5, "full_name": "Student"}
        uc = TeacherDashboardUseCase(repo)
        r = _await(uc.get_student_detail(1, 5))
        assert r == {"success": True, "student": {"id": 5, "full_name": "Student"}}

    def test_get_student_detail_not_found(self):
        from application.useCases.teacher_dashboard import TeacherDashboardUseCase
        repo = self.make_repo()
        repo.get_student_details.return_value = None
        uc = TeacherDashboardUseCase(repo)
        r = _await(uc.get_student_detail(1, 99))
        assert r["success"] is False
        assert "no encontrado" in r["error"]

    def test_get_student_detail_exception(self):
        from application.useCases.teacher_dashboard import TeacherDashboardUseCase
        repo = self.make_repo()
        repo.get_student_details.side_effect = RuntimeError("detail err")
        uc = TeacherDashboardUseCase(repo)
        r = _await(uc.get_student_detail(1, 5))
        assert r["success"] is False
        assert "detail err" in r["error"]


class TestGenerateAIAlertsUseCase:
    """GenerateAIAlertsUseCase — grouping, thresholds, priority sorting."""

    def make_repo(self):
        repo = MagicMock()
        repo.get_teacher_students = AsyncMock()
        return repo

    def test_empty_students(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        repo = self.make_repo()
        repo.get_teacher_students.return_value = []
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        assert r == {"success": True, "alerts": []}

    def test_skips_students_without_module_id(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        repo = self.make_repo()
        repo.get_teacher_students.return_value = [
            {"full_name": "No Module", "progress": 50},
        ]
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        assert r["success"] is True
        assert r["alerts"] == []

    def test_high_alert_class_difficulty(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        from domain.entities.alert import AlertPriority, AlertType
        repo = self.make_repo()
        now = datetime.now(timezone.utc).isoformat()
        students = []
        for i in range(5):
            students.append({
                "student_id": i,
                "full_name": f"S{i}",
                "module_id": 1,
                "module_title": "Mod1",
                "progress": 5 if i < 2 else 70,
                "enrolled_at": now,
            })
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        assert r["success"] is True
        high = [a for a in r["alerts"] if a["priority"] == AlertPriority.HIGH]
        assert len(high) == 1
        assert "dificultades" in high[0]["message"].lower()
        assert high[0]["type"] == AlertType.DIFFICULTY

    def test_no_high_alert_when_few_students(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        from domain.entities.alert import AlertPriority
        repo = self.make_repo()
        now = datetime.now(timezone.utc).isoformat()
        students = [
            {"student_id": 1, "full_name": "A", "module_id": 1,
             "module_title": "M", "progress": 0, "enrolled_at": now},
            {"student_id": 2, "full_name": "B", "module_id": 1,
             "module_title": "M", "progress": 0, "enrolled_at": now},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        highs = [a for a in r["alerts"] if a["priority"] == AlertPriority.HIGH]
        assert len(highs) == 0

    def test_medium_alert_slow_learner(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        from domain.entities.alert import AlertPriority, AlertType
        repo = self.make_repo()
        enrolled_long_ago = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        enrolled_recent = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        students = [
            {"student_id": 1, "full_name": "Fast", "module_id": 1,
             "module_title": "M", "progress": 80, "enrolled_at": enrolled_recent},
            {"student_id": 2, "full_name": "Slow", "module_id": 1,
             "module_title": "M", "progress": 5, "enrolled_at": enrolled_long_ago},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        mediums = [a for a in r["alerts"] if a["priority"] == AlertPriority.MEDIUM]
        assert len(mediums) >= 1
        assert mediums[0]["type"] == AlertType.SLOW_LEARNER
        assert mediums[0]["student_name"] == "Slow"

    def test_no_medium_alert_under_7_days(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        from domain.entities.alert import AlertPriority
        repo = self.make_repo()
        just_enrolled = datetime.now(timezone.utc).isoformat()
        students = [
            {"student_id": 1, "full_name": "New", "module_id": 1,
             "module_title": "M", "progress": 1, "enrolled_at": just_enrolled},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        mediums = [a for a in r["alerts"] if a["priority"] == AlertPriority.MEDIUM]
        assert len(mediums) == 0

    def test_low_alert_fast_learner(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        from domain.entities.alert import AlertPriority, AlertType
        repo = self.make_repo()
        # Need multiple students so fast learner's velocity exceeds 2x avg
        enrolled_fast = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        enrolled_normal = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        students = [
            {"student_id": 1, "full_name": "Fast", "module_id": 1,
             "module_title": "M", "progress": 90, "enrolled_at": enrolled_fast},
            {"student_id": 2, "full_name": "Normal", "module_id": 1,
             "module_title": "M", "progress": 20, "enrolled_at": enrolled_normal},
            {"student_id": 3, "full_name": "Normal2", "module_id": 1,
             "module_title": "M", "progress": 20, "enrolled_at": enrolled_normal},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        lows = [a for a in r["alerts"] if a["priority"] == AlertPriority.LOW]
        assert len(lows) >= 1
        assert lows[0]["type"] == AlertType.FAST_LEARNER

    def test_priority_sorting_high_first(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        from domain.entities.alert import AlertPriority
        repo = self.make_repo()
        enrolled_old = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        enrolled_recent = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        students = [
            {"student_id": 1, "full_name": "Slow", "module_id": 1,
             "module_title": "M", "progress": 2, "enrolled_at": enrolled_old},
            {"student_id": 2, "full_name": "Medium", "module_id": 1,
             "module_title": "M", "progress": 3, "enrolled_at": enrolled_old},
            {"student_id": 3, "full_name": "Fast", "module_id": 1,
             "module_title": "M", "progress": 95, "enrolled_at": enrolled_recent},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        priorities = [a["priority"] for a in r["alerts"]]
        high_idx = priorities.index(AlertPriority.HIGH) if AlertPriority.HIGH in priorities else -1
        medium_idx = priorities.index(AlertPriority.MEDIUM) if AlertPriority.MEDIUM in priorities else -1
        low_idx = priorities.index(AlertPriority.LOW) if AlertPriority.LOW in priorities else -1
        if high_idx >= 0 and medium_idx >= 0:
            assert high_idx < medium_idx
        if medium_idx >= 0 and low_idx >= 0:
            assert medium_idx < low_idx

    def test_parse_enrolled_at_no_timezone(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        repo = self.make_repo()
        naive_dt = (datetime.now() - timedelta(days=10)).isoformat()
        students = [
            {"student_id": 1, "full_name": "A", "module_id": 1,
             "module_title": "M", "progress": 50, "enrolled_at": naive_dt},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        assert r["success"] is True

    def test_parse_enrolled_at_invalid(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        repo = self.make_repo()
        students = [
            {"student_id": 1, "full_name": "A", "module_id": 1,
             "module_title": "M", "progress": 50, "enrolled_at": "not-a-date"},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        assert r["success"] is True

    def test_enrolled_at_none_defaults_one_day(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        repo = self.make_repo()
        students = [
            {"student_id": 1, "full_name": "A", "module_id": 1,
             "module_title": "M", "progress": 100, "enrolled_at": None},
        ]
        repo.get_teacher_students.return_value = students
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        assert r["success"] is True

    def test_exception_in_execute(self):
        from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
        repo = self.make_repo()
        repo.get_teacher_students.side_effect = RuntimeError("boom")
        uc = GenerateAIAlertsUseCase(repo)
        r = _await(uc.execute(1))
        assert r["success"] is False
        assert "boom" in r["error"]
