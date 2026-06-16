import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime


_await = lambda c: asyncio.run(c)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.description = None
    cursor.rowcount = 0
    return cursor


@pytest.fixture
def mock_get_cursor(mock_cursor):
    with patch('infrastructure.adapters.output.postgres.connection.PostgresConnection.get_cursor') as m:
        m.return_value.__enter__.return_value = mock_cursor
        yield m


@pytest.fixture
def sample_user_row():
    now = datetime.now()
    return (1, "test@example.com", "hash", "Test User", "student", True, None,
            None, "uuid-123", "bio", 0, 0, now, now)


@pytest.fixture
def sample_module_row():
    now = datetime.now()
    return (1, "Test Module", "A module description", "theory...", 1,
            "approved", 1, True, now, now)


@pytest.fixture
def sample_enrollment_row():
    now = datetime.now()
    return (1, 1, 1, "active", now, None)


# ---------------------------------------------------------------------------
# PostgresConnection
# ---------------------------------------------------------------------------

class TestPostgresConnection:

    def teardown_method(self):
        from infrastructure.adapters.output.postgres.connection import PostgresConnection
        PostgresConnection._pool = None

    def _patch_threaded_pool(self, mock_pool=None):
        import infrastructure.adapters.output.postgres.connection as conn_module
        if mock_pool is None:
            mock_pool = MagicMock()
        return patch.object(conn_module, 'ThreadedConnectionPool', return_value=mock_pool), mock_pool

    def test_init_pool_creates_pool(self):
        from infrastructure.adapters.output.postgres.connection import PostgresConnection
        PostgresConnection._pool = None
        patcher, mock_pool = self._patch_threaded_pool()
        with patcher:
            PostgresConnection.init_pool()
        assert PostgresConnection._pool is mock_pool

    def test_init_pool_skips_if_exists(self):
        from infrastructure.adapters.output.postgres.connection import PostgresConnection
        existing = MagicMock()
        PostgresConnection._pool = existing
        PostgresConnection.init_pool()
        assert PostgresConnection._pool is existing

    def test_close_pool(self):
        from infrastructure.adapters.output.postgres.connection import PostgresConnection
        pool = MagicMock()
        PostgresConnection._pool = pool
        PostgresConnection.close_pool()
        pool.closeall.assert_called_once()
        assert PostgresConnection._pool is None

    def test_close_pool_noop_when_none(self):
        from infrastructure.adapters.output.postgres.connection import PostgresConnection
        PostgresConnection._pool = None
        PostgresConnection.close_pool()

    def _get_cursor_setup(self):
        from infrastructure.adapters.output.postgres.connection import PostgresConnection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        return PostgresConnection, mock_conn, mock_cursor

    def test_get_cursor_success(self):
        PostgresConnection, mock_conn, mock_cursor = self._get_cursor_setup()
        pool_instance = MagicMock()
        pool_instance.getconn.return_value = mock_conn
        PostgresConnection._pool = pool_instance

        with PostgresConnection.get_cursor() as cursor:
            assert cursor is mock_cursor
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        pool_instance.putconn.assert_called_once_with(mock_conn)

    def test_get_cursor_rollback_on_error(self):
        PostgresConnection, mock_conn, _ = self._get_cursor_setup()
        pool_instance = MagicMock()
        pool_instance.getconn.return_value = mock_conn
        PostgresConnection._pool = pool_instance
        mock_conn.cursor.side_effect = Exception("db error")

        with pytest.raises(Exception, match="db error"):
            with PostgresConnection.get_cursor():
                pass
        mock_conn.rollback.assert_called_once()

    def test_get_cursor_init_pool_if_none(self):
        PostgresConnection, mock_conn, mock_cursor = self._get_cursor_setup()
        PostgresConnection._pool = None
        pool_instance = MagicMock()
        pool_instance.getconn.return_value = mock_conn
        patcher, _ = self._patch_threaded_pool(pool_instance)
        with patcher:
            PostgresConnection._pool = None
            with PostgresConnection.get_cursor() as cursor:
                assert cursor is mock_cursor


# ---------------------------------------------------------------------------
# ProcedureRunner
# ---------------------------------------------------------------------------

class TestProcedureRunner:

    def test_call_function_returns_rows(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["id"], ["name"]]
        mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
        result = ProcedureRunner.call_function("fn_get_users", [])
        assert result == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    def test_call_function_empty_description(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = None
        result = ProcedureRunner.call_function("fn_get_users", [])
        assert result == []

    def test_call_function_no_params(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["cnt"]]
        mock_cursor.fetchall.return_value = [(42,)]
        result = ProcedureRunner.call_function("fn_count")
        assert result == [{"cnt": 42}]

    def test_execute_procedure_returns_rows(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["col"]]
        mock_cursor.fetchall.return_value = [("val",)]
        result = ProcedureRunner.execute_procedure("sp_do", [1])
        assert result == [{"col": "val"}]

    def test_execute_procedure_empty(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = None
        result = ProcedureRunner.execute_procedure("sp_noop", [])
        assert result == []

    def test_execute_function_single_found(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["id"]]
        mock_cursor.fetchall.return_value = [(99,)]
        result = ProcedureRunner.execute_function_single("fn_get", [1])
        assert result == {"id": 99}

    def test_execute_function_single_not_found(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["id"]]
        mock_cursor.fetchall.return_value = []
        result = ProcedureRunner.execute_function_single("fn_get", [1])
        assert result is None

    def test_named_functions(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["result"]]
        mock_cursor.fetchall.return_value = [("ok",)]
        assert ProcedureRunner.get_student_progress_summary(1) == {"result": "ok"}
        assert ProcedureRunner.get_teacher_dashboard(1) == {"result": "ok"}
        assert ProcedureRunner.get_admin_stats() == {"result": "ok"}
        assert ProcedureRunner.search_users("term", "student", 50, 0) == [{"result": "ok"}]
        assert ProcedureRunner.upsert_progress(1, 1, 10) == {"result": "ok"}
        assert ProcedureRunner.record_exercise_attempt(1, 1, True, 0.9) == {"result": "ok"}
        assert ProcedureRunner.enroll_student(1, 1) == {"result": "ok"}
        assert ProcedureRunner.check_and_award_achievements(1) == [{"result": "ok"}]

    def test_award_points_returns_int(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["sp_award_points"]]
        mock_cursor.fetchall.return_value = [(50,)]
        result = ProcedureRunner.award_points(1, 50, "test")
        assert result == 50

    def test_award_points_returns_none(self, mock_cursor, mock_get_cursor):
        from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
        mock_cursor.description = [["sp_award_points"]]
        mock_cursor.fetchall.return_value = []
        result = ProcedureRunner.award_points(1, 50, "test")
        assert result is None


# ---------------------------------------------------------------------------
# UserRepositoryImpl
# ---------------------------------------------------------------------------

class TestUserRepositoryImpl:

    def make(self):
        from infrastructure.adapters.output.postgres.user_repository_impl import UserRepositoryImpl
        return UserRepositoryImpl()

    def test_create_returns_user_with_id(self, mock_cursor, mock_get_cursor, sample_user_row):
        from domain.entities.user import User, UserRole
        mock_cursor.fetchone.return_value = (1,)
        repo = self.make()
        user = User(id=None, email="test@example.com", password_hash="hash",
                    full_name="Test User", role=UserRole.STUDENT)
        result = _await(repo.create(user))
        assert result.id == 1
        assert result.public_id is not None

    def test_get_by_id_found(self, mock_cursor, mock_get_cursor, sample_user_row):
        from domain.entities.user import UserRole
        mock_cursor.fetchone.return_value = sample_user_row
        repo = self.make()
        result = _await(repo.get_by_id(1))
        assert result is not None
        assert result.id == 1
        assert result.email == "test@example.com"
        assert result.role == UserRole.STUDENT

    def test_get_by_id_not_found(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchone.return_value = None
        repo = self.make()
        result = _await(repo.get_by_id(999))
        assert result is None

    def test_get_by_email_found(self, mock_cursor, mock_get_cursor, sample_user_row):
        mock_cursor.fetchone.return_value = sample_user_row
        repo = self.make()
        result = _await(repo.get_by_email("test@example.com"))
        assert result is not None
        assert result.email == "test@example.com"

    def test_get_by_email_not_found(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchone.return_value = None
        repo = self.make()
        result = _await(repo.get_by_email("missing@example.com"))
        assert result is None

    def test_get_by_public_id_found(self, mock_cursor, mock_get_cursor, sample_user_row):
        mock_cursor.fetchone.return_value = sample_user_row
        repo = self.make()
        result = _await(repo.get_by_public_id("uuid-123"))
        assert result is not None
        assert result.public_id == "uuid-123"

    def test_get_by_public_id_not_found(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchone.return_value = None
        repo = self.make()
        result = _await(repo.get_by_public_id("missing-uuid"))
        assert result is None

    def test_list_all(self, mock_cursor, mock_get_cursor, sample_user_row):
        mock_cursor.fetchall.return_value = [sample_user_row]
        repo = self.make()
        result = _await(repo.list_all())
        assert len(result) == 1
        assert result[0].id == 1

    def test_list_all_empty(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchall.return_value = []
        repo = self.make()
        result = _await(repo.list_all())
        assert result == []

    def test_update_returns_user(self, mock_cursor, mock_get_cursor, sample_user_row):
        from domain.entities.user import User, UserRole
        repo = self.make()
        user = User(id=1, email="updated@example.com", password_hash="newhash",
                    full_name="Updated", role=UserRole.STUDENT)
        result = _await(repo.update(user))
        assert result.email == "updated@example.com"

    def test_delete_returns_true(self, mock_cursor, mock_get_cursor):
        mock_cursor.rowcount = 1
        repo = self.make()
        result = _await(repo.delete(1))
        assert result is True

    def test_delete_returns_false(self, mock_cursor, mock_get_cursor):
        mock_cursor.rowcount = 0
        repo = self.make()
        result = _await(repo.delete(999))
        assert result is False

    def test_create_assigns_uuid_when_missing(self, mock_cursor, mock_get_cursor):
        from domain.entities.user import User, UserRole
        mock_cursor.fetchone.return_value = (1,)
        repo = self.make()
        user = User(id=None, email="a@b.com", password_hash="h", full_name="A",
                    role=UserRole.STUDENT, public_id=None)
        result = _await(repo.create(user))
        assert result.public_id is not None
        assert len(result.public_id) == 36

    def test_create_non_teacher_status_none(self, mock_cursor, mock_get_cursor):
        from domain.entities.user import User, UserRole
        mock_cursor.fetchone.return_value = (2,)
        repo = self.make()
        user = User(id=None, email="b@c.com", password_hash="h", full_name="B",
                    role=UserRole.TEACHER, teacher_request_status=None)
        result = _await(repo.create(user))
        assert result.id == 2


# ---------------------------------------------------------------------------
# ModuleRepositoryImpl
# ---------------------------------------------------------------------------

class TestModuleRepositoryImpl:

    def make(self):
        from infrastructure.adapters.output.postgres.module_repository_impl import ModuleRepositoryImpl
        return ModuleRepositoryImpl()

    def test_create_returns_module_with_id(self, mock_cursor, mock_get_cursor):
        from domain.entities.module import Module, ContentStatus
        mock_cursor.fetchone.return_value = (5,)
        repo = self.make()
        module = Module(id=None, title="M", description="D", teacher_id=1,
                        status=ContentStatus.DRAFT)
        result = _await(repo.create(module))
        assert result.id == 5

    def test_get_by_id_found(self, mock_cursor, mock_get_cursor, sample_module_row):
        mock_cursor.fetchone.return_value = sample_module_row
        repo = self.make()
        result = _await(repo.get_by_id(1))
        assert result is not None
        assert result.id == 1
        assert result.title == "Test Module"

    def test_get_by_id_not_found(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchone.return_value = None
        repo = self.make()
        result = _await(repo.get_by_id(999))
        assert result is None

    def test_get_by_teacher(self, mock_cursor, mock_get_cursor, sample_module_row):
        mock_cursor.fetchall.return_value = [sample_module_row]
        repo = self.make()
        result = _await(repo.get_by_teacher(1))
        assert len(result) == 1

    def test_get_by_teacher_empty(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchall.return_value = []
        repo = self.make()
        result = _await(repo.get_by_teacher(999))
        assert result == []

    def test_list_published(self, mock_cursor, mock_get_cursor, sample_module_row):
        mock_cursor.fetchall.return_value = [sample_module_row]
        repo = self.make()
        result = _await(repo.list_published())
        assert len(result) == 1

    def test_list_published_empty(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchall.return_value = []
        repo = self.make()
        result = _await(repo.list_published())
        assert result == []

    def test_update_returns_module(self, mock_cursor, mock_get_cursor):
        from domain.entities.module import Module, ContentStatus
        repo = self.make()
        module = Module(id=1, title="Updated", description="Desc", teacher_id=1)
        result = _await(repo.update(module))
        assert result.title == "Updated"

    def test_delete_returns_true(self, mock_cursor, mock_get_cursor):
        mock_cursor.rowcount = 1
        repo = self.make()
        result = _await(repo.delete(1))
        assert result is True

    def test_delete_returns_false(self, mock_cursor, mock_get_cursor):
        mock_cursor.rowcount = 0
        repo = self.make()
        result = _await(repo.delete(999))
        assert result is False


# ---------------------------------------------------------------------------
# EnrollmentRepositoryImpl
# ---------------------------------------------------------------------------

class TestEnrollmentRepositoryImpl:

    def make(self):
        from infrastructure.adapters.output.postgres.enrollment_repository_impl import EnrollmentRepositoryImpl
        return EnrollmentRepositoryImpl()

    def test_create_returns_enrollment(self, mock_cursor, mock_get_cursor, sample_enrollment_row):
        from domain.entities.enrollment import Enrollment
        mock_cursor.fetchone.return_value = sample_enrollment_row
        repo = self.make()
        enrollment = Enrollment(id=None, student_id=1, module_id=1, status="active",
                                enrolled_at=None, completed_at=None)
        result = _await(repo.create(enrollment))
        assert result.id == 1
        assert result.student_id == 1

    def test_get_by_id_found(self, mock_cursor, mock_get_cursor, sample_enrollment_row):
        mock_cursor.fetchone.return_value = sample_enrollment_row
        repo = self.make()
        result = _await(repo.get_by_id(1))
        assert result is not None
        assert result.id == 1

    def test_get_by_id_not_found(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchone.return_value = None
        repo = self.make()
        result = _await(repo.get_by_id(999))
        assert result is None

    def test_get_by_student_and_module_found(self, mock_cursor, mock_get_cursor, sample_enrollment_row):
        mock_cursor.fetchone.return_value = sample_enrollment_row
        repo = self.make()
        result = _await(repo.get_by_student_and_module(1, 1))
        assert result is not None

    def test_get_by_student_and_module_not_found(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchone.return_value = None
        repo = self.make()
        result = _await(repo.get_by_student_and_module(1, 999))
        assert result is None

    def test_get_by_student(self, mock_cursor, mock_get_cursor, sample_enrollment_row):
        mock_cursor.fetchall.return_value = [sample_enrollment_row]
        repo = self.make()
        result = _await(repo.get_by_student(1))
        assert len(result) == 1

    def test_get_by_student_empty(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchall.return_value = []
        repo = self.make()
        result = _await(repo.get_by_student(999))
        assert result == []

    def test_get_by_module(self, mock_cursor, mock_get_cursor, sample_enrollment_row):
        mock_cursor.fetchall.return_value = [sample_enrollment_row]
        repo = self.make()
        result = _await(repo.get_by_module(1))
        assert len(result) == 1

    def test_get_by_module_empty(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchall.return_value = []
        repo = self.make()
        result = _await(repo.get_by_module(999))
        assert result == []

    def test_update_returns_enrollment(self, mock_cursor, mock_get_cursor):
        from domain.entities.enrollment import Enrollment
        repo = self.make()
        enrollment = Enrollment(id=1, student_id=1, module_id=1, status="completed",
                                enrolled_at=None, completed_at=None)
        result = _await(repo.update(enrollment))
        assert result.status == "completed"

    def test_delete_returns_true(self, mock_cursor, mock_get_cursor):
        mock_cursor.rowcount = 1
        repo = self.make()
        result = _await(repo.delete(1))
        assert result is True

    def test_delete_returns_false(self, mock_cursor, mock_get_cursor):
        mock_cursor.rowcount = 0
        repo = self.make()
        result = _await(repo.delete(999))
        assert result is False


# ---------------------------------------------------------------------------
# TeacherRepositoryImpl
# ---------------------------------------------------------------------------

class TestTeacherRepositoryImpl:

    def make(self):
        from infrastructure.adapters.output.postgres.teacher_repository_impl import TeacherRepositoryImpl
        return TeacherRepositoryImpl()

    def test_get_teacher_students(self, mock_cursor, mock_get_cursor):
        now = datetime.now()
        mock_cursor.fetchall.return_value = [
            (1, "Student A", "a@b.com", 10, "Module X", 50.0, now, "active", now),
            (2, "Student B", "b@c.com", 10, "Module X", 100.0, now, "active", now),
        ]
        repo = self.make()
        result = _await(repo.get_teacher_students(1))
        assert len(result) == 2
        assert result[1]["status"] == "Completado"

    def test_get_teacher_students_withdrawn(self, mock_cursor, mock_get_cursor):
        now = datetime.now()
        mock_cursor.fetchall.return_value = [
            (1, "S", "e", 10, "M", 20.0, now, "withdrawn", now),
        ]
        repo = self.make()
        result = _await(repo.get_teacher_students(1))
        assert result[0]["status"] == "Inactivo"

    def test_get_teacher_students_active(self, mock_cursor, mock_get_cursor):
        now = datetime.now()
        mock_cursor.fetchall.return_value = [
            (1, "S", "e", 10, "M", 30.0, now, "active", now),
        ]
        repo = self.make()
        result = _await(repo.get_teacher_students(1))
        assert result[0]["status"] == "Activo"

    def test_get_teacher_students_empty(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchall.return_value = []
        repo = self.make()
        result = _await(repo.get_teacher_students(1))
        assert result == []

    def test_get_teacher_metrics(self, mock_get_cursor):
        cursor = MagicMock()
        cursor.fetchone.side_effect = [
            (10,),           # total_students
            (75.0,),         # avg_progress
            (50.0,),         # completion_rate
        ]
        cursor.fetchall.side_effect = [
            [("Intro", 80.0), ("Advanced", 60.0)],   # course_progress
        ]
        mock_get_cursor.return_value.__enter__.return_value = cursor

        with patch('infrastructure.adapters.output.postgres.procedure_runner.ProcedureRunner.get_student_performance_distribution', return_value=[
            {"name": "Alto (80-100)", "count": 5},
        ]):
            with patch('infrastructure.adapters.output.postgres.procedure_runner.ProcedureRunner.get_weekly_activity', return_value=[
                {"day_name": "Lun", "active_count": 3},
            ]):
                repo = self.make()
                result = _await(repo.get_teacher_metrics(1))
                assert result["total_students"] == 10
                assert result["avg_progress"] == 75.0
                assert result["completion_rate"] == 50.0
                assert len(result["course_progress"]) == 2
                assert result["weekly_activity"][0]["day"] == "Lun"

    def test_get_teacher_metrics_null_values(self, mock_get_cursor):
        cursor = MagicMock()
        cursor.fetchone.side_effect = [
            (0,),    # total_students
            (None,), # avg_progress
            (None,), # completion_rate
        ]
        cursor.fetchall.return_value = []
        mock_get_cursor.return_value.__enter__.return_value = cursor

        with patch('infrastructure.adapters.output.postgres.procedure_runner.ProcedureRunner.get_student_performance_distribution', return_value=[]):
            with patch('infrastructure.adapters.output.postgres.procedure_runner.ProcedureRunner.get_weekly_activity', return_value=[]):
                repo = self.make()
                result = _await(repo.get_teacher_metrics(1))
                assert result["total_students"] == 0
                assert result["avg_progress"] == 0.0

    def test_get_student_details_found(self, mock_cursor, mock_get_cursor):
        now = datetime.now()
        mock_cursor.fetchone.return_value = (1, "Student", "e@mail", 100, 5, now)
        mock_cursor.fetchall.return_value = [
            (10, "Module", 80.0, "active", now),
        ]
        repo = self.make()
        result = _await(repo.get_student_details(1, 1))
        assert result is not None
        assert result["full_name"] == "Student"
        assert len(result["modules"]) == 1

    def test_get_student_details_not_found(self, mock_cursor, mock_get_cursor):
        mock_cursor.fetchone.return_value = None
        repo = self.make()
        result = _await(repo.get_student_details(1, 999))
        assert result is None
