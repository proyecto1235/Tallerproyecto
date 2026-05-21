from typing import List, Dict, Any, Optional
from infrastructure.adapters.output.postgres.connection import PostgresConnection


class ProcedureRunner:
    """
    Ejecuta funciones y procedimientos almacenados PostgreSQL.
    Todas las consultas usan parámetros con %s para evitar inyección SQL.
    """

    @staticmethod
    def call_function(func_name: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        placeholders = ", ".join(f"%s" for _ in (params or []))
        query = f"SELECT * FROM {func_name}({placeholders})"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, params or [])
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def execute_procedure(proc_name: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        placeholders = ", ".join(f"%s" for _ in (params or []))
        query = f"SELECT * FROM {proc_name}({placeholders})"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, params or [])
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []

    @staticmethod
    def execute_function_single(func_name: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        results = ProcedureRunner.call_function(func_name, params)
        return results[0] if results else None

    @staticmethod
    def get_student_progress_summary(student_id: int) -> Optional[Dict[str, Any]]:
        return ProcedureRunner.execute_function_single(
            "fn_get_student_progress_summary", [student_id]
        )

    @staticmethod
    def get_teacher_dashboard(teacher_id: int) -> Optional[Dict[str, Any]]:
        return ProcedureRunner.execute_function_single(
            "fn_get_teacher_dashboard", [teacher_id]
        )

    @staticmethod
    def get_admin_stats() -> Optional[Dict[str, Any]]:
        return ProcedureRunner.execute_function_single("fn_get_admin_stats", [])

    @staticmethod
    def get_admin_modules(status_filter: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        return ProcedureRunner.call_function(
            "fn_get_admin_modules", [status_filter, search]
        )

    @staticmethod
    def get_module_detail_for_admin(module_id: int) -> Optional[Dict[str, Any]]:
        return ProcedureRunner.execute_function_single(
            "fn_get_module_detail_for_admin", [module_id]
        )

    @staticmethod
    def get_student_performance_distribution(teacher_id: int) -> List[Dict[str, Any]]:
        return ProcedureRunner.call_function(
            "fn_get_student_performance_distribution", [teacher_id]
        )

    @staticmethod
    def get_weekly_activity(teacher_id: int) -> List[Dict[str, Any]]:
        return ProcedureRunner.call_function(
            "fn_get_weekly_activity", [teacher_id]
        )

    @staticmethod
    def get_student_alerts(teacher_id: int) -> List[Dict[str, Any]]:
        return ProcedureRunner.call_function(
            "fn_get_student_alerts", [teacher_id]
        )

    @staticmethod
    def search_users(search: Optional[str] = None, role: Optional[str] = None,
                     limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return ProcedureRunner.call_function(
            "fn_search_users", [search, role, limit, offset]
        )

    @staticmethod
    def upsert_progress(student_id: int, module_id: int, points_earned: int = 0) -> Optional[Dict[str, Any]]:
        return ProcedureRunner.execute_function_single(
            "sp_upsert_progress", [student_id, module_id, points_earned]
        )

    @staticmethod
    def record_exercise_attempt(student_id: int, exercise_id: int,
                                 passed: bool, score: float, points_awarded: int = 0) -> Optional[Dict[str, Any]]:
        return ProcedureRunner.execute_function_single(
            "sp_record_exercise_attempt",
            [student_id, exercise_id, passed, score, points_awarded],
        )

    @staticmethod
    def enroll_student(student_id: int, module_id: int) -> Optional[Dict[str, Any]]:
        return ProcedureRunner.execute_function_single(
            "sp_enroll_student", [student_id, module_id]
        )

    @staticmethod
    def award_points(user_id: int, points: int, reason: Optional[str] = None) -> Optional[int]:
        result = ProcedureRunner.execute_function_single(
            "sp_award_points", [user_id, points, reason]
        )
        return result.get("sp_award_points") if result else None

    @staticmethod
    def check_and_award_achievements(user_id: int) -> List[Dict[str, Any]]:
        return ProcedureRunner.call_function(
            "sp_check_and_award_achievements", [user_id]
        )
