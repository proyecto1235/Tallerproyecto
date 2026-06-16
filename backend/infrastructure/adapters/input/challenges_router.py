from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timezone

from app.schemas.challenges import ChallengeCreate, ChallengeSubmit
from app.schemas.common import TokenData
from app.dependencies import (
    sandbox_service, event_repository, PostgresConnection,
    verify_token, verify_teacher, check_and_award_achievements,
)
from app.logging_config import logger

router = APIRouter(tags=["Challenges"])


@router.get("/api/challenges")
async def list_challenges(token_data: TokenData = Depends(verify_token)):
    """List all challenges"""
    role = token_data.role
    if role == "student":
        query = """SELECT c.id, c.title, c.description, c.difficulty, c.points, u.full_name as author_name,
            c.base_code, c.deadline, c.is_published, COALESCE(ca.passed, FALSE) as user_passed, COALESCE(ca.attempt_count, 0) as user_attempts
            FROM challenges c JOIN users u ON c.teacher_id = u.id
            LEFT JOIN challenge_attempts ca ON ca.challenge_id = c.id AND ca.student_id = %s
            WHERE c.is_published = TRUE ORDER BY c.created_at DESC"""
        params = (token_data.user_id,)
    else:
        query = """SELECT c.id, c.title, c.description, c.difficulty, c.points, u.full_name as author_name,
            c.base_code, c.deadline, c.is_published, FALSE as user_passed, 0 as user_attempts
            FROM challenges c JOIN users u ON c.teacher_id = u.id ORDER BY c.created_at DESC"""
        params = ()
    challenges = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, params)
        for row in cursor.fetchall():
            deadline_str = None
            if row[7]:
                try:
                    deadline_str = row[7].isoformat() if hasattr(row[7], 'isoformat') else str(row[7])
                except:
                    deadline_str = str(row[7])
            challenges.append({"id": row[0], "title": row[1], "description": row[2], "difficulty": row[3], "points": row[4],
                              "author_name": row[5], "base_code": row[6] or "", "deadline": deadline_str,
                              "is_published": row[8], "user_passed": row[9], "user_attempts": row[10]})
    return {"success": True, "challenges": challenges}


@router.get("/api/challenges/{challenge_id}")
async def get_challenge(challenge_id: int, token_data: TokenData = Depends(verify_token)):
    """Get details of a specific challenge"""
    query = """SELECT c.id, c.title, c.description, c.instructions, c.difficulty, c.points, c.teacher_id,
        u.full_name as author_name, c.base_code, c.solution_code, c.solution_type, c.solution_output,
        c.test_code, c.deadline, c.is_published, c.max_attempts, c.created_at
        FROM challenges c JOIN users u ON c.teacher_id = u.id WHERE c.id = %s"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (challenge_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Challenge not found")

    deadline = row[13]
    deadline_passed = False
    if deadline:
        try:
            deadline_dt = deadline if not isinstance(deadline, str) else datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            deadline_passed = datetime.now(timezone.utc) > deadline_dt
        except:
            pass

    user_attempts = 0
    user_passed = False
    if token_data.role == "student":
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT attempt_count, passed FROM challenge_attempts WHERE challenge_id = %s AND student_id = %s ORDER BY submitted_at DESC LIMIT 1", (challenge_id, token_data.user_id))
            arow = cursor.fetchone()
            if arow:
                user_attempts = arow[0] or 0
                user_passed = arow[1]

    show_solution = token_data.role != "student" or deadline_passed or user_passed
    deadline_str = None
    if deadline:
        try:
            deadline_str = deadline.isoformat() if hasattr(deadline, 'isoformat') else str(deadline)
        except:
            deadline_str = str(deadline)

    return {"success": True, "challenge": {
        "id": row[0], "title": row[1], "description": row[2], "instructions": row[3],
        "difficulty": row[4], "points": row[5], "teacher_id": row[6], "author_name": row[7],
        "base_code": row[8] or "", "solution_code": row[9] if show_solution else None,
        "solution_type": row[10], "solution_output": row[11] if show_solution else None,
        "test_code": row[12] if show_solution else None, "deadline": deadline_str,
        "is_published": row[14], "max_attempts": row[15],
        "created_at": row[16].isoformat() if row[16] else None,
        "deadline_passed": deadline_passed, "user_attempts": user_attempts, "user_passed": user_passed
    }}


@router.post("/api/challenges")
async def create_challenge(request: ChallengeCreate, token_data: TokenData = Depends(verify_teacher)):
    """Create a new challenge"""
    deadline_val = None
    if request.deadline:
        try:
            deadline_val = datetime.fromisoformat(request.deadline.replace('Z', '+00:00'))
        except:
            deadline_val = None
    query = """INSERT INTO challenges (title, description, instructions, difficulty, points, teacher_id,
        base_code, solution_code, solution_type, solution_output, test_code, deadline, is_published, max_attempts)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (request.title, request.description, request.instructions, request.difficulty,
                                request.points, token_data.user_id, request.base_code, request.solution_code,
                                request.solution_type, request.solution_output, request.test_code,
                                deadline_val, request.is_published, request.max_attempts))
        challenge_id = cursor.fetchone()[0]
    await event_repository.log_event("challenge_created", token_data.user_id, {"challenge_id": challenge_id, "title": request.title})
    return {"success": True, "challenge_id": challenge_id}


@router.put("/api/challenges/{challenge_id}")
async def update_challenge(challenge_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Update an existing challenge"""
    body = await request.json()
    fields = []
    values = []
    allowed_fields = ["title", "description", "instructions", "difficulty", "points",
                      "base_code", "solution_code", "solution_type", "solution_output",
                      "test_code", "is_published", "max_attempts"]
    for field in allowed_fields:
        if field in body:
            fields.append(f"{field} = %s")
            values.append(body[field])
    if "deadline" in body and body["deadline"]:
        try:
            deadline_val = datetime.fromisoformat(body["deadline"].replace('Z', '+00:00'))
            fields.append("deadline = %s")
            values.append(deadline_val)
        except:
            pass
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(challenge_id)
    query = f"UPDATE challenges SET {', '.join(fields)} WHERE id = %s AND teacher_id = %s"
    values.append(token_data.user_id)
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(values))
    return {"success": True, "message": "Challenge updated"}


@router.delete("/api/challenges/{challenge_id}")
async def delete_challenge(challenge_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a challenge"""
    query = "DELETE FROM challenges WHERE id = %s AND teacher_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (challenge_id, token_data.user_id))
    return {"success": True, "message": "Challenge deleted"}


@router.post("/api/challenges/submit")
async def submit_challenge(request: ChallengeSubmit, token_data: TokenData = Depends(verify_token)):
    """Submit a solution for a challenge"""
    student_id = token_data.user_id
    query = """SELECT id, title, description, instructions, difficulty, points, base_code, solution_code,
        solution_type, solution_output, test_code, deadline, max_attempts FROM challenges WHERE id = %s"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (request.challenge_id,))
        row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Challenge not found")
    challenge = {"id": row[0], "title": row[1], "description": row[2], "instructions": row[3],
                 "difficulty": row[4], "points": row[5], "base_code": row[6] or "", "solution_code": row[7],
                 "solution_type": row[8] or "output", "solution_output": row[9], "test_code": row[10],
                 "deadline": row[11], "max_attempts": row[12] or 0}

    if challenge["deadline"]:
        try:
            deadline = challenge["deadline"]
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > deadline:
                raise HTTPException(status_code=400, detail="Challenge deadline has passed")
        except HTTPException:
            raise
        except:
            pass

    if challenge["max_attempts"] > 0:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM challenge_attempts WHERE challenge_id = %s AND student_id = %s", (request.challenge_id, student_id))
            if (cursor.fetchone()[0] or 0) >= challenge["max_attempts"]:
                raise HTTPException(status_code=400, detail="Maximum attempts reached")

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT passed FROM challenge_attempts WHERE challenge_id = %s AND student_id = %s AND passed = TRUE", (request.challenge_id, student_id))
        if cursor.fetchone():
            return {"success": True, "passed": True, "message": "Already passed this challenge"}

    grading_result = await sandbox_service.execute_and_compare(
        code=request.code, expected_output=challenge["solution_output"],
        solution_type=challenge["solution_type"], test_code=challenge["test_code"],
    )
    passed = grading_result["passed"]
    score = grading_result["score"]
    error = grading_result.get("error")

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""INSERT INTO challenge_attempts (challenge_id, student_id, passed, score, attempt_count, submitted_code)
            VALUES (%s, %s, %s, %s, (SELECT COALESCE(MAX(attempt_count), 0) + 1 FROM challenge_attempts WHERE challenge_id = %s AND student_id = %s), %s)""",
                       (request.challenge_id, student_id, passed, score, request.challenge_id, student_id, request.code))

    if passed:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s", (challenge["points"], student_id))
        await check_and_award_achievements(student_id)
        await event_repository.log_event("challenge_passed", student_id, {"challenge_id": request.challenge_id, "points_earned": challenge["points"]})

    return {"success": True, "passed": passed, "score": score, "error": error, "points_earned": challenge["points"] if passed else 0}


