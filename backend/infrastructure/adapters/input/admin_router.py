from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime

from app.schemas.common import TokenData
from app.dependencies import (
    PostgresConnection, verify_admin, event_repository,
)
from app.logging_config import logger

router = APIRouter(tags=["Admin"])


@router.get("/api/admin/users")
async def admin_list_users(token_data: TokenData = Depends(verify_admin)):
    """List all users"""
    query = "SELECT id, full_name, email, role, is_active, public_id, points, created_at FROM users ORDER BY created_at DESC"
    users = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            users.append({"id": row[0], "full_name": row[1], "email": row[2], "role": row[3], "is_active": row[4],
                         "public_id": row[5], "points": row[6] or 0, "created_at": row[7].isoformat() if row[7] else None})
    return {"success": True, "users": users}


@router.put("/api/admin/users/{user_id}/role")
async def admin_change_role(user_id: int, request: Request, token_data: TokenData = Depends(verify_admin)):
    """Change a user's role"""
    body = await request.json()
    new_role = body.get("role")
    if new_role not in ("student", "teacher", "admin"):
        raise HTTPException(status_code=400, detail="Invalid role")
    query = "UPDATE users SET role = %s WHERE id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (new_role, user_id))
    await event_repository.log_event("user_role_changed", token_data.user_id, {"target_user": user_id, "new_role": new_role})
    return {"success": True, "message": "Role updated"}


@router.get("/api/admin/teachers/pending")
async def admin_pending_teachers(token_data: TokenData = Depends(verify_admin)):
    """List pending teacher approvals"""
    query = "SELECT id, full_name, email, created_at FROM users WHERE role = 'teacher' AND is_active = FALSE ORDER BY created_at ASC"
    teachers = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            teachers.append({"id": row[0], "full_name": row[1], "email": row[2], "created_at": row[3].isoformat() if row[3] else None})
    return {"success": True, "teachers": teachers}


@router.post("/api/admin/teachers/approve/{user_id}")
async def admin_approve_teacher(user_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve a pending teacher"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE users SET is_active = TRUE WHERE id = %s AND role = 'teacher'", (user_id,))
    await event_repository.log_event("teacher_approved", token_data.user_id, {"target_user": user_id})
    return {"success": True, "message": "Teacher approved"}


@router.post("/api/admin/teachers/reject/{user_id}")
async def admin_reject_teacher(user_id: int, token_data: TokenData = Depends(verify_admin)):
    """Reject a pending teacher"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s AND role = 'teacher' AND is_active = FALSE", (user_id,))
    await event_repository.log_event("teacher_rejected", token_data.user_id, {"target_user": user_id})
    return {"success": True, "message": "Teacher rejected"}


@router.post("/api/admin/modules/{module_id}/approve-deletion")
async def admin_approve_deletion(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve module deletion request"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE modules SET deletion_requested = FALSE, is_published = FALSE WHERE id = %s", (module_id,))
    await event_repository.log_event("module_deletion_approved", token_data.user_id, {"module_id": module_id})
    return {"success": True, "message": "Deletion approved"}


@router.post("/api/admin/modules/{module_id}/reject-deletion")
async def admin_reject_deletion(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Reject module deletion request"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE modules SET deletion_requested = FALSE WHERE id = %s", (module_id,))
    await event_repository.log_event("module_deletion_rejected", token_data.user_id, {"module_id": module_id})
    return {"success": True, "message": "Deletion rejected"}


@router.get("/api/dashboard/admin")
async def admin_dashboard(token_data: TokenData = Depends(verify_admin)):
    """Get admin dashboard statistics"""
    stats = {}
    queries = {
        "total_users": "SELECT COUNT(*) FROM users",
        "total_teachers": "SELECT COUNT(*) FROM users WHERE role = 'teacher'",
        "total_students": "SELECT COUNT(*) FROM users WHERE role = 'student'",
        "total_modules": "SELECT COUNT(*) FROM modules",
        "total_exercises": "SELECT COUNT(*) FROM exercises",
        "total_challenges": "SELECT COUNT(*) FROM challenges",
        "total_classes": "SELECT COUNT(*) FROM classes",
        "pending_teachers": "SELECT COUNT(*) FROM users WHERE role = 'teacher' AND is_active = FALSE",
        "pending_deletions": "SELECT COUNT(*) FROM modules WHERE deletion_requested = TRUE",
        "total_attempts": "SELECT COUNT(*) FROM exercise_attempts",
    }
    with PostgresConnection.get_cursor() as cursor:
        for key, q in queries.items():
            cursor.execute(q)
            row = cursor.fetchone()
            stats[key] = row[0] if row else 0
    return {"success": True, "stats": stats}


@router.get("/api/admin/audit-logs")
async def admin_audit_logs(token_data: TokenData = Depends(verify_admin)):
    """Get audit log entries"""
    query = """SELECT id, user_id, event_type, metadata, created_at FROM events
        ORDER BY created_at DESC LIMIT 200"""
    logs = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            logs.append({"id": row[0], "user_id": row[1], "event_type": row[2],
                        "metadata": row[3], "created_at": row[4].isoformat() if row[4] else None})
    return {"success": True, "logs": logs}


@router.get("/api/admin/modules")
async def admin_modules(token_data: TokenData = Depends(verify_admin)):
    """List all modules for moderation"""
    query = """SELECT m.id, m.title, m.description, m.difficulty, m.is_published, m.deletion_requested,
        u.full_name as teacher_name, m.created_at FROM modules m JOIN users u ON m.teacher_id = u.id
        ORDER BY m.created_at DESC"""
    modules = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            modules.append({"id": row[0], "title": row[1], "description": row[2], "difficulty": row[3],
                           "is_published": row[4], "deletion_requested": row[5], "teacher_name": row[6],
                           "created_at": row[7].isoformat() if row[7] else None})
    return {"success": True, "modules": modules}


@router.get("/api/admin/modules/{module_id}")
async def admin_module_detail(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Get module details with exercises"""
    query = """SELECT m.id, m.title, m.description, m.difficulty, m.is_published, m.deletion_requested,
        m.teacher_id, u.full_name as teacher_name, m.created_at, m.updated_at
        FROM modules m JOIN users u ON m.teacher_id = u.id WHERE m.id = %s"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Module not found")
    exercises = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT id, title, difficulty, points FROM exercises WHERE module_id = %s ORDER BY id", (module_id,))
        for erow in cursor.fetchall():
            exercises.append({"id": erow[0], "title": erow[1], "difficulty": erow[2], "points": erow[3]})
    return {"success": True, "module": {
        "id": row[0], "title": row[1], "description": row[2], "difficulty": row[3],
        "is_published": row[4], "deletion_requested": row[5], "teacher_id": row[6],
        "teacher_name": row[7], "created_at": row[8].isoformat() if row[8] else None,
        "updated_at": row[9].isoformat() if row[9] else None, "exercises": exercises
    }}


@router.post("/api/admin/modules/{module_id}/approve")
async def admin_approve_module(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve and publish a module"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE modules SET is_published = TRUE WHERE id = %s", (module_id,))
    await event_repository.log_event("module_approved", token_data.user_id, {"module_id": module_id})
    return {"success": True, "message": "Module approved and published"}


@router.post("/api/admin/modules/{module_id}/reject")
async def admin_reject_module(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Reject and unpublish a module"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE modules SET is_published = FALSE WHERE id = %s", (module_id,))
    await event_repository.log_event("module_rejected", token_data.user_id, {"module_id": module_id})
    return {"success": True, "message": "Module rejected"}


@router.put("/api/admin/modules/{module_id}/content")
async def admin_update_content(module_id: int, request: Request, token_data: TokenData = Depends(verify_admin)):
    """Update module content"""
    body = await request.json()
    fields = []
    values = []
    for field in ["title", "description", "difficulty", "content", "is_published"]:
        if field in body:
            fields.append(f"{field} = %s")
            values.append(body[field])
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(module_id)
    query = f"UPDATE modules SET {', '.join(fields)} WHERE id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(values))
    await event_repository.log_event("module_content_updated", token_data.user_id, {"module_id": module_id})
    return {"success": True, "message": "Module updated"}


@router.get("/api/admin/content-review")
async def admin_content_review(token_data: TokenData = Depends(verify_admin)):
    """List modules pending content review"""
    query = """SELECT m.id, m.title, m.description, m.difficulty, m.is_published, u.full_name,
        m.created_at, m.updated_at FROM modules m JOIN users u ON m.teacher_id = u.id
        ORDER BY m.updated_at DESC LIMIT 50"""
    modules = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            modules.append({"id": row[0], "title": row[1], "description": row[2], "difficulty": row[3],
                           "is_published": row[4], "teacher_name": row[5],
                           "created_at": row[6].isoformat() if row[6] else None,
                           "updated_at": row[7].isoformat() if row[7] else None})
    return {"success": True, "modules": modules}


