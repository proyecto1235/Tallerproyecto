from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timezone

from app.schemas.classes import ClassCreate, ClassUpdate, ClassStudentAdd
from app.schemas.common import TokenData
from app.dependencies import (
    event_repository, PostgresConnection,
    verify_token, verify_teacher, verify_admin,
)
from app.logging_config import logger

router = APIRouter(tags=["Classes"])


@router.get("/api/classes")
async def list_classes(token_data: TokenData = Depends(verify_token)):
    """List classes for the current user"""
    role = token_data.role
    user_id = token_data.user_id
    if role == "admin":
        query = """SELECT c.id, c.name, c.description, c.invite_code, c.is_active, u.full_name as teacher_name,
            c.teacher_id, c.created_at, c.updated_at FROM classes c JOIN users u ON c.teacher_id = u.id ORDER BY c.created_at DESC"""
        params = ()
    elif role == "teacher":
        query = """SELECT c.id, c.name, c.description, c.invite_code, c.is_active, u.full_name as teacher_name,
            c.teacher_id, c.created_at, c.updated_at FROM classes c JOIN users u ON c.teacher_id = u.id
            WHERE c.teacher_id = %s ORDER BY c.created_at DESC"""
        params = (user_id,)
    else:
        query = """SELECT c.id, c.name, c.description, c.invite_code, c.is_active, u.full_name as teacher_name,
            c.teacher_id, c.created_at, c.updated_at FROM classes c JOIN users u ON c.teacher_id = u.id
            JOIN class_students cs ON cs.class_id = c.id WHERE cs.student_id = %s ORDER BY c.created_at DESC"""
        params = (user_id,)
    classes = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, params)
        for row in cursor.fetchall():
            classes.append({"id": row[0], "name": row[1], "description": row[2], "invite_code": row[3],
                           "is_active": row[4], "teacher_name": row[5], "teacher_id": row[6],
                           "created_at": row[7].isoformat() if row[7] else None,
                           "updated_at": row[8].isoformat() if row[8] else None})
    return {"success": True, "classes": classes}


@router.get("/api/classes/{class_id}")
async def get_class(class_id: int, token_data: TokenData = Depends(verify_token)):
    """Get details of a specific class"""
    query = """SELECT c.id, c.name, c.description, c.invite_code, c.is_active, c.teacher_id,
        u.full_name as teacher_name, c.created_at, c.updated_at FROM classes c JOIN users u ON c.teacher_id = u.id WHERE c.id = %s"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"success": True, "class": {
        "id": row[0], "name": row[1], "description": row[2], "invite_code": row[3],
        "is_active": row[4], "teacher_id": row[5], "teacher_name": row[6],
        "created_at": row[7].isoformat() if row[7] else None,
        "updated_at": row[8].isoformat() if row[8] else None
    }}


@router.post("/api/classes", status_code=201)
async def create_class(request: ClassCreate, token_data: TokenData = Depends(verify_teacher)):
    """Create a new class"""
    query = """INSERT INTO classes (name, description, invite_code, is_active, teacher_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING id"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (request.name, request.description, request.invite_code, True, token_data.user_id))
        class_id = cursor.fetchone()[0]
    await event_repository.log_event("class_created", token_data.user_id, {"class_id": class_id, "name": request.name})
    return {"success": True, "class_id": class_id}


@router.put("/api/classes/{class_id}")
async def update_class(class_id: int, request: ClassUpdate, token_data: TokenData = Depends(verify_teacher)):
    """Update an existing class"""
    fields = []
    values = []
    for field in ["name", "description", "invite_code", "is_active"]:
        val = getattr(request, field, None)
        if val is not None:
            fields.append(f"{field} = %s")
            values.append(val)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.extend([class_id, token_data.user_id])
    query = f"UPDATE classes SET {', '.join(fields)} WHERE id = %s AND teacher_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(values))
    return {"success": True, "message": "Class updated"}


@router.delete("/api/classes/{class_id}")
async def delete_class(class_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a class"""
    query = "DELETE FROM classes WHERE id = %s AND teacher_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, token_data.user_id))
    return {"success": True, "message": "Class deleted"}


@router.post("/api/classes/{class_id}/add-student")
async def add_student_to_class(class_id: int, request: ClassStudentAdd, token_data: TokenData = Depends(verify_teacher)):
    """Add a student to a class by public ID"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT id FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Class not found or unauthorized")
        cursor.execute("""
            INSERT INTO class_students (class_id, student_id)
            SELECT %s, id FROM users WHERE public_id = %s AND role = 'student'
            ON CONFLICT DO NOTHING RETURNING student_id""", (class_id, request.student_public_id))
        result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Student not found or already in class")
    student_id = result[0]
    await event_repository.log_event("student_added_to_class", token_data.user_id, {"class_id": class_id, "student_id": student_id})
    return {"success": True, "message": "Student added to class"}


@router.post("/api/classes/join/{invite_code}")
async def join_class_by_code(invite_code: str, token_data: TokenData = Depends(verify_token)):
    """Join a class using an invite code"""
    query = "SELECT id, teacher_id FROM classes WHERE invite_code = %s AND is_active = TRUE"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (invite_code,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Invalid or inactive invite code")
    class_id, teacher_id = row[0], row[1]
    if token_data.user_id == teacher_id:
        raise HTTPException(status_code=400, detail="Teacher cannot join their own class")
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO class_students (class_id, student_id) VALUES (%s, %s)
            ON CONFLICT DO NOTHING RETURNING student_id""", (class_id, token_data.user_id))
        result = cursor.fetchone()
    if not result:
        return {"success": True, "message": "Already a member of this class"}
    await event_repository.log_event("student_joined_class", token_data.user_id, {"class_id": class_id})
    return {"success": True, "message": "Joined class successfully"}


@router.get("/api/classes/{class_id}/modules")
async def get_class_modules(class_id: int, token_data: TokenData = Depends(verify_token)):
    """List modules assigned to a class"""
    query = """SELECT cm.id, cm.class_id, cm.module_id, cm.order, cm.is_mandatory, cm.due_date,
        m.title, m.description, m.difficulty, m.is_published
        FROM class_modules cm JOIN modules m ON cm.module_id = m.id
        WHERE cm.class_id = %s ORDER BY cm.order ASC"""
    modules = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id,))
        for row in cursor.fetchall():
            modules.append({"id": row[0], "class_id": row[1], "module_id": row[2], "order": row[3],
                           "is_mandatory": row[4], "due_date": row[5].isoformat() if row[5] else None,
                           "title": row[6], "description": row[7], "difficulty": row[8], "is_published": row[9]})
    return {"success": True, "class_modules": modules}


@router.post("/api/classes/{class_id}/modules")
async def add_module_to_class(class_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Assign a module to a class"""
    body = await request.json()
    module_id = body.get("module_id")
    order = body.get("order", 0)
    is_mandatory = body.get("is_mandatory", False)
    due_date = None
    if body.get("due_date"):
        try:
            due_date = datetime.fromisoformat(body["due_date"].replace('Z', '+00:00'))
        except:
            pass
    query = "INSERT INTO class_modules (class_id, module_id, \"order\", is_mandatory, due_date) VALUES (%s, %s, %s, %s, %s) RETURNING id"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT id FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Class not found or unauthorized")
        cursor.execute(query, (class_id, module_id, order, is_mandatory, due_date))
        new_id = cursor.fetchone()[0]
    return {"success": True, "id": new_id}


@router.get("/api/classes/{class_id}/students")
async def get_class_students(class_id: int, token_data: TokenData = Depends(verify_token)):
    """List students enrolled in a class"""
    query = """SELECT u.id, u.full_name, u.email, u.public_id, u.points, u.created_at
        FROM users u JOIN class_students cs ON u.id = cs.student_id WHERE cs.class_id = %s ORDER BY u.full_name ASC"""
    students = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id,))
        for row in cursor.fetchall():
            students.append({"id": row[0], "full_name": row[1], "email": row[2], "public_id": row[3],
                            "points": row[4] or 0, "joined_at": row[5].isoformat() if row[5] else None})
    return {"success": True, "students": students}


