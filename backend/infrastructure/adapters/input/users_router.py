from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone

from app.schemas.auth import ProfileUpdate
from app.schemas.common import TokenData
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from app.dependencies import (
    user_repository, event_repository, pwd_context, verify_token, verify_token_optional,
)
from app.logging_config import logger

router = APIRouter(tags=["Users"],
    prefix="/api/users",
)


@router.get("/profile")
async def get_profile(token_data: TokenData = Depends(verify_token)):
    """Get the authenticated user's profile"""
    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "user": user.to_dict()}


@router.put("/profile")
async def update_profile(request: ProfileUpdate, token_data: TokenData = Depends(verify_token)):
    """Update the authenticated user's profile"""
    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.email is not None:
        user.email = request.email
    if request.password is not None and request.password != "":
        user.password_hash = pwd_context.hash(request.password)
    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url
    if request.bio is not None:
        user.bio = request.bio
    try:
        query = "UPDATE users SET full_name = %s, email = %s, password_hash = %s, avatar_url = %s, bio = %s WHERE id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (user.full_name, user.email, user.password_hash, user.avatar_url, user.bio, user.id))
        await event_repository.log_event("profile_updated", user.id, {"email": user.email})
        return {"success": True, "message": "Profile updated successfully", "user": user.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-public-id/{public_id}")
async def get_user_by_public_id(public_id: str, token_data: TokenData = Depends(verify_token_optional)):
    """Get a user by their public ID"""
    user = await user_repository.get_by_public_id(public_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.to_dict()
    user_data.pop("password_hash", None)
    return {"success": True, "user": user_data}


@router.get("/{user_id}")
async def get_user(user_id: int, token_data: TokenData = Depends(verify_token)):
    """Get a user by their internal ID"""
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.to_dict()
    user_data.pop("password_hash", None)
    return {"success": True, "user": user_data}


@router.get("/search")
async def search_users(q: str = "", token_data: TokenData = Depends(verify_token)):
    """Search users by name or email"""
    if not q:
        return {"success": True, "users": []}
    query = """
        SELECT id, email, full_name, role, avatar_url, bio, points, streak_days
        FROM users WHERE LOWER(full_name) LIKE LOWER(%s)
        ORDER BY full_name ASC LIMIT 20
    """
    users = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (f"%{q}%",))
        for row in cursor.fetchall():
            users.append({
                "id": row[0], "email": row[1], "full_name": row[2],
                "role": row[3], "avatar_url": row[4], "bio": row[5],
                "points": row[6], "streak_days": row[7]
            })
    return {"success": True, "users": users}


