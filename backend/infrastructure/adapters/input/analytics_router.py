from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta

from app.schemas.analytics import DashboardResponse
from app.schemas.common import TokenData
from app.dependencies import (
    PostgresConnection, verify_token, verify_teacher, verify_admin,
    event_repository, behavioral_repo, student_predictor,
)
from app.logging_config import logger

router = APIRouter(tags=["Analytics"])


@router.get("/api/analytics/teacher-overview", response_model=DashboardResponse)
async def teacher_overview(token_data: TokenData = Depends(verify_teacher)):
    """Get teacher analytics overview"""
    query = """SELECT COUNT(DISTINCT s.id) FROM users s
        JOIN class_students cs ON s.id = cs.student_id JOIN classes c ON cs.class_id = c.id
        WHERE c.teacher_id = %s"""
    total_students = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id,))
        row = cursor.fetchone()
        total_students = row[0] or 0

    query2 = "SELECT COUNT(*) FROM modules WHERE teacher_id = %s"
    total_modules = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query2, (token_data.user_id,))
        row = cursor.fetchone()
        total_modules = row[0] or 0

    query3 = """SELECT COUNT(*) FROM challenges WHERE teacher_id = %s"""
    total_challenges = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query3, (token_data.user_id,))
        row = cursor.fetchone()
        total_challenges = row[0] or 0

    query4 = """SELECT COUNT(*) FROM class_students cs JOIN classes c ON cs.class_id = c.id
        WHERE c.teacher_id = %s AND cs.joined_at >= NOW() - INTERVAL '30 days'"""
    new_students_30d = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query4, (token_data.user_id,))
        row = cursor.fetchone()
        new_students_30d = row[0] or 0

    query5 = """SELECT COALESCE(AVG(p.percentage), 0) FROM progress p
        JOIN modules m ON p.module_id = m.id WHERE m.teacher_id = %s"""
    avg_progress = 0.0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query5, (token_data.user_id,))
        row = cursor.fetchone()
        avg_progress = float(row[0]) if row and row[0] else 0.0

    return {
        "success": True,
        "total_students": total_students,
        "total_modules": total_modules,
        "total_challenges": total_challenges,
        "new_students_30d": new_students_30d,
        "avg_student_progress": round(avg_progress, 1),
    }


@router.get("/api/analytics/admin-dashboard")
async def admin_dashboard(token_data: TokenData = Depends(verify_admin)):
    """Get admin dashboard statistics"""
    queries = {
        "total_users": "SELECT COUNT(*) FROM users",
        "total_teachers": "SELECT COUNT(*) FROM users WHERE role = 'teacher'",
        "total_students": "SELECT COUNT(*) FROM users WHERE role = 'student'",
        "total_modules": "SELECT COUNT(*) FROM modules",
        "total_exercises": "SELECT COUNT(*) FROM exercises",
        "total_challenges": "SELECT COUNT(*) FROM challenges",
        "total_classes": "SELECT COUNT(*) FROM classes",
        "total_submissions": "SELECT COUNT(*) FROM exercise_attempts",
        "total_points_awarded": "SELECT COALESCE(SUM(score), 0) FROM exercise_attempts WHERE passed = TRUE",
        "users_30d": "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '30 days'",
        "active_users_7d": """SELECT COUNT(DISTINCT student_id) FROM exercise_attempts WHERE submitted_at >= NOW() - INTERVAL '7 days'""",
    }
    stats = {}
    with PostgresConnection.get_cursor() as cursor:
        for key, q in queries.items():
            cursor.execute(q)
            row = cursor.fetchone()
            stats[key] = row[0] if row else 0
    return {"success": True, "stats": stats}


@router.get("/api/analytics/student-evolution")
async def student_evolution(student_id: int, days: int = 30, token_data: TokenData = Depends(verify_teacher)):
    """Get student performance evolution over time"""
    query = """SELECT DATE(submitted_at) as day, COUNT(*) as attempts,
        SUM(CASE WHEN passed THEN 1 ELSE 0 END) as passed, COALESCE(AVG(score), 0) as avg_score
        FROM exercise_attempts WHERE student_id = %s AND submitted_at >= CURRENT_DATE - %s::interval
        GROUP BY DATE(submitted_at) ORDER BY day ASC"""
    evolution = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (student_id, f"{days} days"))
        for row in cursor.fetchall():
            evolution.append({"date": row[0].isoformat(), "attempts": row[1], "passed": row[2], "avg_score": float(row[3])})
    return {"success": True, "evolution": evolution}


@router.get("/api/analytics/module-performance/{module_id}")
async def module_performance(module_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Get performance metrics for a module"""
    query = """SELECT e.id, e.title, COUNT(ea.id) as total_attempts,
        COALESCE(AVG(ea.score), 0) as avg_score,
        COUNT(CASE WHEN ea.passed THEN 1 END) as passed_count,
        COUNT(DISTINCT ea.student_id) as unique_students
        FROM exercises e LEFT JOIN exercise_attempts ea ON e.id = ea.exercise_id
        WHERE e.module_id = %s GROUP BY e.id, e.title ORDER BY e.id"""
    exercises = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id,))
        for row in cursor.fetchall():
            total = row[2] or 0
            passed = row[4] or 0
            pass_rate = round(passed / total * 100, 1) if total > 0 else 0
            exercises.append({"id": row[0], "title": row[1], "total_attempts": total,
                             "avg_score": round(float(row[3]), 1), "passed": passed,
                             "unique_students": row[5] or 0, "pass_rate": pass_rate})
    return {"success": True, "module_id": module_id, "exercises": exercises}


@router.get("/api/analytics/teacher/students")
async def teacher_students_list(token_data: TokenData = Depends(verify_teacher)):
    """List teacher's students with progress"""
    query = """SELECT u.id, u.full_name, u.email, u.public_id, u.points,
        STRING_AGG(DISTINCT c.name, ', ') as class_names,
        (SELECT COALESCE(AVG(p.percentage), 0) FROM progress p
         JOIN class_modules cm ON p.module_id = cm.module_id
         JOIN classes cl ON cm.class_id = cl.id
         WHERE cl.teacher_id = %s AND p.student_id = u.id) as avg_progress,
        (SELECT COALESCE(SUM(score), 0) FROM exercise_attempts WHERE student_id = u.id) as total_score
        FROM users u
        JOIN class_students cs ON u.id = cs.student_id
        JOIN classes c ON cs.class_id = c.id
        WHERE c.teacher_id = %s AND u.role = 'student'
        GROUP BY u.id, u.full_name, u.email, u.public_id, u.points
        ORDER BY u.full_name ASC"""
    students = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, token_data.user_id))
        for row in cursor.fetchall():
            students.append({"id": row[0], "full_name": row[1], "email": row[2], "public_id": row[3],
                            "points": row[4] or 0, "classes": row[5] or "",
                            "avg_progress": round(float(row[6]), 1) if row[6] else 0,
                            "total_score": row[7] or 0})
    return {"success": True, "students": students}


@router.get("/api/analytics/student-progress/{student_id}")
async def get_student_progress(student_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Get detailed progress for a specific student"""
    query = """SELECT m.id, m.title, COALESCE(p.percentage, 0) as progress,
        COALESCE(p.completed_exercises, 0) as completed, COALESCE(p.total_exercises, 0) as total,
        COALESCE(p.points_earned, 0) as points, p.last_activity
        FROM modules m LEFT JOIN progress p ON p.module_id = m.id AND p.student_id = %s
        WHERE m.teacher_id = %s ORDER BY m.id"""
    modules = []
    total_points = 0
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (student_id, token_data.user_id))
        for row in cursor.fetchall():
            modules.append({"module_id": row[0], "module_title": row[1], "progress": float(row[2]),
                           "completed": row[3], "total": row[4], "points_earned": row[5],
                           "last_activity": row[6].isoformat() if row[6] else None})
            total_points += row[5] or 0
    return {"success": True, "modules": modules, "total_points": total_points}


