import pytest
import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path


_await = lambda c: asyncio.run(c)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_conn():
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    conn.cursor.return_value = cursor
    return conn


@pytest.fixture
def mock_psycopg2(mock_conn):
    with patch('config.database_init.psycopg2.connect', return_value=mock_conn):
        yield mock_conn


# ===================================================================
# find_script
# ===================================================================

class TestFindScript:

    def test_finds_existing_script(self):
        from config.database_init import find_script
        result = find_script("001-init.sql")
        assert result is not None
        assert result.exists()

    def test_not_found(self):
        from config.database_init import find_script
        result = find_script("nonexistent.sql")
        assert result is None


# ===================================================================
# database_exists
# ===================================================================

class TestDatabaseExists:

    def test_exists_returns_true(self, mock_psycopg2, mock_conn):
        mock_conn.cursor.return_value.fetchone.return_value = (1,)
        from config.database_init import database_exists
        assert database_exists("robolearn") is True

    def test_exists_returns_false(self, mock_psycopg2, mock_conn):
        mock_conn.cursor.return_value.fetchone.return_value = None
        from config.database_init import database_exists
        assert database_exists("robolearn") is False

    def test_exists_handles_exception(self, mock_conn):
        with patch('config.database_init.psycopg2.connect', side_effect=Exception("connection failed")):
            from config.database_init import database_exists
            assert database_exists("robolearn") is False


# ===================================================================
# create_database
# ===================================================================

class TestCreateDatabase:

    def test_creates_successfully(self, mock_psycopg2, mock_conn):
        mock_conn.autocommit = None
        from config.database_init import create_database
        assert create_database("robolearn") is True

    def test_already_exists(self, mock_psycopg2, mock_conn):
        from psycopg2 import Error as Psycopg2Error
        error = Psycopg2Error()
        error.args = ('already exists',)
        mock_conn.cursor.return_value.execute.side_effect = error
        from config.database_init import create_database
        assert create_database("robolearn") is True

    def test_create_fails(self, mock_conn):
        with patch('config.database_init.psycopg2.connect', side_effect=Exception("no postgres")):
            from config.database_init import create_database
            assert create_database("robolearn") is False

    def test_create_unexpected_error_returns_false(self, mock_psycopg2, mock_conn):
        from psycopg2 import Error as Psycopg2Error
        error = Psycopg2Error()
        error.args = ('permission denied',)
        mock_conn.cursor.return_value.execute.side_effect = error
        from config.database_init import create_database
        assert create_database("robolearn") is False


# ===================================================================
# table_exists
# ===================================================================

class TestTableExists:

    def test_exists(self, mock_psycopg2, mock_conn):
        mock_conn.cursor.return_value.fetchone.return_value = (1,)
        from config.database_init import table_exists
        assert table_exists(mock_conn.cursor.return_value, "users") is True

    def test_not_exists(self, mock_psycopg2, mock_conn):
        mock_conn.cursor.return_value.fetchone.return_value = None
        from config.database_init import table_exists
        assert table_exists(mock_conn.cursor.return_value, "users") is False

    def test_exception_returns_false(self, mock_psycopg2, mock_conn):
        mock_conn.cursor.return_value.execute.side_effect = Exception("error")
        from config.database_init import table_exists
        assert table_exists(mock_conn.cursor.return_value, "users") is False


# ===================================================================
# execute_sql_file
# ===================================================================

class TestExecuteSQLFile:

    def test_executes_successfully(self, mock_psycopg2, mock_conn, tmp_path):
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("CREATE TABLE test (id INT);\nINSERT INTO test VALUES (1);")
        from config.database_init import execute_sql_file
        assert execute_sql_file(sql_file) is True

    def test_handles_sql_errors_gracefully(self, mock_psycopg2, mock_conn, tmp_path):
        from psycopg2 import Error as Psycopg2Error
        error = Psycopg2Error()
        error.args = ('relation "test" already exists',)
        mock_conn.cursor.return_value.execute.side_effect = error
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("CREATE TABLE test (id INT);")
        from config.database_init import execute_sql_file
        assert execute_sql_file(sql_file) is True

    def test_raises_on_fatal_error(self, mock_conn, tmp_path):
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("SELECT 1;")
        with patch('config.database_init.psycopg2.connect', side_effect=Exception("fatal error")):
            from config.database_init import execute_sql_file
            assert execute_sql_file(sql_file) is False

    def test_empty_statements_skipped(self, mock_psycopg2, mock_conn, tmp_path):
        sql_file = tmp_path / "empty.sql"
        sql_file.write_text(";;;")
        from config.database_init import execute_sql_file
        assert execute_sql_file(sql_file) is True


# ===================================================================
# data_exists
# ===================================================================

class TestDataExists:

    def test_has_data(self, mock_psycopg2, mock_conn):
        mock_conn.cursor.return_value.fetchone.return_value = (5,)
        from config.database_init import data_exists
        assert data_exists("users") is True

    def test_no_data(self, mock_psycopg2, mock_conn):
        mock_conn.cursor.return_value.fetchone.return_value = (0,)
        from config.database_init import data_exists
        assert data_exists("users") is False

    def test_exception_returns_false(self, mock_conn):
        with patch('config.database_init.psycopg2.connect', side_effect=Exception("no connection")):
            from config.database_init import data_exists
            assert data_exists("users") is False


# ===================================================================
# initialize_database - full integration scenario
# ===================================================================

class TestInitializeDatabase:

    @pytest.fixture
    def mock_all(self):
        """Mock psycopg2 and file system for initialize_database."""
        with patch('config.database_init.psycopg2.connect') as mock_connect:
            with patch('config.database_init.find_script') as mock_find:
                with patch('config.database_init.data_exists') as mock_data:
                    with patch('config.database_init.execute_sql_file') as mock_exec:
                        with patch('config.database_init.database_exists') as mock_db_exists:
                            with patch('config.database_init.create_database') as mock_create:
                                with patch('config.database_init._update_module_content_if_needed') as mock_update:
                                    with patch('builtins.open', new_callable=MagicMock) as mock_open:
                                        conn = MagicMock()
                                        cursor = MagicMock()
                                        conn.cursor.return_value = cursor
                                        mock_connect.return_value = conn
                                        mock_file = MagicMock()
                                        mock_file.read.return_value = "SELECT 1;"
                                        mock_open.return_value.__enter__.return_value = mock_file
                                        yield {
                                            "connect": mock_connect,
                                            "find": mock_find,
                                            "data_exists": mock_data,
                                            "execute_sql_file": mock_exec,
                                            "database_exists": mock_db_exists,
                                            "create_database": mock_create,
                                            "update": mock_update,
                                        }

    def test_initialize_full_success(self, mock_all):
        mock_all["database_exists"].return_value = True
        mock_all["find"].side_effect = lambda name: Path(name)
        mock_all["data_exists"].return_value = False
        mock_all["execute_sql_file"].return_value = True

        from config.database_init import initialize_database
        assert initialize_database() is True

    def test_initialize_database_not_exists(self, mock_all):
        mock_all["database_exists"].return_value = False
        mock_all["create_database"].return_value = True
        mock_all["find"].side_effect = lambda name: Path(name)
        mock_all["data_exists"].return_value = False
        mock_all["execute_sql_file"].return_value = True

        from config.database_init import initialize_database
        assert initialize_database() is True

    def test_initialize_create_database_fails(self, mock_all):
        mock_all["database_exists"].return_value = False
        mock_all["create_database"].return_value = False

        from config.database_init import initialize_database
        assert initialize_database() is False

    def test_initialize_schema_fails(self, mock_all):
        mock_all["database_exists"].return_value = True
        mock_all["find"].return_value = Path("001-init.sql")
        mock_all["connect"].side_effect = Exception("schema error")

        from config.database_init import initialize_database
        assert initialize_database() is False

    def test_initialize_seed_already_exists(self, mock_all):
        mock_all["database_exists"].return_value = True
        mock_all["find"].side_effect = lambda name: Path(name) if name != "003-seed-massive.sql" else None
        mock_all["data_exists"].return_value = True
        mock_all["connect"].return_value = MagicMock()

        from config.database_init import initialize_database
        assert initialize_database() is True

    def test_initialize_script_not_found(self, mock_all):
        mock_all["database_exists"].return_value = True
        mock_all["find"].return_value = None

        from config.database_init import initialize_database
        assert initialize_database() is True

    def test_initialize_seed_exception(self, mock_all):
        mock_all["database_exists"].return_value = True
        def find_side(name):
            if name == "001-init.sql":
                return Path(name)
            return None
        mock_all["find"].side_effect = find_side
        mock_all["data_exists"].return_value = False
        mock_all["connect"].return_value = MagicMock()
        mock_all["execute_sql_file"].return_value = True

        from config.database_init import initialize_database
        assert initialize_database() is True


# ===================================================================
# _update_module_content_if_needed
# ===================================================================

class TestUpdateModuleContent:

    def test_update_with_content(self, mock_psycopg2, mock_conn):
        cursor = mock_conn.cursor.return_value
        cursor.fetchall.return_value = [
            (1, "Introducción a Python", ""),
            (2, "Variables y Tipos de Datos", None),
        ]
        from config.database_init import _update_module_content_if_needed
        _update_module_content_if_needed()
        assert cursor.execute.call_count >= 3

    def test_update_no_modules(self, mock_psycopg2, mock_conn):
        cursor = mock_conn.cursor.return_value
        cursor.fetchall.return_value = []
        from config.database_init import _update_module_content_if_needed
        _update_module_content_if_needed()

    def test_update_unknown_title(self, mock_psycopg2, mock_conn):
        cursor = mock_conn.cursor.return_value
        cursor.fetchall.return_value = [
            (1, "Unknown Title", ""),
        ]
        from config.database_init import _update_module_content_if_needed
        _update_module_content_if_needed()
