from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas.modules import ModuleCreate, ModuleUpdate, ModuleComplete, LessonComplete
from app.schemas.common import TokenData
from app.dependencies import (
    module_repository, enrollment_repository, user_repository,
    event_repository, PostgresConnection, verify_token, verify_teacher, verify_admin,
    check_and_award_achievements,
)
from domain.entities.module import Module, ContentStatus
from app.logging_config import logger

router = APIRouter(tags=["Modules"])


@router.get("/api/modules")
async def list_modules():
    """List all published modules"""
    query = """
        SELECT m.id, m.title, m.description, m.theory_content, m.teacher_id,
               m.status, m."order", m.is_published, m.is_global, m.difficulty, m.lesson_count,
               m.created_at, u.full_name as teacher_name
        FROM modules m LEFT JOIN users u ON m.teacher_id = u.id
        WHERE m.is_published = TRUE AND m.status = 'approved'
        ORDER BY m."order" ASC
    """
    modules = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            modules.append({
                "id": row[0], "title": row[1], "description": row[2],
                "theory_content": row[3], "teacher_id": row[4], "status": row[5],
                "order": row[6], "is_published": row[7], "is_global": row[8],
                "difficulty": row[9], "lesson_count": row[10],
                "created_at": row[11].isoformat() if row[11] else None, "teacher_name": row[12]
            })
    return {"success": True, "modules": modules}


@router.get("/api/modules/search")
async def search_modules(q: str = "", token_data: TokenData = Depends(verify_token)):
    """Search modules by keyword"""
    query = """
        SELECT m.id, m.title, m.description, m.teacher_id, u.full_name as teacher_name 
        FROM modules m JOIN users u ON m.teacher_id = u.id
        WHERE m.is_published = TRUE AND m.status = 'approved'
        AND (m.title ILIKE %s OR u.full_name ILIKE %s)
        ORDER BY m.title ASC
    """
    search_term = f"%{q}%"
    results = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (search_term, search_term))
        for row in cursor.fetchall():
            results.append({"id": row[0], "title": row[1], "description": row[2], "teacher_id": row[3], "teacher_name": row[4]})
    return {"success": True, "results": results}


@router.get("/api/modules/enrolled")
async def get_enrolled_modules(token_data: TokenData = Depends(verify_token)):
    """Get modules the current user is enrolled in"""
    enrollments = await enrollment_repository.get_by_student(token_data.user_id)
    result = []
    for enr in enrollments:
        module = await module_repository.get_by_id(enr.module_id)
        if module:
            mod_dict = module.to_dict()
            mod_dict["enrollment_status"] = enr.status
            mod_dict["enrolled_at"] = enr.enrolled_at.isoformat() if enr.enrolled_at else None
            result.append(mod_dict)
    return {"success": True, "modules": result}


@router.get("/api/modules/{module_id}")
async def get_module(module_id: int):
    """Get details of a specific module"""
    module = await module_repository.get_by_id(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    result = module.to_dict()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""SELECT id, title, theory_content, "order" FROM lessons WHERE module_id = %s ORDER BY "order" ASC""", (module_id,))
        lesson_rows = cursor.fetchall()
    lessons = []
    for row in lesson_rows:
        lesson_id, title, theory, order_num = row
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""SELECT id, title, description, instructions, difficulty, points, solution_output, solution_type, "order"
                FROM exercises WHERE lesson_id = %s ORDER BY "order" ASC""", (lesson_id,))
            ex_rows = cursor.fetchall()
        exercises = [{"id": er[0], "title": er[1], "description": er[2], "instructions": er[3],
                       "difficulty": er[4], "points": er[5], "solution_output": er[6], "solution_type": er[7], "order": er[8]} for er in ex_rows]
        lessons.append({"id": lesson_id, "title": title, "theory": theory, "order": order_num, "exercises": exercises})
    result["lessons"] = lessons
    return {"success": True, "module": result}


@router.get("/api/modules/{module_id}/exercises")
async def get_module_exercises(module_id: int):
    """List exercises in a module"""
    query = """SELECT id, module_id, title, description, theory_content, instructions, difficulty, points, "order"
        FROM exercises WHERE module_id = %s ORDER BY "order" ASC"""
    exercises = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id,))
        for row in cursor.fetchall():
            exercises.append({"id": row[0], "module_id": row[1], "title": row[2], "description": row[3],
                              "theory_content": row[4], "instructions": row[5], "difficulty": row[6], "points": row[7], "order": row[8]})
    return {"success": True, "exercises": exercises}


@router.get("/api/modules/{module_id}/progress")
async def get_module_progress(module_id: int, token_data: TokenData = Depends(verify_token)):
    """Get progress for a module"""
    query = """SELECT p.percentage, p.completed_exercises, p.total_exercises, p.points_earned, p.is_completed, p.last_activity, e.status as enrollment_status
        FROM progress p JOIN enrollments e ON e.student_id = p.student_id AND e.module_id = p.module_id
        WHERE p.student_id = %s AND p.module_id = %s"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, module_id))
        row = cursor.fetchone()
    if not row:
        enroll_query = "SELECT status FROM enrollments WHERE student_id = %s AND module_id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(enroll_query, (token_data.user_id, module_id))
            enr = cursor.fetchone()
        if enr:
            return {"success": True, "progress": {"percentage": 0, "completed_exercises": 0, "total_exercises": 0,
                                                    "points_earned": 0, "is_completed": False, "enrollment_status": enr[0]}}
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM exercises WHERE module_id = %s", (module_id,))
            total = cursor.fetchone()[0]
        return {"success": True, "progress": {"percentage": 0, "completed_exercises": 0, "total_exercises": total,
                                                "points_earned": 0, "is_completed": False, "enrollment_status": None}}
    return {"success": True, "progress": {
        "percentage": float(row[0]) if row[0] else 0, "completed_exercises": row[1] or 0,
        "total_exercises": row[2] or 0, "points_earned": row[3] or 0, "is_completed": row[4] or False,
        "last_activity": row[5].isoformat() if row[5] else None, "enrollment_status": row[6]
    }}


@router.get("/api/modules/{module_id}/lessons")
async def get_module_lessons(module_id: int, token_data: TokenData = Depends(verify_token)):
    """List lessons in a module"""
    student_id = token_data.user_id
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""SELECT id, title, theory_content, "order" FROM lessons WHERE module_id = %s ORDER BY "order" ASC""", (module_id,))
        lesson_rows = cursor.fetchall()
    lessons = []
    for row in lesson_rows:
        lesson_id, title, theory, order_num = row
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT e.id, e.title, e.description, e.instructions, e.difficulty, e.points, e.solution_output,
                    COALESCE((SELECT passed FROM exercise_attempts WHERE student_id = %s AND exercise_id = e.id ORDER BY submitted_at DESC LIMIT 1), FALSE) as passed,
                    (SELECT attempt_count FROM exercise_attempts WHERE student_id = %s AND exercise_id = e.id ORDER BY submitted_at DESC LIMIT 1) as attempts
                FROM exercises e WHERE e.lesson_id = %s ORDER BY e."order" ASC
            """, (student_id, student_id, lesson_id))
            exercise_rows = cursor.fetchall()
        exercises = [{"id": er[0], "title": er[1], "description": er[2], "instructions": er[3],
                       "difficulty": er[4], "points": er[5], "solution": er[6], "passed": bool(er[7]), "attempts": er[8] or 0} for er in exercise_rows]
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT 1 FROM lesson_completions WHERE student_id = %s AND lesson_id = %s", (student_id, lesson_id))
            lesson_done = cursor.fetchone() is not None
        lessons.append({"id": lesson_id, "title": title, "theory": theory, "order": order_num, "completed": lesson_done,
                        "total_exercises": len(exercises), "passed_exercises": sum(1 for ex in exercises if ex["passed"]), "exercises": exercises})
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT title, lesson_count FROM modules WHERE id = %s", (module_id,))
        mod = cursor.fetchone()
        mod_title = mod[0] if mod else ""
    total_lessons = len(lessons)
    completed_lessons = sum(1 for l in lessons if l["completed"])
    return {"success": True, "module_id": module_id, "module_title": mod_title, "lessons": lessons,
            "total_lessons": total_lessons, "completed_lessons": completed_lessons,
            "all_completed": total_lessons > 0 and completed_lessons >= total_lessons}


@router.post("/api/modules/complete")
async def complete_module(request: ModuleComplete, token_data: TokenData = Depends(verify_token)):
    """Mark a module as completed"""
    student_id = token_data.user_id
    module_id = request.module_id
    enroll_query = "SELECT id, status FROM enrollments WHERE student_id = %s AND module_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(enroll_query, (student_id, module_id))
        enrollment = cursor.fetchone()
    if not enrollment:
        raise HTTPException(status_code=400, detail="Not enrolled in this module")
    if enrollment[1] == "completed":
        return {"success": True, "message": "Module already completed"}
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM lessons WHERE module_id = %s", (module_id,))
        total_lessons = cursor.fetchone()[0] or 0
    if total_lessons > 0:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM lesson_completions WHERE module_id = %s AND student_id = %s", (module_id, student_id))
            completed_lessons = cursor.fetchone()[0] or 0
        if completed_lessons < total_lessons:
            return {"success": False, "message": f"Complete all {total_lessons} lessons first ({completed_lessons}/{total_lessons})"}
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE enrollments SET status = 'completed', completed_at = NOW() WHERE student_id = %s AND module_id = %s", (student_id, module_id))
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""INSERT INTO progress (student_id, module_id, percentage, is_completed, last_activity)
            VALUES (%s, %s, 100.0, TRUE, NOW()) ON CONFLICT (student_id, module_id) DO UPDATE SET percentage = 100.0, is_completed = TRUE, last_activity = NOW()""", (student_id, module_id))
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE users SET points = COALESCE(points, 0) + 50 WHERE id = %s", (student_id,))
    await check_and_award_achievements(student_id)
    await event_repository.log_event("module_completed", student_id, {"module_id": module_id, "manual": True})
    return {"success": True, "message": "Module completed!", "points_earned": 50}


@router.post("/api/modules")
async def create_module(request: ModuleCreate, token_data: TokenData = Depends(verify_teacher)):
    """Create a new module"""
    module = Module(id=None, title=request.title, description=request.description,
                    teacher_id=token_data.user_id, status=ContentStatus.DRAFT,
                    order=request.order, is_published=request.is_published)
    created_module = await module_repository.create(module)
    await event_repository.log_event("module_created", token_data.user_id, {"module_id": created_module.id, "title": created_module.title})
    return {"success": True, "module": created_module.to_dict()}


@router.put("/api/modules/{module_id}")
async def update_module(module_id: int, request: ModuleUpdate, token_data: TokenData = Depends(verify_teacher)):
    """Update an existing module"""
    module = await module_repository.get_by_id(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if module.teacher_id != token_data.user_id and token_data.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit this module")
    if request.title is not None:
        module.title = request.title
    if request.description is not None:
        module.description = request.description
    if request.order is not None:
        module.order = request.order
    if request.is_published is not None:
        module.is_published = request.is_published
    if request.difficulty is not None:
        module.difficulty = request.difficulty
    if request.theory_content is not None:
        module.theory_content = request.theory_content
    updated_module = await module_repository.update(module)
    return {"success": True, "module": updated_module.to_dict()}


@router.delete("/api/modules/{module_id}")
async def request_module_deletion(module_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a module"""
    module = await module_repository.get_by_id(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if module.teacher_id != token_data.user_id and token_data.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this module")
    module.status = ContentStatus.PENDING_DELETION
    await module_repository.update(module)
    await event_repository.log_event("module_deletion_requested", token_data.user_id, {"module_id": module.id})
    return {"success": True, "message": "Module deletion requested and pending admin approval"}


@router.post("/api/modules/{module_id}/enroll")
async def enroll_module(module_id: int, token_data: TokenData = Depends(verify_token)):
    """Enroll in a module"""
    from application.useCases.enroll_student import EnrollStudentUseCase
    use_case = EnrollStudentUseCase(user_repository, module_repository, event_repository, enrollment_repository)
    result = await use_case.execute(token_data.user_id, module_id)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return result


# ---- Lesson CRUD ----

@router.post("/api/modules/{module_id}/lessons")
async def create_module_lesson(module_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Add a lesson to a module"""
    body = await request.json()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        cursor.execute("""INSERT INTO lessons (module_id, title, theory_content, "order") VALUES (%s, %s, %s, %s) RETURNING id""",
                       (module_id, body.get("title", "New Lesson"), body.get("theory_content", ""), body.get("order", 0)))
        lesson_id = cursor.fetchone()[0]
        cursor.execute("UPDATE modules SET lesson_count = (SELECT COUNT(*) FROM lessons WHERE module_id = %s) WHERE id = %s", (module_id, module_id))
    return {"success": True, "lesson_id": lesson_id}


@router.put("/api/modules/{module_id}/lessons/{lesson_id}")
async def update_module_lesson(module_id: int, lesson_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Update a lesson"""
    body = await request.json()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        fields = []; values = []
        if "title" in body:
            fields.append("title = %s"); values.append(body["title"])
        if "theory_content" in body:
            fields.append("theory_content = %s"); values.append(body["theory_content"])
        if "order" in body:
            fields.append('"order" = %s'); values.append(body["order"])
        if fields:
            values.extend([lesson_id, module_id])
            cursor.execute(f"UPDATE lessons SET {', '.join(fields)} WHERE id = %s AND module_id = %s", tuple(values))
    return {"success": True, "message": "Lesson updated"}


@router.delete("/api/modules/{module_id}/lessons/{lesson_id}")
async def delete_module_lesson(module_id: int, lesson_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a lesson from a module"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        cursor.execute("DELETE FROM lessons WHERE id = %s AND module_id = %s", (lesson_id, module_id))
        cursor.execute("UPDATE modules SET lesson_count = (SELECT COUNT(*) FROM lessons WHERE module_id = %s) WHERE id = %s", (module_id, module_id))
    return {"success": True, "message": "Lesson deleted"}


@router.post("/api/modules/{module_id}/exercises")
async def create_module_exercise(module_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Add an exercise to a module"""
    body = await request.json()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        cursor.execute("""INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points,
            solution_output, solution_type, test_code, "order") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                       (module_id, body.get("lesson_id"), body.get("title", "New Exercise"), body.get("description", ""),
                        body.get("instructions", ""), body.get("difficulty", 1), body.get("points", 10),
                        body.get("solution_output"), body.get("solution_type", "output"), body.get("test_code"), body.get("order", 0)))
        exercise_id = cursor.fetchone()[0]
    return {"success": True, "exercise_id": exercise_id}


@router.put("/api/modules/{module_id}/exercises/{exercise_id}")
async def update_module_exercise(module_id: int, exercise_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Update an exercise"""
    body = await request.json()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        fields = []; values = []
        for key in ("title", "description", "instructions", "difficulty", "points", "solution_output", "solution_type", "test_code", "lesson_id"):
            if key in body:
                fields.append(f"{key} = %s"); values.append(body[key])
        if "order" in body:
            fields.append('"order" = %s'); values.append(body["order"])
        if fields:
            values.extend([exercise_id, module_id])
            cursor.execute(f"UPDATE exercises SET {', '.join(fields)} WHERE id = %s AND module_id = %s", tuple(values))
    return {"success": True, "message": "Exercise updated"}


@router.delete("/api/modules/{module_id}/exercises/{exercise_id}")
async def delete_module_exercise(module_id: int, exercise_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete an exercise from a module"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        cursor.execute("DELETE FROM exercises WHERE id = %s AND module_id = %s", (exercise_id, module_id))
    return {"success": True, "message": "Exercise deleted"}


