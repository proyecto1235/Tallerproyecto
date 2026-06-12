from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas.ai import ChatRequest, ExerciseGenerateRequest, TutorRequest, FeedbackRequest
from app.schemas.common import TokenData
from app.dependencies import (
    ai_service, intelligent_tutor, ai_tutor_service, rag_service,
    exercise_generator_service, verify_token, verify_teacher, PostgresConnection,
    event_repository, rate_limiter,
)
from app.logging_config import logger

router = APIRouter(tags=["AI"])


@router.post("/api/ai/chat")
async def ai_chat(request: ChatRequest, token_data: TokenData = Depends(verify_token)):
    """Send a message to the AI chat assistant"""
    await rate_limiter.check_by_user(token_data.user_id, "ai_chat", max_requests=20, window_seconds=60)
    history = []
    if request.conversation_id:
        msg_query = "SELECT role, content FROM chat_messages WHERE conversation_id = %s ORDER BY created_at ASC"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(msg_query, (request.conversation_id,))
            for row in cursor.fetchall():
                history.append({"role": row[0], "content": row[1]})
    result = await ai_service.chat(request.message, history=history, context=request.context)
    conversation_id = request.conversation_id
    if not conversation_id:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("INSERT INTO conversations (student_id, title) VALUES (%s, %s) RETURNING id",
                          (token_data.user_id, request.message[:50]))
            conversation_id = cursor.fetchone()[0]
    insert_query = "INSERT INTO chat_messages (conversation_id, role, content) VALUES (%s, %s, %s)"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(insert_query, (conversation_id, "user", request.message))
        cursor.execute(insert_query, (conversation_id, "assistant", result["response"]))
    if token_data.role != "admin" and not request.conversation_id:
        try:
            from app.dependencies import check_and_award_achievements
            await check_and_award_achievements(token_data.user_id)
        except:
            pass
    return {"success": True, "response": result["response"], "conversation_id": conversation_id, "token_count": result.get("token_count")}


@router.get("/api/ai/conversations")
async def list_conversations(token_data: TokenData = Depends(verify_token)):
    """List chat conversations for the user"""
    query = "SELECT id, title, created_at, updated_at FROM conversations WHERE student_id = %s ORDER BY updated_at DESC"
    conversations = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id,))
        for row in cursor.fetchall():
            conversations.append({"id": row[0], "title": row[1], "created_at": row[2].isoformat() if row[2] else None,
                                 "updated_at": row[3].isoformat() if row[3] else None})
    return {"success": True, "conversations": conversations}


@router.get("/api/ai/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, token_data: TokenData = Depends(verify_token)):
    """Get messages in a conversation"""
    query = "SELECT role, content, created_at FROM chat_messages WHERE conversation_id = %s ORDER BY created_at ASC"
    messages = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (conversation_id,))
        for row in cursor.fetchall():
            messages.append({"role": row[0], "content": row[1], "created_at": row[2].isoformat() if row[2] else None})
    return {"success": True, "messages": messages}


@router.delete("/api/ai/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int, token_data: TokenData = Depends(verify_token)):
    """Delete a conversation"""
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("DELETE FROM chat_messages WHERE conversation_id = %s", (conversation_id,))
        cursor.execute("DELETE FROM conversations WHERE id = %s AND student_id = %s", (conversation_id, token_data.user_id))
    return {"success": True, "message": "Conversation deleted"}


@router.post("/api/ai/generate-exercise")
async def generate_exercise(request: ExerciseGenerateRequest, token_data: TokenData = Depends(verify_teacher)):
    """Generate an exercise using AI"""
    result = await exercise_generator_service.generate(
        topic=request.topic, difficulty=request.difficulty,
        exercise_type=request.exercise_type, language=request.language,
        additional_instructions=request.additional_instructions,
    )
    return {"success": True, **result}


@router.post("/api/ai/tutor")
async def tutor_ask(request: TutorRequest, token_data: TokenData = Depends(verify_token)):
    """Ask the AI tutor a question"""
    result = await ai_tutor_service.ask(
        question=request.question, module_id=request.module_id,
        student_id=token_data.user_id, code=request.code,
    )
    return {"success": True, "response": result.get("response"), "hints": result.get("hints")}


@router.post("/api/ai/ask")
async def intelligent_tutor_ask(request: Request, token_data: TokenData = Depends(verify_token)):
    """Ask the intelligent tutor a question"""
    body = await request.json()
    question = body.get("question", "")
    context = body.get("context", {})
    result = await intelligent_tutor.answer_question(question, token_data.user_id, context)
    return {"success": True, "answer": result.get("answer"), "resources": result.get("resources", [])}


@router.post("/api/ai/recommend")
async def get_recommendations(token_data: TokenData = Depends(verify_token)):
    """Get personalized recommendations"""
    result = await intelligent_tutor.get_recommendations(token_data.user_id)
    return {"success": True, "recommendations": result}


@router.post("/api/ai/feedback")
async def submit_feedback(request: FeedbackRequest, token_data: TokenData = Depends(verify_token)):
    """Submit user feedback"""
    query = "INSERT INTO feedback (user_id, module_id, exercise_id, content, rating, category) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, request.module_id, request.exercise_id, request.content, request.rating, request.category))
        feedback_id = cursor.fetchone()[0]
    return {"success": True, "feedback_id": feedback_id}


@router.post("/api/ai/explain")
async def explain_code(request: Request, token_data: TokenData = Depends(verify_token)):
    """Get an AI explanation of code"""
    body = await request.json()
    code = body.get("code", "")
    context = body.get("context", {})
    result = await ai_service.explain_code(code, context)
    return {"success": True, "explanation": result.get("explanation")}


@router.post("/api/ai/debug")
async def debug_code(request: Request, token_data: TokenData = Depends(verify_token)):
    """Get AI debugging assistance"""
    body = await request.json()
    code = body.get("code", "")
    error = body.get("error", "")
    result = await ai_service.debug_code(code, error)
    return {"success": True, "analysis": result.get("analysis"), "suggestions": result.get("suggestions")}


@router.post("/api/ai/rag-query")
async def rag_query(request: Request, token_data: TokenData = Depends(verify_token)):
    """Query the RAG knowledge base"""
    body = await request.json()
    query = body.get("query", "")
    context = body.get("context", {})
    result = await rag_service.query(query, context)
    return {"success": True, "response": result.get("response"), "sources": result.get("sources", [])}


@router.post("/api/ai/personalized-path")
async def personalized_path(token_data: TokenData = Depends(verify_token)):
    """Get a personalized learning path"""
    result = await intelligent_tutor.get_personalized_path(token_data.user_id)
    return {"success": True, "personalized_path": result}


