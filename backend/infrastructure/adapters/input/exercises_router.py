from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timezone, timedelta

from app.schemas.exercises import ExecuteRequest, ExerciseSubmit
from app.schemas.common import TokenData
from app.dependencies import (
    sandbox_service, event_repository, PostgresConnection,
    verify_token, verify_teacher, check_and_award_achievements,
    rate_limiter, behavioral_repo, student_predictor, intelligent_tutor,
    ai_tutor_service, exercise_generator_service, rag_service, ai_service,
    verify_admin, module_repository,
)
from app.logging_config import logger

router = APIRouter(tags=["Exercises"])


@router.post("/api/exercises/submit")
async def submit_exercise(request: ExerciseSubmit, token_data: TokenData = Depends(verify_token)):
    """Submit and grade an exercise solution"""
    student_id = token_data.user_id
    if request.is_class_exercise:
        return await _submit_class_exercise(request, student_id)

    query = "SELECT id, module_id, solution_output, solution_type, test_code, title, points, lesson_id FROM exercises WHERE id = %s"
    exercise = None
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (request.exercise_id,))
        row = cursor.fetchone()
        if row:
            exercise = {"id": row[0], "module_id": row[1], "solution_output": row[2],
                        "solution_type": row[3] or "output", "test_code": row[4],
                        "title": row[5], "points": row[6], "lesson_id": row[7]}
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    attempt_query = "SELECT attempt_count, passed FROM exercise_attempts WHERE student_id = %s AND exercise_id = %s ORDER BY submitted_at DESC LIMIT 1"
    prev_attempts = 0
    already_passed = False
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(attempt_query, (student_id, request.exercise_id))
        row = cursor.fetchone()
        if row:
            prev_attempts = row[0] or 0
            already_passed = row[1]
    if already_passed:
        return {"success": True, "passed": True, "message": "You already solved this exercise", "attempts": prev_attempts}

    grading_result = await sandbox_service.execute_and_compare(
        code=request.code, expected_output=exercise["solution_output"],
        solution_type=exercise["solution_type"], test_code=exercise["test_code"],
    )
    passed = grading_result["passed"]
    score = grading_result["score"]
    error = grading_result.get("error")

    insert_query = """INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count)
        SELECT %s, %s, %s, %s, COALESCE(MAX(attempt_count), 0) + 1
        FROM exercise_attempts WHERE student_id = %s AND exercise_id = %s
        ON CONFLICT (student_id, exercise_id, attempt_count) DO NOTHING RETURNING attempt_count"""
    attempt_count = 1
    for _ in range(3):
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(insert_query, (student_id, request.exercise_id, passed, score, student_id, request.exercise_id))
            result = cursor.fetchone()
            if result:
                attempt_count = result[0]
                break

    if passed:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s", (exercise["points"], student_id))
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO progress (student_id, module_id, completed_exercises, total_exercises, points_earned, percentage, last_activity)
                VALUES (%s, %s, 1, (SELECT COUNT(*) FROM exercises WHERE module_id = %s), %s,
                    (SELECT ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM exercises WHERE module_id = %s) * 100, 2)
                     FROM exercise_attempts WHERE student_id = %s AND exercise_id IN (SELECT id FROM exercises WHERE module_id = %s) AND passed = TRUE), NOW())
                ON CONFLICT (student_id, module_id) DO UPDATE SET
                    completed_exercises = (SELECT COUNT(*) FROM exercise_attempts WHERE student_id = %s AND exercise_id IN (SELECT id FROM exercises WHERE module_id = %s) AND passed = TRUE),
                    points_earned = progress.points_earned + %s,
                    percentage = (SELECT ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM exercises WHERE module_id = %s) * 100, 2)
                                  FROM exercise_attempts WHERE student_id = %s AND exercise_id IN (SELECT id FROM exercises WHERE module_id = %s) AND passed = TRUE),
                    last_activity = NOW()
            """, (student_id, request.module_id, request.module_id, exercise["points"],
                  request.module_id, student_id, request.module_id,
                  student_id, request.module_id, exercise["points"],
                  request.module_id, student_id, request.module_id))
        lesson_id = exercise.get("lesson_id")
        if lesson_id:
            with PostgresConnection.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM exercises WHERE lesson_id = %s", (lesson_id,))
                total_in_lesson = cursor.fetchone()[0] or 0
                cursor.execute("""SELECT COUNT(*) FROM exercise_attempts ea JOIN exercises e ON e.id = ea.exercise_id
                    WHERE e.lesson_id = %s AND ea.student_id = %s AND ea.passed = TRUE""", (lesson_id, student_id))
                passed_in_lesson = cursor.fetchone()[0] or 0
            if total_in_lesson > 0 and passed_in_lesson >= total_in_lesson:
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("INSERT INTO lesson_completions (student_id, lesson_id, module_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (student_id, lesson_id, request.module_id))
        await check_and_award_achievements(student_id)
        await event_repository.log_event("exercise_passed", student_id, {"exercise_id": request.exercise_id, "module_id": request.module_id, "attempts": attempt_count, "points_earned": exercise["points"]})

    can_view_solution = attempt_count >= 3 and not passed
    solution = exercise.get("solution_output", "").replace("\\n", "\n") if (can_view_solution or passed) else None
    return {"success": True, "passed": passed, "score": score, "error": error, "attempts": attempt_count,
            "can_view_solution": can_view_solution, "solution": solution, "points_earned": exercise["points"] if passed else 0}


async def _submit_class_exercise(request: ExerciseSubmit, student_id: int):
    """Submit and grade a class exercise solution"""
    module_id = request.class_module_id or request.module_id
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""SELECT ce.id, ce.solution_output, ce.solution_type, ce.test_code, ce.title, ce.points
            FROM class_exercises ce WHERE ce.id = %s AND ce.class_module_id = %s""", (request.exercise_id, module_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Class exercise not found")
        exercise = {"id": row[0], "solution_output": row[1], "solution_type": row[2] or "output", "test_code": row[3], "title": row[4], "points": row[5] or 10}
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT attempt_count, passed FROM class_exercise_attempts WHERE student_id = %s AND class_exercise_id = %s ORDER BY submitted_at DESC LIMIT 1", (student_id, request.exercise_id))
        row = cursor.fetchone()
    prev_attempts = row[0] if row else 0
    already_passed = row[1] if row else False
    if already_passed:
        return {"success": True, "passed": True, "message": "You already solved this exercise", "attempts": prev_attempts}
    grading_result = await sandbox_service.execute_and_compare(
        code=request.code, expected_output=exercise["solution_output"],
        solution_type=exercise["solution_type"], test_code=exercise["test_code"],
    )
    passed = grading_result["passed"]
    score = grading_result["score"]
    error = grading_result.get("error")
    insert_query = """INSERT INTO class_exercise_attempts (student_id, class_exercise_id, class_module_id, passed, score, attempt_count)
        SELECT %s, %s, %s, %s, %s, COALESCE(MAX(attempt_count), 0) + 1
        FROM class_exercise_attempts WHERE student_id = %s AND class_exercise_id = %s
        ON CONFLICT (student_id, class_exercise_id, attempt_count) DO NOTHING RETURNING attempt_count"""
    attempt_count = 1
    for _ in range(3):
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(insert_query, (student_id, request.exercise_id, module_id, passed, score, student_id, request.exercise_id))
            result = cursor.fetchone()
            if result:
                attempt_count = result[0]
                break
    if passed:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s", (exercise["points"], student_id))
        await check_and_award_achievements(student_id)
        await event_repository.log_event("exercise_passed", student_id, {"exercise_id": request.exercise_id, "module_id": module_id, "attempts": attempt_count, "points_earned": exercise["points"], "is_class_exercise": True})
    can_view_solution = attempt_count >= 3 and not passed
    solution = exercise.get("solution_output", "").replace("\\n", "\n") if (can_view_solution or passed) else None
    return {"success": True, "passed": passed, "score": score, "error": error, "attempts": attempt_count,
            "can_view_solution": can_view_solution, "solution": solution, "points_earned": exercise["points"] if passed else 0}


@router.get("/api/exercises/{exercise_id}/attempts")
async def get_exercise_attempts(exercise_id: int, token_data: TokenData = Depends(verify_token)):
    """Get attempt history for an exercise"""
    query = "SELECT attempt_count, passed, score, submitted_at FROM exercise_attempts WHERE student_id = %s AND exercise_id = %s ORDER BY submitted_at DESC"
    attempts = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, exercise_id))
        for row in cursor.fetchall():
            attempts.append({"attempt": row[0], "passed": row[1], "score": row[2], "submitted_at": row[3].isoformat() if row[3] else None})
    total_attempts = len(attempts)
    last_passed = any(a["passed"] for a in attempts)
    can_view = total_attempts >= 3 and not last_passed
    solution = None
    if can_view or last_passed:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT solution_output FROM exercises WHERE id = %s", (exercise_id,))
            row = cursor.fetchone()
            if row:
                solution = row[0]
    return {"success": True, "attempts": attempts, "total_attempts": total_attempts, "can_view_solution": can_view, "already_passed": last_passed, "solution": solution}


@router.get("/api/exercises/difficulty-analysis")
async def get_exercise_difficulty_analysis(token_data: TokenData = Depends(verify_teacher)):
    """Analyze exercise difficulty across students"""
    query = """SELECT e.id, e.title, e.difficulty as current_difficulty, e.points, e.module_id, m.title as module_title,
        COUNT(ea.id) as total_attempts, COALESCE(AVG(ea.score), 0) as avg_score,
        COUNT(CASE WHEN ea.passed = TRUE THEN 1 END) as passed_count, COUNT(DISTINCT ea.student_id) as unique_students
        FROM exercises e JOIN modules m ON e.module_id = m.id LEFT JOIN exercise_attempts ea ON e.id = ea.exercise_id
        WHERE m.teacher_id = %s OR %s IN (SELECT id FROM users WHERE role = 'admin')
        GROUP BY e.id, e.title, e.difficulty, e.points, e.module_id, m.title
        HAVING COUNT(ea.id) > 0 ORDER BY CAST(AVG(ea.score) AS DECIMAL) ASC"""
    suggestions = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, token_data.user_id))
        for row in cursor.fetchall():
            ex_id, title, current_diff, points, module_id, module_title = row[0], row[1], row[2], row[3], row[4], row[5]
            total_attempts = row[6] or 0
            avg_score = float(row[7] or 0)
            passed_count = row[8] or 0
            pass_rate = (passed_count / total_attempts * 100) if total_attempts > 0 else 0
            suggestion = None
            suggested_diff = current_diff
            if pass_rate < 30 and current_diff > 1:
                suggestion = {"type": "too_hard", "message": f"Very hard: only {round(pass_rate)}% pass rate. Consider lowering difficulty.", "alternative": "Add a guided version."}
                suggested_diff = max(1, current_diff - 1)
            elif pass_rate > 85 and current_diff < 5:
                suggestion = {"type": "too_easy", "message": f"Very easy: {round(pass_rate)}% pass rate. Consider raising difficulty.", "alternative": "Add variants requiring more complex logic."}
                suggested_diff = min(5, current_diff + 1)
            elif avg_score < 50 and unique_students >= 3:
                suggestion = {"type": "needs_review", "message": f"Students struggle (avg {round(avg_score)}%). Review the statement.", "alternative": "Add an intermediate exercise."}
            if suggestion:
                suggestions.append({"exercise_id": ex_id, "title": title, "module_title": module_title, "module_id": module_id,
                                    "current_difficulty": current_diff, "suggested_difficulty": suggested_diff,
                                    "pass_rate": round(pass_rate, 1), "avg_score": round(avg_score, 1),
                                    "total_attempts": total_attempts, "unique_students": unique_students, **suggestion})
    return {"success": True, "suggestions": suggestions}


@router.get("/api/exercises")
async def get_all_exercises():
    """List all published exercises"""
    query = """SELECT e.id, e.module_id, e.title, e.description, e.instructions, e.difficulty, e.points, m.title as module_title
        FROM exercises e JOIN modules m ON e.module_id = m.id
        WHERE m.is_published = TRUE ORDER BY m."order", e."order" ASC"""
    exercises = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            exercises.append({"id": row[0], "module_id": row[1], "title": row[2], "description": row[3],
                              "instructions": row[4], "difficulty": row[5], "points": row[6], "module_title": row[7]})
    return {"success": True, "exercises": exercises}


# ---- Code Execution ----

_EXEC_TIMEOUT = 10
_executor = None


def _get_executor():
    global _executor
    if _executor is None:
        import concurrent.futures
        _executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    return _executor


def _build_safe_env():
    actions = []
    def jump(): actions.append("jump")
    def forward(steps=1): actions.append(f"forward_{steps}")
    safe_builtins = {
        'print': print, 'len': len, 'range': range, 'int': int, 'float': float,
        'str': str, 'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple,
        'set': set, 'True': True, 'False': False, 'None': None,
        'abs': abs, 'max': max, 'min': min, 'sum': sum, 'sorted': sorted,
        'reversed': reversed, 'enumerate': enumerate, 'zip': zip, 'map': map,
        'filter': filter, 'all': all, 'any': any, 'round': round,
        'isinstance': isinstance,
        'ValueError': ValueError, 'TypeError': TypeError, 'KeyError': KeyError,
        'IndexError': IndexError, 'StopIteration': StopIteration,
        'Exception': Exception,
    }
    env = {"jump": jump, "forward": forward, "__builtins__": safe_builtins}
    return env, actions


def _execute_sync(code: str, env: dict, actions: list) -> dict:
    import io, sys, ast
    from contextlib import redirect_stdout
    f = io.StringIO()
    error = None
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {"success": False, "output": "", "actions": [], "error": f"Syntax Error: {e}"}
    try:
        with redirect_stdout(f):
            exec(code, env)
    except Exception as e:
        error = str(e)
    return {"success": error is None, "output": f.getvalue(), "actions": list(actions), "error": error}


DANGEROUS_PATTERNS = [
    "__import__", "eval(", "exec(", "open(",
    "__builtins__", "__class__", "__bases__", "__subclasses__",
    "__mro__", "__globals__", "__code__", "__reduce__",
    "__subclasshook__", "__init_subclass__",
    "__dir__", "__getattribute__", "__setattr__",
]
DANGEROUS_IMPORTS = [
    "import os", "import subprocess", "import shutil",
    "import sys", "import socket", "import requests",
    "import ctypes", "import multiprocessing",
    "import http", "import urllib", "import ftplib",
    "import telnetlib", "import poplib", "import smtplib",
    "from os", "from subprocess", "from shutil", "from sys",
    "from socket", "from requests", "from ctypes",
]


@router.post("/api/execute-code")
async def execute_code(request: ExecuteRequest, http_request: Request, token_data: TokenData = Depends(verify_token)):
    """Execute code in a sandboxed environment"""
    await rate_limiter.check_by_user(token_data.user_id, "execute", max_requests=30, window_seconds=60)
    if len(request.code) > 10000:
        return {"success": False, "output": "", "actions": [], "error": "Code exceeds maximum length of 10000 characters"}
    code_lower = request.code.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in code_lower or pattern in request.code:
            return {"success": False, "output": "", "actions": [], "error": f"Security: pattern '{pattern}' is not allowed"}
    for pattern in DANGEROUS_IMPORTS:
        if pattern in code_lower or pattern in request.code:
            return {"success": False, "output": "", "actions": [], "error": f"Security: pattern '{pattern}' is not allowed"}
    import ast
    try:
        ast.parse(request.code)
    except SyntaxError as e:
        return {"success": False, "output": "", "actions": [], "error": f"Syntax Error: {e}"}
    env, actions = _build_safe_env()
    import asyncio
    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                _get_executor(), _execute_sync, request.code, env, actions
            ),
            timeout=_EXEC_TIMEOUT,
        )
        return result
    except asyncio.TimeoutError:
        return {"success": False, "output": "", "actions": [], "error": f"Execution timeout (max {_EXEC_TIMEOUT}s)"}


# ---- Lessons ----

@router.post("/api/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: int, token_data: TokenData = Depends(verify_token)):
    """Mark a lesson as completed"""
    student_id = token_data.user_id
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT module_id FROM lessons WHERE id = %s", (lesson_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Lesson not found")
        module_id = row[0]
        cursor.execute("INSERT INTO lesson_completions (student_id, lesson_id, module_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (student_id, lesson_id, module_id))
    return {"success": True, "message": "Lesson completed"}


