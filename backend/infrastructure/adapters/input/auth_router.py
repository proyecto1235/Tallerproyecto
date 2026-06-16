from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
import asyncio

from app.schemas.auth import RegisterRequest, LoginRequest, ProfileUpdate, UserRoleUpdate
from app.schemas.common import TokenData
from app.dependencies import (
    pwd_context, user_repository, event_repository, rate_limiter,
    create_access_token, verify_token, verify_token_optional,
)
from app.logging_config import logger
from application.useCases.register_user import RegisterUserUseCase
from config.settings import settings

router = APIRouter(tags=["Auth"])


@router.post("/api/auth/register")
async def register(request: RegisterRequest, response: Response, http_request: Request):
    """Register a new user account"""
    await rate_limiter.check_by_ip(http_request, "register", max_requests=5, window_seconds=300)
    use_case = RegisterUserUseCase(user_repository)
    result = await use_case.execute(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        request_teacher=request.request_teacher
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    user = result.get("user")
    token = create_access_token({"user_id": user["id"], "email": user["email"], "role": user["role"]})
    response.set_cookie(
        key="auth-token", value=token, httponly=True,
        secure=settings.node_env == "production", samesite="strict",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return {"success": True, "user": user, "teacher_request_pending": result.get("teacher_request_pending", False)}


@router.post("/api/auth/login")
async def login(request: LoginRequest, response: Response, http_request: Request):
    """Authenticate user and return JWT token"""
    await rate_limiter.check_by_ip(http_request, "login", max_requests=10, window_seconds=60)
    logger.debug(f"Login attempt for {request.email}")
    user = await user_repository.get_by_email(request.email)
    if not user:
        logger.debug("User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.debug("Found user, verifying password...")
    try:
        is_valid = pwd_context.verify(request.password, user.password_hash)
    except Exception as e:
        logger.error(f"Password verification error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al verificar la contraseña")
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")
    token = create_access_token({"user_id": user.id, "email": user.email, "role": user.role.value})
    response.set_cookie(
        key="auth-token", value=token, httponly=True,
        secure=settings.node_env == "production", samesite="strict",
        max_age=settings.access_token_expire_minutes * 60,
    )
    asyncio.create_task(event_repository.log_event("user_login", user.id, {"email": user.email}))
    logger.debug(f"Login successful for {user.email}")
    return {
        "success": True,
        "user": {
            "id": user.id, "email": user.email, "full_name": user.full_name,
            "role": user.role.value, "points": getattr(user, "points", 0),
            "streak_days": getattr(user, "streakDays", 0),
            "teacher_request_status": user.teacher_request_status.value if user.teacher_request_status else None,
        }
    }


@router.post("/api/auth/logout")
async def logout(http_request: Request, response: Response, token_data: TokenData = Depends(verify_token)):
    """Invalidate the current JWT token"""
    try:
        r = await rate_limiter._get_redis()
        if r:
            blacklist_key = token_data.jti if token_data.jti else http_request.cookies.get("auth-token")
            if blacklist_key:
                exp = int(token_data.exp.timestamp())
                ttl = max(exp - int(datetime.now(timezone.utc).timestamp()), 0)
                if ttl > 0:
                    await r.setex(f"token_blacklist:{blacklist_key}", ttl, "1")
    except Exception as e:
        logger.error(f"Error blacklisting token: {e}")
    response.delete_cookie(key="auth-token", path="/", secure=settings.node_env == "production", samesite="lax", httponly=True)
    await event_repository.log_event("user_logout", token_data.user_id, {"email": token_data.email})
    return {"success": True, "message": "Logged out successfully"}
