from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
import bcrypt

from config.settings import settings
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from infrastructure.adapters.output.postgres.user_repository_impl import UserRepositoryImpl
from infrastructure.adapters.output.postgres.module_repository_impl import ModuleRepositoryImpl
from infrastructure.adapters.output.postgres.enrollment_repository_impl import EnrollmentRepositoryImpl
from infrastructure.adapters.output.postgres.teacher_repository_impl import TeacherRepositoryImpl
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository
from infrastructure.adapters.output.mongo.behavioral_repository import BehavioralRepository
from application.services.ai_service_impl import AIServiceImpl
from application.services.ai_recommender import RecommendationService
from application.services.student_predictor import StudentPredictor
from application.services.intelligent_tutor import IntelligentTutor
from application.services.sandbox_service import SandboxService
from application.services.llm_service import LLMService
from application.services.embedding_service import EmbeddingService
from application.services.rag_service import RAGService
from application.services.ai_tutor_service import AITutorService
from application.services.exercise_generator_service import ExerciseGeneratorService
from infrastructure.adapters.output.redis.cache import AICache
from infrastructure.adapters.output.redis.rate_limiter import RateLimiter
from app.schemas.common import TokenData
from domain.entities.user import UserRole

class _PasswordContext:
    """Backward-compatible password hashing using bcrypt directly"""
    @staticmethod
    def hash(secret: str) -> str:
        return bcrypt.hashpw(secret.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    @staticmethod
    def verify(secret: str, hash: str) -> bool:
        return bcrypt.checkpw(secret.encode("utf-8"), hash.encode("utf-8"))

pwd_context = _PasswordContext()
security = HTTPBearer()

# Repositories
user_repository = UserRepositoryImpl()
module_repository = ModuleRepositoryImpl()
enrollment_repository = EnrollmentRepositoryImpl()
teacher_repository = TeacherRepositoryImpl()
event_repository = EventRepository()
behavioral_repo = BehavioralRepository()

# AI / ML services
ai_service = AIServiceImpl()
student_predictor = StudentPredictor()
intelligent_tutor = IntelligentTutor(predictor=student_predictor)
sandbox_service = SandboxService()

# New architecture services
ai_cache = AICache(redis_url=settings.redis_url)
rate_limiter = RateLimiter(redis_url=settings.redis_url)
llm_service = LLMService(ollama_url=settings.ollama_url, model=settings.ollama_model)
embedding_service = EmbeddingService(llm_service=llm_service, cache=ai_cache)
rag_service = RAGService(embedding_service=embedding_service, llm_service=llm_service)
ai_tutor_service = AITutorService(llm_service=llm_service, rag_service=rag_service, cache=ai_cache)
exercise_generator_service = ExerciseGeneratorService(llm_service=llm_service)


def _get_sign_key() -> tuple:
    if settings.jwt_private_key:
        return settings.jwt_private_key, "RS256"
    return settings.secret_key, "HS256"


def _decode_token_fallback(token: str) -> dict:
    algorithms = []
    if settings.jwt_public_key:
        algorithms.append("RS256")
    if settings.secret_key:
        algorithms.append("HS256")
    last_exc = None
    for alg in algorithms:
        key = settings.jwt_public_key if alg == "RS256" else settings.secret_key
        try:
            return jwt.decode(token, key, algorithms=[alg])
        except JWTError as e:
            last_exc = e
    raise last_exc or JWTError("Token verification failed")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    import uuid
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "iat": now, "jti": str(uuid.uuid4())})
    key, alg = _get_sign_key()
    return jwt.encode(to_encode, key, algorithm=alg)


def _extract_jti_from_token(token: str) -> str:
    """Extract jti from JWT without signature verification. Fallback to full token."""
    try:
        parts = token.split(".")
        if len(parts) == 3:
            import json, base64
            payload_b64 = parts[1]
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            jti = payload.get("jti")
            if jti:
                return jti
    except Exception:
        pass
    return token


async def is_token_blacklisted(token: str) -> bool:
    try:
        r = await rate_limiter._get_redis()
        if r is None:
            return True
        key = _extract_jti_from_token(token)
        return await r.exists(f"token_blacklist:{key}")
    except Exception as e:
        from app.logging_config import logger
        logger.error(f"Redis error in is_token_blacklisted: {e}")
        return True


async def verify_token(request: Request) -> TokenData:
    token = request.cookies.get("auth-token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if await is_token_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    try:
        payload = _decode_token_fallback(token)
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        jti: str = payload.get("jti")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return TokenData(user_id=user_id, email=email, role=role, exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc), jti=jti)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def verify_teacher(token_data: TokenData = Depends(verify_token)) -> TokenData:
    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires teacher privileges")
    return token_data


async def verify_admin(token_data: TokenData = Depends(verify_token)) -> TokenData:
    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin privileges")
    return token_data


async def verify_token_optional(request: Request) -> Optional[TokenData]:
    token = request.cookies.get("auth-token")
    if not token:
        return None
    try:
        payload = _decode_token_fallback(token)
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        jti: str = payload.get("jti")
        if user_id is None:
            return None
        return TokenData(user_id=user_id, email=email, role=role, exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc), jti=jti)
    except JWTError:
        return None


async def check_and_award_achievements(user_id: int):
    """Check all achievement criteria and award any newly earned ones"""
    try:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.id, a.criteria FROM achievements a
                JOIN user_achievements ua ON ua.achievement_id = a.id
                WHERE ua.user_id = %s
            """, (user_id,))
            earned_ids = {row[0] for row in cursor.fetchall()}

        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT id, name, criteria, points FROM achievements")
            all_achievements = cursor.fetchall()

        new_achievements = []
        for ach_id, name, criteria_json, points in all_achievements:
            if ach_id in earned_ids:
                continue
            if not criteria_json:
                continue
            criteria = criteria_json if isinstance(criteria_json, dict) else {}
            if not criteria:
                continue

            earned = False
            ach_type = criteria.get("type", "")

            if ach_type == "exercise_complete":
                count = criteria.get("count", 1)
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM exercise_attempts WHERE student_id = %s AND passed = TRUE", (user_id,))
                    if (cursor.fetchone()[0] or 0) >= count:
                        earned = True
            elif ach_type == "module_complete":
                module_order = criteria.get("module_order")
                if module_order:
                    with PostgresConnection.get_cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) FROM enrollments e
                            JOIN modules m ON e.module_id = m.id
                            WHERE e.student_id = %s AND e.status = 'completed' AND m."order" = %s
                        """, (user_id, module_order))
                        if (cursor.fetchone()[0] or 0) > 0:
                            earned = True
            elif ach_type == "exercise_fail_then_pass":
                count = criteria.get("count", 10)
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM (
                            SELECT exercise_id FROM exercise_attempts 
                            WHERE student_id = %s AND passed = TRUE
                            GROUP BY exercise_id
                            HAVING COUNT(*) > 1
                        ) sub
                    """, (user_id,))
                    if (cursor.fetchone()[0] or 0) >= count:
                        earned = True
            elif ach_type == "streak_days":
                count = criteria.get("count", 7)
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("SELECT COALESCE(streak_days, 0) FROM users WHERE id = %s", (user_id,))
                    if (cursor.fetchone()[0] or 0) >= count:
                        earned = True
            elif ach_type == "challenge_complete":
                count = criteria.get("count", 1)
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM challenge_attempts WHERE student_id = %s AND passed = TRUE", (user_id,))
                    if (cursor.fetchone()[0] or 0) >= count:
                        earned = True
            elif ach_type == "first_try":
                count = criteria.get("count", 1)
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM (
                            SELECT exercise_id FROM exercise_attempts 
                            WHERE student_id = %s AND passed = TRUE AND attempt_count = 1
                            GROUP BY exercise_id
                        ) sub
                    """, (user_id,))
                    if (cursor.fetchone()[0] or 0) >= count:
                        earned = True

            if earned:
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_achievements (user_id, achievement_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING
                    """, (user_id, ach_id))
                    cursor.execute("UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s", (points, user_id))
                new_achievements.append({"id": ach_id, "name": name})

        if new_achievements:
            await event_repository.log_event("achievements_awarded", user_id, {
                "count": len(new_achievements),
                "achievements": [a["name"] for a in new_achievements]
            })
        return new_achievements
    except Exception as e:
        from app.logging_config import logger
        logger.warning(f"Achievement check error: {e}")
        return []
