from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta

from app.schemas.common import TokenData
from app.dependencies import (
    PostgresConnection, verify_token, verify_teacher, verify_admin,
    event_repository, behavioral_repo, student_predictor,
)
from app.logging_config import logger

router = APIRouter(tags=["Dashboard"])


@router.get("/api/dashboard/student")
async def student_dashboard(token_data: TokenData = Depends(verify_token)):
    """Get student dashboard with progress summary"""
    user_id = token_data.user_id

    progress_query = """SELECT COALESCE(SUM(p.completed_exercises), 0), COALESCE(SUM(p.total_exercises), 0)
        FROM progress p WHERE p.student_id = %s"""
    total_completed = 0
    total_exercises = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(progress_query, (user_id,))
        row = cursor.fetchone()
        total_completed = row[0] or 0
        total_exercises = row[1] or 0

    points_query = "SELECT points FROM users WHERE id = %s"
    points = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(points_query, (user_id,))
        row = cursor.fetchone()
        points = row[0] or 0

    streak_query = """SELECT COUNT(DISTINCT DATE(submitted_at)) FROM exercise_attempts
        WHERE student_id = %s AND submitted_at >= NOW() - INTERVAL '7 days'"""
    active_days_7 = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(streak_query, (user_id,))
        row = cursor.fetchone()
        active_days_7 = row[0] or 0

    recent_query = """SELECT e.title, e.points, ea.passed, ea.score, ea.submitted_at
        FROM exercise_attempts ea JOIN exercises e ON ea.exercise_id = e.id
        WHERE ea.student_id = %s ORDER BY ea.submitted_at DESC LIMIT 5"""
    recent_attempts = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(recent_query, (user_id,))
        for row in cursor.fetchall():
            recent_attempts.append({"title": row[0], "points": row[1], "passed": row[2],
                                   "score": float(row[3]) if row[3] else 0, "submitted_at": row[4].isoformat() if row[4] else None})

    modules_progress = []
    mod_query = """SELECT m.id, m.title, COALESCE(p.percentage, 0), COALESCE(p.completed_exercises, 0),
        COALESCE(p.total_exercises, 0), COALESCE(p.points_earned, 0)
        FROM modules m LEFT JOIN progress p ON p.module_id = m.id AND p.student_id = %s
        WHERE m.is_published = TRUE ORDER BY m.order ASC"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(mod_query, (user_id,))
        for row in cursor.fetchall():
            modules_progress.append({"module_id": row[0], "title": row[1], "progress": float(row[2]),
                                    "completed": row[3], "total": row[4], "points_earned": row[5]})

    challenges_query = """SELECT COUNT(*), COUNT(CASE WHEN ca.passed THEN 1 END)
        FROM challenge_attempts ca WHERE ca.student_id = %s"""
    total_challenges = 0
    passed_challenges = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(challenges_query, (user_id,))
        row = cursor.fetchone()
        total_challenges = row[0] or 0
        passed_challenges = row[1] or 0

    return {"success": True, "dashboard": {
        "total_points": points, "total_completed_exercises": total_completed,
        "total_exercises": total_exercises, "active_days_last_7": active_days_7,
        "recent_attempts": recent_attempts, "modules_progress": modules_progress,
        "total_attempted_challenges": total_challenges, "passed_challenges": passed_challenges,
    }}


@router.get("/api/dashboard/teacher")
async def teacher_dashboard(token_data: TokenData = Depends(verify_token)):
    """Get teacher dashboard with class overview"""
    user_id = token_data.user_id

    students_query = """SELECT COUNT(DISTINCT cs.student_id) FROM class_students cs
        JOIN classes c ON cs.class_id = c.id WHERE c.teacher_id = %s"""
    total_students = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(students_query, (user_id,))
        row = cursor.fetchone()
        total_students = row[0] or 0

    modules_count = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM modules WHERE teacher_id = %s", (user_id,))
        row = cursor.fetchone()
        modules_count = row[0] or 0

    avg_progress = 0.0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""SELECT COALESCE(AVG(p.percentage), 0) FROM progress p
            JOIN modules m ON p.module_id = m.id WHERE m.teacher_id = %s""", (user_id,))
        row = cursor.fetchone()
        avg_progress = float(row[0]) if row and row[0] else 0.0

    recent_submissions = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""SELECT u.full_name, e.title, ea.passed, ea.score, ea.submitted_at
            FROM exercise_attempts ea JOIN exercises e ON ea.exercise_id = e.id
            JOIN users u ON ea.student_id = u.id
            JOIN modules m ON e.module_id = m.id WHERE m.teacher_id = %s
            ORDER BY ea.submitted_at DESC LIMIT 10""", (user_id,))
        for row in cursor.fetchall():
            recent_submissions.append({"student": row[0], "exercise": row[1], "passed": row[2],
                                       "score": float(row[3]) if row[3] else 0, "submitted_at": row[4].isoformat() if row[4] else None})

    return {"success": True, "dashboard": {
        "total_students": total_students, "total_modules": modules_count,
        "average_student_progress": round(avg_progress, 1), "recent_submissions": recent_submissions,
    }}


