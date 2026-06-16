"""Tests for domain entities and value objects (no database dependencies)."""
import pytest
from datetime import datetime, timezone


class TestUserEntity:
    def test_user_creation(self):
        from domain.entities.user import User, UserRole, TeacherRequestStatus
        u = User(id=1, email="test@test.com", password_hash="hash", full_name="Test", role=UserRole.STUDENT)
        assert u.id == 1
        assert u.role == UserRole.STUDENT
        assert u.is_active is True

    def test_user_to_dict(self):
        from domain.entities.user import User, UserRole
        u = User(id=1, email="a@b.com", password_hash="hash", full_name="Name", role=UserRole.TEACHER)
        d = u.to_dict()
        assert d["email"] == "a@b.com"
        assert d["role"] == "teacher"

    def test_user_role_values(self):
        from domain.entities.user import UserRole
        assert UserRole.STUDENT.value == "student"
        assert UserRole.TEACHER.value == "teacher"
        assert UserRole.ADMIN.value == "admin"

    def test_teacher_request_status(self):
        from domain.entities.user import TeacherRequestStatus
        assert TeacherRequestStatus.PENDING.value == "pending"
        assert TeacherRequestStatus.APPROVED.value == "approved"


class TestModuleEntity:
    def test_module_creation(self):
        from domain.entities.module import Module, ContentStatus
        m = Module(id=1, title="Test Module", description="Desc", teacher_id=10)
        assert m.title == "Test Module"
        assert m.status == ContentStatus.DRAFT
        assert m.is_published is False

    def test_module_to_dict(self):
        from domain.entities.module import Module
        m = Module(id=1, title="T", description="D", teacher_id=1)
        d = m.to_dict()
        assert d["title"] == "T"


class TestExerciseEntity:
    def test_exercise_creation(self):
        from domain.entities.exercise import Exercise
        e = Exercise(id=1, module_id=1, title="Ex1", description="Desc", instructions="Do X", difficulty=2, points=10, order=1)
        assert e.title == "Ex1"
        assert e.difficulty == 2

    def test_exercise_to_dict(self):
        from domain.entities.exercise import Exercise
        e = Exercise(id=1, module_id=1, title="T", description="D", instructions="I", difficulty=1, points=5, order=1)
        d = e.to_dict()
        assert d["points"] == 5


class TestEnrollmentEntity:
    def test_enrollment_creation(self):
        from domain.entities.enrollment import Enrollment
        from datetime import datetime
        now = datetime.now()
        e = Enrollment(id=1, student_id=1, module_id=1, status="active", enrolled_at=now, completed_at=None)
        assert e.student_id == 1
        assert e.status == "active"

    def test_enrollment_to_dict(self):
        from domain.entities.enrollment import Enrollment
        from datetime import datetime
        now = datetime.now()
        e = Enrollment(id=1, student_id=1, module_id=1, status="active", enrolled_at=now, completed_at=None)
        d = e.to_dict()
        assert d["status"] == "active"


class TestChallengeEntity:
    def test_challenge_creation(self):
        from domain.entities.challenge import Challenge
        c = Challenge(id=1, title="Challenge1", description="Desc", instructions="Do", teacher_id=5, difficulty=3, points=100)
        assert c.title == "Challenge1"
        assert c.points == 100

    def test_challenge_to_dict(self):
        from domain.entities.challenge import Challenge
        c = Challenge(id=1, title="T", description="D", instructions="I", teacher_id=1, difficulty=1, points=10)
        d = c.to_dict()
        assert d["difficulty"] == 1


class TestAchievementEntity:
    def test_achievement_creation(self):
        from domain.entities.achievement import Achievement
        a = Achievement(id=1, name="Achiever", description="Did it", icon="star", points=50, criteria="{}")
        assert a.name == "Achiever"

    def test_achievement_to_dict(self):
        from domain.entities.achievement import Achievement, UserAchievement
        a = Achievement(id=1, name="A", description="D", icon="i", points=10, criteria="{}")
        d = a.to_dict()
        assert d["name"] == "A"
        ua = UserAchievement(id=1, user_id=1, achievement_id=1)
        assert ua.achievement_id == 1


class TestAlertEntity:
    def test_alert_creation(self):
        from domain.entities.alert import Alert, AlertType, AlertPriority
        a = Alert(id="1", teacher_id=1, student_id=1, module_id=1, type=AlertType.DIFFICULTY,
                  priority=AlertPriority.HIGH, message="Alert!", recommendations=[], created_at="2025-01-01T00:00:00")
        assert a.type == AlertType.DIFFICULTY
        assert a.priority == AlertPriority.HIGH

    def test_alert_type_values(self):
        from domain.entities.alert import AlertType, AlertPriority
        assert AlertType.DIFFICULTY.value == "difficulty"
        assert AlertType.FAST_LEARNER.value == "fast_learner"
        assert AlertPriority.HIGH.value == "high"


class TestProgressValueObject:
    def test_progress_creation(self):
        from domain.valueObjects.progress import Progress
        p = Progress(user_id=1, module_id=1, completed_exercises=5, total_exercises=10, points_earned=50)
        assert p.percentage == 50.0
        assert p.is_completed is False

    def test_progress_update(self):
        from domain.valueObjects.progress import Progress
        p = Progress(user_id=1, module_id=1)
        p.update_progress(8, 10, 80)
        assert p.percentage == 80.0
        assert p.is_completed is False

    def test_progress_completed(self):
        from domain.valueObjects.progress import Progress
        p = Progress(user_id=1, module_id=1)
        p.update_progress(10, 10, 100)
        assert p.percentage == 100.0
        assert p.is_completed is True

    def test_progress_to_dict(self):
        from domain.valueObjects.progress import Progress
        p = Progress(user_id=1, module_id=1, completed_exercises=3, total_exercises=10, points_earned=30)
        d = p.to_dict()
        assert d["percentage"] == 30.0


class TestAnalyticsModels:
    def test_student_metrics(self):
        from domain.analytics.student_metrics import StudentMetrics
        m = StudentMetrics(student_id=1, session_days=5, total_sessions=10, total_time_minutes=300,
                          exercise_attempts=20, passed_exercises=15, error_rate=0.2,
                          forum_interactions=3, content_views=12)
        d = m.to_dict()
        assert d["student_id"] == 1
        assert d["session_days"] == 5
        m2 = StudentMetrics.from_dict(d)
        assert m2.student_id == 1
        assert m2.session_days == 5

    def test_weekly_metrics(self):
        from domain.analytics.weekly_metrics import WeeklyStudentMetrics
        w = WeeklyStudentMetrics(student_id=1, week_number=1, year=2025, avg_session_days=4.0,
                                avg_total_sessions=8.0, avg_total_time_minutes=240.0,
                                avg_exercise_attempts=15.0, avg_passed_exercises=12.0,
                                avg_error_rate=0.15, avg_forum_interactions=2.0,
                                avg_content_views=10.0, engagement_score=0.7, performance_score=0.8,
                                frustration_score=0.3, dropout_risk=0.1,
                                cluster_id=0, cluster_name="Activo")
        d = w.to_dict()
        assert d["week_number"] == 1
        w2 = WeeklyStudentMetrics.from_dict(d)
        assert w2.engagement_score == 0.7

    def test_ml_prediction(self):
        from domain.analytics.ml_predictions import MLPrediction
        p = MLPrediction(student_id=1, week_number=5, predicted_engagement=0.75,
                        predicted_performance=0.8, predicted_dropout_prob=0.1,
                        predicted_frustration_level=0, cluster_id=1, cluster_name="Activo",
                        anomaly_score=0.0, is_anomaly=False)
        d = p.to_dict()
        assert d["predicted_engagement"] == 0.75
        p2 = MLPrediction.from_dict(d)
        assert p2.predicted_performance == 0.8
