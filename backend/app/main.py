from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from config.database_init import initialize_database
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from infrastructure.adapters.output.postgres.user_repository_impl import UserRepositoryImpl
from infrastructure.adapters.output.postgres.module_repository_impl import ModuleRepositoryImpl
from infrastructure.adapters.output.postgres.enrollment_repository_impl import EnrollmentRepositoryImpl
from infrastructure.adapters.output.postgres.teacher_repository_impl import TeacherRepositoryImpl
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository
from application.services.ai_service_impl import AIServiceImpl
from application.services.ai_recommender import RecommendationService
from application.services.student_predictor import StudentPredictor
from application.services.intelligent_tutor import IntelligentTutor
from application.services.sandbox_service import SandboxService
from application.services.llm_service import LLMService
from application.services.embedding_service import EmbeddingService
from application.services.rag_service import RAGService
from application.services.ai_tutor_service import AITutorService
from infrastructure.adapters.output.redis.cache import AICache
from infrastructure.adapters.output.redis.rate_limiter import RateLimiter
from application.services.exercise_generator_service import ExerciseGeneratorService
from infrastructure.adapters.output.mongo.behavioral_repository import BehavioralRepository
from application.useCases.register_user import RegisterUserUseCase
from application.useCases.get_recommendations import GetRecommendationsUseCase
from application.useCases.enroll_student import EnrollStudentUseCase
from application.useCases.teacher_dashboard import TeacherDashboardUseCase
from application.useCases.generate_ai_alerts import GenerateAIAlertsUseCase
from domain.entities.user import User, UserRole
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

# ============================================
# Security Configuration
# ============================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class TokenData(BaseModel):
    user_id: int
    email: str
    role: str
    exp: datetime

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    request_teacher: bool = False

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    message: str

class PublicChatRequest(BaseModel):
    message: str
    session_id: str
    history: Optional[list] = []

class ModuleCreate(BaseModel):
    title: str
    description: str
    order: int = 0
    is_published: bool = False

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None
    difficulty: Optional[str] = None
    theory_content: Optional[str] = None

class ExecuteRequest(BaseModel):
    code: str

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

# Classes Models
class ClassCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    is_published: bool = False

class ClassUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    is_published: Optional[bool] = None

class ClassModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    theory_content: Optional[str] = None
    order: int = 0

class ClassModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    theory_content: Optional[str] = None
    order: Optional[int] = None

class ClassExerciseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    exercise_type: str = "coding"
    difficulty: int = 1
    points: int = 10
    order: int = 0
    solution_output: Optional[str] = None
    solution_type: Optional[str] = "output"
    test_code: Optional[str] = None
    metadata: Optional[dict] = None

class ClassExerciseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    exercise_type: Optional[str] = None
    difficulty: Optional[int] = None
    points: Optional[int] = None
    order: Optional[int] = None
    solution_output: Optional[str] = None
    solution_type: Optional[str] = None
    test_code: Optional[str] = None
    metadata: Optional[dict] = None

class UserRoleUpdate(BaseModel):
    role: str

class ExerciseSubmit(BaseModel):
    exercise_id: int
    code: str
    module_id: int
    is_class_exercise: bool = False
    class_module_id: Optional[int] = None

class ModuleComplete(BaseModel):
    module_id: int

class LessonComplete(BaseModel):
    module_id: int
    lesson_id: int

class ChallengeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: int = 1
    points: int = 100
    base_code: Optional[str] = ""
    solution_code: Optional[str] = None
    solution_type: str = "output"
    solution_output: Optional[str] = None
    test_code: Optional[str] = None
    deadline: Optional[str] = None
    is_published: bool = False
    max_attempts: int = 0

class ChallengeSubmit(BaseModel):
    challenge_id: int
    code: str

# New architecture models
class ExerciseSuggestionRequest(BaseModel):
    exercise_id: int
    title: str
    description: str
    instructions: str
    solution: str
    difficulty: int

class RAGIndexRequest(BaseModel):
    text: str
    source_type: str
    source_id: int
    metadata: Optional[dict] = None

class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    source_type: Optional[str] = None

class AITutorAskRequest(BaseModel):
    message: str
    student_level: str = "beginner"

# ============================================
# Lifespan Events
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Robolearn API...")
    
    # Set Google credentials for Dialogflow if configured
    if settings.google_credentials_path:
        cred_path = os.path.abspath(settings.google_credentials_path)
        if os.path.exists(cred_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
            print(f"✅ Google credentials loaded from: {cred_path}")
        else:
            print(f"⚠️ Google credentials file not found at: {cred_path}")
    
    # Initialize database (create if needed, migrate tables, seed data)
    initialize_database()
    
    PostgresConnection.init_pool()
    
    yield
    
    # Shutdown
    print("Shutting down Robolearn API...")
    PostgresConnection.close_pool()
    EventRepository.close()

# ============================================
# Initialize FastAPI App
# ============================================

app = FastAPI(
    title="Robolearn API",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Audit Logging Middleware
# ============================================

AUDIT_PATHS = [
    "/api/auth/", "/api/admin/", "/api/users/profile",
    "/api/execute-code", "/api/exercises/submit",
]

@app.middleware("http")
async def audit_logging(request: Request, call_next):
    if any(request.url.path.startswith(p) for p in AUDIT_PATHS):
        ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        method = request.method
        path = request.url.path
        print(f"[AUDIT] {ip} - {method} {path}")
    response = await call_next(request)
    return response

# ============================================
# Security Headers Middleware
# ============================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.node_env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response

# ============================================
# Utilities
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"GLOBAL ERROR: {type(exc).__name__}: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Error interno del servidor"},
    )

async def is_token_blacklisted(token: str) -> bool:
    try:
        r = await rate_limiter._get_redis()
        if r:
            return await r.exists(f"token_blacklist:{token}")
    except Exception:
        pass
    return False

async def verify_token(request: Request) -> TokenData:
    """Verify JWT token from cookies"""
    token = request.cookies.get("auth-token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return TokenData(
            user_id=user_id,
            email=email,
            role=role,
            exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def verify_teacher(token_data: TokenData = Depends(verify_token)) -> TokenData:
    """Verify user is a teacher or admin (checks DB for current role)"""
    user = await user_repository.get_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher privileges"
        )
    return token_data

async def verify_admin(token_data: TokenData = Depends(verify_token)) -> TokenData:
    """Verify user is an admin"""
    if token_data.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges"
        )
    return token_data

async def verify_token_optional(request: Request) -> Optional[TokenData]:
    """Verify JWT token from cookies — returns None if not authenticated"""
    token = request.cookies.get("auth-token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        if user_id is None:
            return None
        return TokenData(
            user_id=user_id, email=email, role=role,
            exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        )
    except JWTError:
        return None

# ============================================
# Initialize Repositories
# ============================================

user_repository = UserRepositoryImpl()
module_repository = ModuleRepositoryImpl()
enrollment_repository = EnrollmentRepositoryImpl()
teacher_repository = TeacherRepositoryImpl()
event_repository = EventRepository()
ai_service = AIServiceImpl()
behavioral_repo = BehavioralRepository()
student_predictor = StudentPredictor()
intelligent_tutor = IntelligentTutor(predictor=student_predictor)

# New architecture services
sandbox_service = SandboxService()
ai_cache = AICache(redis_url=settings.redis_url)
rate_limiter = RateLimiter(redis_url=settings.redis_url)
llm_service = LLMService(
    ollama_url=settings.ollama_url,
    model=settings.ollama_model,
)
embedding_service = EmbeddingService(llm_service=llm_service, cache=ai_cache)
rag_service = RAGService(embedding_service=embedding_service, llm_service=llm_service)
ai_tutor_service = AITutorService(llm_service=llm_service, rag_service=rag_service, cache=ai_cache)
exercise_generator_service = ExerciseGeneratorService(llm_service=llm_service)

# ============================================
# Routes - Health
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"message": "Robolearn API running", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# ============================================
# Routes - Authentication
# ============================================

@app.post("/api/auth/register", tags=["Auth"])
async def register(request: RegisterRequest, response: Response, http_request: Request):
    """Register a new user"""
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
    
    # Create token
    user = result.get("user")
    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"]
    })
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="auth-token",
        value=token,
        httponly=True,
        secure=settings.node_env == "production",
        samesite="strict",
        max_age=settings.access_token_expire_minutes * 60,
    )
    
    return {
        "success": True,
        "user": user,
        "teacher_request_pending": result.get("teacher_request_pending", False)
    }

@app.post("/api/auth/login", tags=["Auth"])
async def login(request: LoginRequest, response: Response, http_request: Request):
    """Login user"""
    await rate_limiter.check_by_ip(http_request, "login", max_requests=10, window_seconds=60)
    print(f"DEBUG: Login attempt for {request.email}")

    user = await user_repository.get_by_email(request.email)
    if not user:
        print(f"DEBUG: User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    print(f"DEBUG: Found user, verifying password...")
    try:
        is_valid = pwd_context.verify(request.password[:72], user.password_hash)
    except Exception as e:
        print(f"DEBUG: bcrypt error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Password verification error: {e}")

    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    })

    response.set_cookie(
        key="auth-token",
        value=token,
        httponly=True,
        secure=settings.node_env == "production",
        samesite="strict",
        max_age=settings.access_token_expire_minutes * 60,
    )

    # Log event to MongoDB (fire-and-forget, don't block login)
    import asyncio
    asyncio.create_task(event_repository.log_event("user_login", user.id, {"email": user.email}))

    print(f"DEBUG: Login successful for {user.email}")
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "points": getattr(user, "points", 0),
            "streak_days": getattr(user, "streakDays", 0),
            "teacher_request_status": user.teacher_request_status.value if user.teacher_request_status else None,
        }
    }

@app.post("/api/auth/logout", tags=["Auth"])
async def logout(http_request: Request, response: Response, token_data: TokenData = Depends(verify_token)):
    """Logout user"""
    try:
        r = await rate_limiter._get_redis()
        if r:
            token = http_request.cookies.get("auth-token")
            if token:
                exp = int(token_data.exp.timestamp())
                ttl = max(exp - int(datetime.now(timezone.utc).timestamp()), 0)
                if ttl > 0:
                    await r.setex(f"token_blacklist:{token}", ttl, "1")
    except Exception:
        pass
    
    response.delete_cookie(
        key="auth-token",
        path="/",
        secure=settings.node_env == "production",
        samesite="lax",
        httponly=True,
    )
    
    await event_repository.log_event(
        "user_logout",
        token_data.user_id,
        {"email": token_data.email}
    )
    
    return {"success": True, "message": "Logged out successfully"}

# ============================================
# Routes - Users
# ============================================

@app.get("/api/users/profile", tags=["Users"])
async def get_profile(token_data: TokenData = Depends(verify_token)):
    """Get current user profile"""
    user = await user_repository.get_by_id(token_data.user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "user": user.to_dict()}

@app.put("/api/users/profile", tags=["Users"])
async def update_profile(
    request: ProfileUpdate,
    token_data: TokenData = Depends(verify_token)
):
    """Update current user profile"""
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
        from infrastructure.adapters.output.postgres.connection import PostgresConnection
        query = "UPDATE users SET full_name = %s, email = %s, password_hash = %s, avatar_url = %s, bio = %s WHERE id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (user.full_name, user.email, user.password_hash, user.avatar_url, user.bio, user.id))
            
        await event_repository.log_event("profile_updated", user.id, {"email": user.email})
        return {"success": True, "message": "Profile updated successfully", "user": user.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/by-public-id/{public_id}", tags=["Users"])
async def get_user_by_public_id(public_id: str, token_data: Optional[TokenData] = Depends(verify_token_optional)):
    """Get user by public UUID"""
    user = await user_repository.get_by_public_id(public_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.to_dict()
    user_data.pop("password_hash", None)
    return {"success": True, "user": user_data}

@app.get("/api/users/{user_id}", tags=["Users"])
async def get_user(user_id: int, token_data: TokenData = Depends(verify_token)):
    """Get user by ID"""
    user = await user_repository.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't expose password hash
    user_data = user.to_dict()
    user_data.pop("password_hash", None)
    return {"success": True, "user": user_data}

@app.get("/api/users/search", tags=["Users"])
async def search_users(q: str = "", token_data: TokenData = Depends(verify_token)):
    """Search users by name"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    if not q:
        return {"success": True, "users": []}
    query = """
        SELECT id, email, full_name, role, avatar_url, bio, points, streak_days
        FROM users
        WHERE LOWER(full_name) LIKE LOWER(%s)
        ORDER BY full_name ASC
        LIMIT 20
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

# ============================================
# Routes - Recommendations (AI/ML)
# ============================================

@app.get("/api/recommendations", tags=["AI/ML"])
async def get_recommendations(token_data: TokenData = Depends(verify_token)):
    """Get personalized module recommendations"""
    use_case = GetRecommendationsUseCase(ai_service, module_repository, event_repository)
    result = await use_case.execute(token_data.user_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@app.get("/api/learning-path", tags=["AI/ML"])
async def get_learning_path(token_data: TokenData = Depends(verify_token)):
    """Detect student's optimal learning path"""
    path = await ai_service.detect_learning_path(token_data.user_id)
    return {"success": True, "learning_path": path}

@app.get("/api/performance-prediction/{module_id}", tags=["AI/ML"])
async def predict_performance(
    module_id: int,
    token_data: TokenData = Depends(verify_token)
):
    """Predict student performance in a module"""
    score = await ai_service.predict_student_performance(token_data.user_id, module_id)
    return {
        "success": True,
        "prediction": {
            "module_id": module_id,
            "score": score,
            "confidence": 0.85
        }
    }

# ============================================
# Routes - AI Analytics (Predictive System for Teachers)
# ============================================

class TutorAskRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    exercise_id: Optional[int] = None
    module_id: Optional[int] = None
    history: Optional[list] = []

class TutorHintRequest(BaseModel):
    exercise_id: int
    module_id: Optional[int] = None

class TutorExplainRequest(BaseModel):
    concept: str
    module_id: Optional[int] = None

class AnalyticsFilter(BaseModel):
    module_id: Optional[int] = None
    days: int = 30

@app.get("/api/analytics/student/{student_id}/metrics", tags=["AI Analytics"])
async def get_student_analytics(
    student_id: int,
    token_data: TokenData = Depends(verify_teacher),
):
    """Get full predictive metrics for a specific student"""
    profile = await behavioral_repo.get_student_behavioral_profile(student_id)
    metrics = await student_predictor.predict_metrics(profile)
    insights = await student_predictor.get_insights(profile)

    return {
        "success": True,
        "student_id": student_id,
        "behavioral_profile": profile,
        "predictions": metrics,
        "insights": insights,
    }

@app.get("/api/analytics/class/predictions", tags=["AI Analytics"])
async def get_class_predictions(
    days: int = 30,
    module_id: Optional[int] = None,
    token_data: TokenData = Depends(verify_teacher),
):
    """Get predictions for all students in the teacher's classes"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection

    with PostgresConnection.get_cursor() as cursor:
        if module_id:
            cursor.execute("""
                SELECT DISTINCT e.student_id FROM enrollments e
                JOIN modules m ON e.module_id = m.id
                WHERE m.teacher_id = %s AND e.module_id = %s
                  AND e.status IN ('active', 'completed')
            """, (token_data.user_id, module_id))
        else:
            cursor.execute("""
                SELECT DISTINCT student_id FROM (
                    SELECT e.student_id FROM enrollments e
                    JOIN modules m ON e.module_id = m.id
                    WHERE m.teacher_id = %s AND e.status IN ('active', 'completed')
                    UNION
                    SELECT ce.student_id FROM class_enrollments ce
                    JOIN classes c ON ce.class_id = c.id
                    WHERE c.teacher_id = %s AND ce.status = 'approved'
                ) AS all_students
            """, (token_data.user_id, token_data.user_id))
        student_rows = cursor.fetchall()

    if not student_rows:
        return {"success": True, "students": [], "summary": {}}

    results = []
    for (sid,) in student_rows:
        try:
            profile = await behavioral_repo.get_student_behavioral_profile(sid)
            metrics = await student_predictor.predict_metrics(profile)
            results.append({
                "student_id": sid,
                **metrics,
            })
        except Exception as e:
            print(f"[WARN] Failed to predict for student {sid}: {e}")
            results.append({
                "student_id": sid,
                "dropout_risk": 0.0,
                "performance_score": 0.0,
                "engagement_score": 0.0,
                "frustration_level": 0,
                "performance_label": "unknown",
                "dropout_risk_label": "low",
                "frustration_label": "baja",
            })

    try:
        classification = await student_predictor.classify_students([
            await behavioral_repo.get_student_behavioral_profile(r["student_id"])
            for r in results
        ])
    except Exception as e:
        print(f"[WARN] classify_students failed: {e}")
        classification = {"at_risk": [], "excellent": []}

    avg_dropout = sum(r["dropout_risk"] for r in results) / len(results) if results else 0
    avg_performance = sum(r["performance_score"] for r in results) / len(results) if results else 0
    avg_engagement = sum(r["engagement_score"] for r in results) / len(results) if results else 0

    return {
        "success": True,
        "students": results,
        "summary": {
            "total_students": len(results),
            "avg_dropout_risk": round(avg_dropout, 4),
            "avg_performance": round(avg_performance, 4),
            "avg_engagement": round(avg_engagement, 4),
            "at_risk_count": len(classification["at_risk"]),
            "excellent_count": len(classification["excellent"]),
        },
        "classification": classification,
    }

@app.get("/api/analytics/student/{student_id}/risk-factors", tags=["AI Analytics"])
async def get_student_risk_factors(
    student_id: int,
    token_data: TokenData = Depends(verify_teacher),
):
    """Get detailed risk factors for a student"""
    profile = await behavioral_repo.get_student_behavioral_profile(student_id)
    insights = await student_predictor.get_insights(profile)

    risk_factors = []
    if profile["session_days_30d"] < 3:
        risk_factors.append({
            "factor": "poca_frecuencia",
            "severity": "alta",
            "description": "El estudiante ha accedido menos de 3 días en el último mes.",
        })
    if profile["error_rate"] > 0.4:
        risk_factors.append({
            "factor": "alta_tasa_error",
            "severity": "alta",
            "description": f"Tasa de error del {round(profile['error_rate'] * 100)}% en sus intentos.",
        })
    if profile["frustration_signals_30d"] > 5:
        risk_factors.append({
            "factor": "frustracion_frecuente",
            "severity": "media",
            "description": f"{profile['frustration_signals_30d']} señales de frustración en 30 días.",
        })
    if profile["total_exercise_attempts_30d"] < 5:
        risk_factors.append({
            "factor": "poca_practica",
            "severity": "media",
            "description": "Menos de 5 intentos de ejercicios en el último mes.",
        })
    if profile["engagement_score"] < 0.3:
        risk_factors.append({
            "factor": "bajo_engagement",
            "severity": "alta",
            "description": f"Puntuación de engagement muy baja: {profile['engagement_score']}.",
        })

    return {
        "success": True,
        "student_id": student_id,
        "risk_factors": risk_factors,
        "insights": insights,
        "profile_summary": {
            k: profile[k] for k in [
                "session_days_30d", "total_time_minutes_30d",
                "total_exercise_attempts_30d", "error_rate",
                "frustration_signals_30d", "engagement_score",
            ]
        },
    }

@app.get("/api/analytics/dashboard", tags=["AI Analytics"])
async def get_analytics_dashboard(
    days: int = 30,
    token_data: TokenData = Depends(verify_teacher),
):
    """Get the full analytics dashboard for teachers"""
    class_preds = None
    try:
        class_preds = await get_class_predictions(days=days, token_data=token_data)
    except Exception as e:
        print(f"[WARN] get_class_predictions failed: {e}")
        class_preds = {"success": True, "students": [], "summary": {}}

    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    daily_activity = []
    frustration_trend = []
    try:
        db = await behavioral_repo.get_db()
        if db is not None:
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            daily_activity = list(db.behavioral_events.aggregate([
                {"$match": {"timestamp": {"$gte": week_ago}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "count": {"$sum": 1},
                }},
                {"$sort": {"_id": 1}},
            ]))
            frustration_trend = list(db.frustration_signals.aggregate([
                {"$match": {"timestamp": {"$gte": week_ago}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "count": {"$sum": 1},
                }},
                {"$sort": {"_id": 1}},
            ]))
    except Exception as e:
        print(f"[WARN] MongoDB analytics fetch: {e}")

    return {
        "success": True,
        "class_predictions": class_preds,
        "daily_activity": daily_activity,
        "frustration_trend": frustration_trend,
    }

# ============================================
# Routes - Intelligent Tutor (Conversational AI for Students)
# ============================================

@app.post("/api/tutor/ask", tags=["Intelligent Tutor"])
async def tutor_ask(
    request: TutorAskRequest,
    token_data: Optional[TokenData] = Depends(verify_token),
):
    """Ask the intelligent tutor a question (with Dialogflow fallback)"""
    user_id = token_data.user_id if token_data else None
    session_id = request.session_id or f"tutor_{user_id or 'anon'}"

    student_profile = None
    if user_id:
        student_profile = await behavioral_repo.get_student_behavioral_profile(user_id)
        metrics = await student_predictor.predict_metrics(student_profile)
        student_profile.update(metrics)

    dialogflow_result = None
    try:
        dialogflow_result = await ai_service.chat_with_dialogflow(session_id, request.message)
    except Exception as e:
        print(f"[Tutor] Dialogflow fallback trigger: {e}")

    result = await intelligent_tutor.generate_response(
        message=request.message,
        student_profile=student_profile,
        exercise_data={"exercise_id": request.exercise_id, "module_id": request.module_id},
        dialogflow_result=dialogflow_result,
    )

    try:
        db = await behavioral_repo.get_db()
        db.tutor_interactions.insert_one({
            "user_id": user_id or 0,
            "session_id": session_id,
            "message": request.message,
            "response": result["response"],
            "source": result.get("source", "tutor"),
            "intent": result.get("intent", "unknown"),
            "student_level": result.get("student_level", "beginner"),
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception as e:
        print(f"[Tutor] Log error: {e}")

    return {
        "success": True,
        **result,
        "session_id": session_id,
        "user_id": user_id,
    }

@app.post("/api/tutor/hint", tags=["Intelligent Tutor"])
async def tutor_hint(
    request: TutorHintRequest,
    token_data: TokenData = Depends(verify_token),
):
    """Get a contextual hint for an exercise"""
    student_profile = None
    try:
        student_profile = await behavioral_repo.get_student_behavioral_profile(token_data.user_id)
        metrics = await student_predictor.predict_metrics(student_profile)
        student_profile.update(metrics)
    except Exception:
        pass

    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    exercise_data = None
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(
            "SELECT id, title, description, instructions, difficulty FROM exercises WHERE id = %s",
            (request.exercise_id,),
        )
        row = cursor.fetchone()
        if row:
            exercise_data = {
                "exercise_id": row[0], "title": row[1],
                "description": row[2], "instructions": row[3],
                "difficulty": row[4],
            }

    hint = await intelligent_tutor.generate_hint(
        request.exercise_id, exercise_data, student_profile,
    )

    await behavioral_repo.log_exercise_action(
        token_data.user_id, request.exercise_id, request.module_id or 0,
        "hint_requested",
    )

    return {
        "success": True,
        "hint": hint,
        "exercise": exercise_data,
    }

@app.post("/api/tutor/explain", tags=["Intelligent Tutor"])
async def tutor_explain(
    request: TutorExplainRequest,
    token_data: Optional[TokenData] = Depends(verify_token),
):
    """Explain a programming or robotics concept"""
    student_profile = None
    if token_data:
        try:
            student_profile = await behavioral_repo.get_student_behavioral_profile(token_data.user_id)
            metrics = await student_predictor.predict_metrics(student_profile)
            student_profile.update(metrics)
        except Exception:
            pass

    intent_data = intelligent_tutor.detect_intent(request.concept)
    level = await intelligent_tutor.get_student_level(student_profile)

    concept = intent_data.get("concept") or intelligent_tutor._detect_concept(request.concept)
    if concept:
        explanation = intelligent_tutor._get_adapted_explanation(concept, level)
    else:
        explanation = f"No encontré información específica sobre '{request.concept}'. ¿Puedes ser más específico? Puedo explicarte sobre variables, funciones, bucles, condicionales, listas, robótica y Python."

    return {
        "success": True,
        "concept": concept or request.concept,
        "explanation": explanation,
        "student_level": level,
    }

@app.get("/api/tutor/student-level", tags=["Intelligent Tutor"])
async def tutor_student_level(
    token_data: TokenData = Depends(verify_token),
):
    """Get the detected level for the current student"""
    student_profile = None
    try:
        student_profile = await behavioral_repo.get_student_behavioral_profile(token_data.user_id)
        metrics = await student_predictor.predict_metrics(student_profile)
        student_profile.update(metrics)
    except Exception:
        pass

    level = await intelligent_tutor.get_student_level(student_profile)

    return {
        "success": True,
        "user_id": token_data.user_id,
        "student_level": level,
        "profile_summary": {
            "passed_exercises_30d": student_profile.get("passed_exercises_30d", 0) if student_profile else 0,
            "performance_score": student_profile.get("performance_score", 0.5) if student_profile else 0.5,
            "engagement_score": student_profile.get("engagement_score", 0.5) if student_profile else 0.5,
        } if student_profile else None,
    }

@app.post("/api/tutor/feedback", tags=["Intelligent Tutor"])
async def tutor_feedback(
    request: Request,
    token_data: TokenData = Depends(verify_token),
):
    """Log tutor feedback (helpful/not helpful)"""
    body = await request.json()
    helpful = body.get("helpful", True)
    message = body.get("message", "")

    try:
        db = await behavioral_repo.get_db()
        db.tutor_feedback.insert_one({
            "user_id": token_data.user_id,
            "helpful": helpful,
            "message": message,
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception as e:
        print(f"[Tutor] Feedback log error: {e}")

    return {"success": True}

@app.post("/api/analytics/train", tags=["AI Analytics"])
async def train_predictive_models(
    token_data: TokenData = Depends(verify_admin),
):
    """Retrain predictive models with real data from MongoDB"""
    result = student_predictor.train_on_real_data(behavioral_repo)
    return {"success": True, "training_result": result}

# ============================================
# Routes - Chatbot (Dialogflow)
# ============================================

@app.post("/api/chatbot/public", tags=["Chatbot"])
async def chat_public(request: PublicChatRequest, http_request: Request):
    """Chat with Dialogflow agent (no auth required, for anonymous users)"""
    await rate_limiter.check_by_ip(http_request, "public_chat", max_requests=20, window_seconds=60)
    session_id = request.session_id or f"anon_{datetime.now(timezone.utc).timestamp()}"

    dialogflow_response = None
    try:
        dialogflow_response = await ai_service.chat_with_dialogflow(session_id, request.message)
    except Exception:
        pass

    if dialogflow_response and "Dialogflow not configured" not in dialogflow_response and "Error" not in dialogflow_response and not ai_service.is_fallback_response(dialogflow_response):
        return {"success": True, "message": dialogflow_response, "session_id": session_id}

    # Dialogflow fallback — try Ollama directly first
    if ai_service.is_fallback_response(dialogflow_response or ""):
        try:
            ollama_response = await ai_tutor_service.answer_question(
                message=request.message,
                student_level="beginner",
            )
            if ollama_response and len(ollama_response) > 10:
                return {
                    "success": True,
                    "message": ollama_response,
                    "session_id": session_id,
                    "source": "ollama",
                }
        except Exception as e:
            print(f"[Ollama fallback error] {e}")

    # Fallback: IntelligentTutor if Ollama didn't produce a response
    tutor_result = await intelligent_tutor.generate_response(
        message=request.message,
        student_profile=None,
        dialogflow_result=dialogflow_response,
    )

    return {
        "success": True,
        "message": tutor_result["response"],
        "session_id": session_id,
        "source": tutor_result.get("source", "tutor"),
    }

@app.post("/api/chatbot", tags=["Chatbot"])
async def chat(
    request: ChatRequest,
    token_data: TokenData = Depends(verify_token)
):
    """Chat with Dialogflow agent with intelligent fallback"""
    session_id = f"user_{token_data.user_id}_session"

    student_profile = None
    try:
        student_profile = await behavioral_repo.get_student_behavioral_profile(token_data.user_id)
        metrics = await student_predictor.predict_metrics(student_profile)
        student_profile.update(metrics)
    except Exception:
        pass

    dialogflow_response = None
    try:
        dialogflow_response = await ai_service.chat_with_dialogflow(session_id, request.message)
    except Exception:
        pass

    if dialogflow_response and "Dialogflow not configured" not in dialogflow_response and "Error" not in dialogflow_response and not ai_service.is_fallback_response(dialogflow_response):
        await event_repository.log_chat_interaction(
            token_data.user_id,
            request.message,
            dialogflow_response,
            session_id
        )
        return {
            "success": True,
            "message": dialogflow_response,
            "source": "dialogflow",
        }

    response_text = ""
    tutor_result = {"source": "tutor", "intent": "general_chat"}

    # Third tier: Ollama fallback when Dialogflow didn't understand
    if ai_service.is_fallback_response(dialogflow_response or ""):
        try:
            ollama_response = await ai_tutor_service.answer_question(
                message=request.message,
                student_level="beginner",
                student_context=student_profile,
            )
            if ollama_response and len(ollama_response) > 10:
                response_text = ollama_response
                tutor_result = {"source": "ollama", "intent": "general_chat"}
        except Exception as e:
            print(f"[Ollama fallback error] {e}")

    if tutor_result.get("source") != "ollama":
        tutor_result = await intelligent_tutor.generate_response(
            message=request.message,
            student_profile=student_profile,
            dialogflow_result=dialogflow_response,
        )
        response_text = tutor_result["response"]

    # Fourth tier: OpenAI fallback if still no good response
    if tutor_result.get("source") != "ollama" and tutor_result.get("intent") in ("general_chat", "fallback") and settings.openai_api_key:
        try:
            import openai
            openai.api_key = settings.openai_api_key
            sys_prompt = f"""Eres un tutor amigable de RoboLearn, una plataforma educativa de programación y robótica.
El estudiante tiene nivel {tutor_result.get('student_level', 'beginner')}.
Contexto: {json.dumps(student_profile or {}, default=str)[:500]}
Responde de forma breve, clara y en español. Si la consulta no es educativa, redirige amablemente al temario."""
            ai_res = await asyncio.get_event_loop().run_in_executor(None, lambda: openai.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": request.message},
                ],
                max_tokens=300,
                temperature=0.7,
            ))
            ai_text = ai_res.choices[0].message.content.strip()
            if ai_text and len(ai_text) > 10:
                response_text = ai_text
                tutor_result["source"] = "openai"
        except ImportError:
            pass
        except Exception as e:
            print(f"[OpenAI fallback error] {e}")

    await event_repository.log_chat_interaction(
        token_data.user_id,
        request.message,
        response_text,
        session_id
    )

    try:
        db = await behavioral_repo.get_db()
        db.tutor_interactions.insert_one({
            "user_id": token_data.user_id,
            "session_id": session_id,
            "message": request.message,
            "response": response_text,
            "source": tutor_result.get("source", "tutor"),
            "intent": tutor_result.get("intent", "unknown"),
            "student_level": tutor_result.get("student_level", "beginner"),
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception:
        pass

    return {
        "success": True,
        "message": response_text,
        "source": tutor_result.get("source", "tutor"),
    }

# ============================================
# Routes - Interactive Execution
# ============================================

@app.post("/api/execute-code", tags=["Interactive"])
async def execute_code(
    request: ExecuteRequest,
    http_request: Request,
    token_data: TokenData = Depends(verify_token),
):
    """Execute Python code for interactive exercises with security restrictions"""
    await rate_limiter.check_by_user(token_data.user_id, "execute", max_requests=30, window_seconds=60)
    
    import io
    import sys
    import ast
    import signal
    from contextlib import redirect_stdout
    
    # Restrict maximum code length
    if len(request.code) > 10000:
        return {
            "success": False,
            "output": "",
            "actions": [],
            "error": "Code exceeds maximum length of 10000 characters"
        }
    
    # Blacklisted patterns for basic security
    dangerous_patterns = [
        "import os", "from os", "import subprocess", "from subprocess",
        "import shutil", "from shutil", "import sys", "from sys",
        "__import__", "eval(", "exec(", "open(", "__builtins__",
        "import socket", "from socket", "import requests", "from requests",
        "import ctypes", "from ctypes", "import multiprocessing",
        "__reduce__", "__subclasshook__", "__init_subclass__",
        "__dir__", "__getattribute__", "__setattr__",
    ]
    
    for pattern in dangerous_patterns:
        if pattern in request.code:
            return {
                "success": False,
                "output": "",
                "actions": [],
                "error": f"Security: '{pattern}' is not allowed in this environment"
            }
    
    actions = []
    
    def jump():
        actions.append("jump")
        
    def forward(steps=1):
        actions.append(f"forward_{steps}")
    
    # Restricted builtins
    safe_builtins = {
        'print': print, 'len': len, 'range': range, 'int': int,
        'float': float, 'str': str, 'bool': bool, 'list': list,
        'dict': dict, 'tuple': tuple, 'set': set, 'type': type,
        'True': True, 'False': False, 'None': None,
        'abs': abs, 'max': max, 'min': min, 'sum': sum,
        'sorted': sorted, 'reversed': reversed, 'enumerate': enumerate,
        'zip': zip, 'map': map, 'filter': filter, 'all': all, 'any': any,
        'round': round, 'isinstance': isinstance, 'hasattr': hasattr,
        'getattr': getattr, 'setattr': setattr,
        'ValueError': ValueError, 'TypeError': TypeError,
        'KeyError': KeyError, 'IndexError': IndexError,
        'StopIteration': StopIteration, 'Exception': Exception,
    }
    
    env = {
        "jump": jump,
        "forward": forward,
        "__builtins__": safe_builtins
    }
    
    f = io.StringIO()
    error = None
    
    try:
        # Validate AST before execution
        try:
            ast.parse(request.code)
        except SyntaxError as e:
            return {
                "success": False,
                "output": "",
                "actions": [],
                "error": f"Syntax Error: {e}"
            }
        
        with redirect_stdout(f):
            exec(request.code, env)
    except Exception as e:
        error = str(e)
        
    return {
        "success": error is None,
        "output": f.getvalue(),
        "actions": actions,
        "error": error
    }

# ============================================
# Routes - Exercise Submission & Grading
# ============================================

@app.post("/api/exercises/submit", tags=["Exercises"])
async def submit_exercise(
    request: ExerciseSubmit,
    token_data: TokenData = Depends(verify_token)
):
    """Submit an exercise attempt, grade it, and track attempts"""
    student_id = token_data.user_id

    if request.is_class_exercise:
        return await _submit_class_exercise(request, student_id)

    # --- Global exercise flow ---
    query = "SELECT id, module_id, solution_output, solution_type, test_code, title, points, lesson_id FROM exercises WHERE id = %s"
    exercise = None
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (request.exercise_id,))
        row = cursor.fetchone()
        if row:
            exercise = {
                "id": row[0], "module_id": row[1], "solution_output": row[2],
                "solution_type": row[3] or "output", "test_code": row[4],
                "title": row[5], "points": row[6], "lesson_id": row[7]
            }

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    attempt_query = """
        SELECT attempt_count, passed FROM exercise_attempts
        WHERE student_id = %s AND exercise_id = %s
        ORDER BY submitted_at DESC LIMIT 1
    """
    prev_attempts = 0
    already_passed = False
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(attempt_query, (student_id, request.exercise_id))
        row = cursor.fetchone()
        if row:
            prev_attempts = row[0] or 0
            already_passed = row[1]

    if already_passed:
        return {"success": True, "passed": True, "message": "Ya habías resuelto este ejercicio", "attempts": prev_attempts}

    grading_result = await sandbox_service.execute_and_compare(
        code=request.code,
        expected_output=exercise["solution_output"],
        solution_type=exercise["solution_type"],
        test_code=exercise["test_code"],
    )
    passed = grading_result["passed"]
    score = grading_result["score"]
    error = grading_result.get("error")
    output = grading_result.get("output", "")

    insert_query = """
        INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count)
        SELECT %s, %s, %s, %s, COALESCE(MAX(attempt_count), 0) + 1
        FROM exercise_attempts WHERE student_id = %s AND exercise_id = %s
        ON CONFLICT (student_id, exercise_id, attempt_count) DO NOTHING
        RETURNING attempt_count
    """
    attempt_count = 1
    for _ in range(3):
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(insert_query, (student_id, request.exercise_id, passed, score, student_id, request.exercise_id))
            result = cursor.fetchone()
            if result:
                attempt_count = result[0]
                break

    if passed:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s",
                          (exercise["points"], student_id))

        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO progress (student_id, module_id, completed_exercises, total_exercises, points_earned, percentage, last_activity)
                VALUES (%s, %s, 1, (SELECT COUNT(*) FROM exercises WHERE module_id = %s), %s,
                    (SELECT ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM exercises WHERE module_id = %s) * 100, 2) FROM exercise_attempts WHERE student_id = %s AND exercise_id IN (SELECT id FROM exercises WHERE module_id = %s) AND passed = TRUE), NOW())
                ON CONFLICT (student_id, module_id) DO UPDATE SET
                    completed_exercises = (SELECT COUNT(*) FROM exercise_attempts WHERE student_id = %s AND exercise_id IN (SELECT id FROM exercises WHERE module_id = %s) AND passed = TRUE),
                    points_earned = progress.points_earned + %s,
                    percentage = (SELECT ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM exercises WHERE module_id = %s) * 100, 2) FROM exercise_attempts WHERE student_id = %s AND exercise_id IN (SELECT id FROM exercises WHERE module_id = %s) AND passed = TRUE),
                    last_activity = NOW()
            """, (student_id, request.module_id, request.module_id, exercise["points"],
                  request.module_id, student_id, request.module_id,
                  student_id, request.module_id, exercise["points"],
                  request.module_id, student_id, request.module_id))

        lesson_id = exercise.get("lesson_id")
        if lesson_id:
            with PostgresConnection.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM exercises WHERE lesson_id = %s", (lesson_id,))
                total_in_lesson = cursor.fetchone()[0] or 0
                cursor.execute("""
                    SELECT COUNT(*) FROM exercise_attempts ea
                    JOIN exercises e ON e.id = ea.exercise_id
                    WHERE e.lesson_id = %s AND ea.student_id = %s AND ea.passed = TRUE
                """, (lesson_id, student_id))
                passed_in_lesson = cursor.fetchone()[0] or 0
            if total_in_lesson > 0 and passed_in_lesson >= total_in_lesson:
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO lesson_completions (student_id, lesson_id, module_id)
                        VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
                    """, (student_id, lesson_id, request.module_id))

        await check_and_award_achievements(student_id)
        await event_repository.log_event("exercise_passed", student_id, {
            "exercise_id": request.exercise_id,
            "module_id": request.module_id,
            "attempts": attempt_count,
            "points_earned": exercise["points"]
        })

    can_view_solution = attempt_count >= 3 and not passed
    solution = None
    if can_view_solution or passed:
        solution = exercise.get("solution_output", "").replace("\\n", "\n")

    return {
        "success": True,
        "passed": passed,
        "score": score,
        "output": output if not error else None,
        "error": error,
        "attempts": attempt_count,
        "can_view_solution": can_view_solution,
        "solution": solution if (can_view_solution or passed) else None,
        "points_earned": exercise["points"] if passed else 0
    }


async def _submit_class_exercise(request: ExerciseSubmit, student_id: int):
    """Handle submission of a class exercise (stored in class_exercises table)"""
    module_id = request.class_module_id or request.module_id

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT ce.id, ce.solution_output, ce.solution_type, ce.test_code,
                   ce.title, ce.points
            FROM class_exercises ce
            WHERE ce.id = %s AND ce.class_module_id = %s
        """, (request.exercise_id, module_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Class exercise not found")
        exercise = {
            "id": row[0], "solution_output": row[1],
            "solution_type": row[2] or "output", "test_code": row[3],
            "title": row[4], "points": row[5] or 10,
        }

    # Previous attempts
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT attempt_count, passed FROM class_exercise_attempts
            WHERE student_id = %s AND class_exercise_id = %s
            ORDER BY submitted_at DESC LIMIT 1
        """, (student_id, request.exercise_id))
        row = cursor.fetchone()
    prev_attempts = row[0] if row else 0
    already_passed = row[1] if row else False

    if already_passed:
        return {"success": True, "passed": True, "message": "Ya habías resuelto este ejercicio", "attempts": prev_attempts}

    grading_result = await sandbox_service.execute_and_compare(
        code=request.code,
        expected_output=exercise["solution_output"],
        solution_type=exercise["solution_type"],
        test_code=exercise["test_code"],
    )
    passed = grading_result["passed"]
    score = grading_result["score"]
    error = grading_result.get("error")
    output = grading_result.get("output", "")

    insert_query = """
        INSERT INTO class_exercise_attempts (student_id, class_exercise_id, class_module_id, passed, score, attempt_count)
        SELECT %s, %s, %s, %s, %s, COALESCE(MAX(attempt_count), 0) + 1
        FROM class_exercise_attempts WHERE student_id = %s AND class_exercise_id = %s
        ON CONFLICT (student_id, class_exercise_id, attempt_count) DO NOTHING
        RETURNING attempt_count
    """
    attempt_count = 1
    for _ in range(3):
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(insert_query, (student_id, request.exercise_id, module_id, passed, score, student_id, request.exercise_id))
            result = cursor.fetchone()
            if result:
                attempt_count = result[0]
                break

    if passed:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s",
                          (exercise["points"], student_id))
        await check_and_award_achievements(student_id)
        await event_repository.log_event("exercise_passed", student_id, {
            "exercise_id": request.exercise_id,
            "module_id": module_id,
            "attempts": attempt_count,
            "points_earned": exercise["points"],
            "is_class_exercise": True,
        })

    can_view_solution = attempt_count >= 3 and not passed
    solution = None
    if can_view_solution or passed:
        solution = exercise.get("solution_output", "").replace("\\n", "\n")

    return {
        "success": True,
        "passed": passed,
        "score": score,
        "output": output if not error else None,
        "error": error,
        "attempts": attempt_count,
        "can_view_solution": can_view_solution,
        "solution": solution if (can_view_solution or passed) else None,
        "points_earned": exercise["points"] if passed else 0,
    }


@app.get("/api/exercises/{exercise_id}/attempts", tags=["Exercises"])
async def get_exercise_attempts(exercise_id: int, token_data: TokenData = Depends(verify_token)):
    """Get the student's attempt history for an exercise"""
    query = """
        SELECT attempt_count, passed, score, submitted_at
        FROM exercise_attempts
        WHERE student_id = %s AND exercise_id = %s
        ORDER BY submitted_at DESC
    """
    attempts = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, exercise_id))
        for row in cursor.fetchall():
            attempts.append({
                "attempt": row[0], "passed": row[1],
                "score": row[2], "submitted_at": row[3].isoformat() if row[3] else None
            })
    
    # Check if can view solution
    total_attempts = len(attempts)
    last_passed = any(a["passed"] for a in attempts)
    can_view = total_attempts >= 3 and not last_passed
    
    solution = None
    if can_view or last_passed:
        query_ex = "SELECT solution_output FROM exercises WHERE id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query_ex, (exercise_id,))
            row = cursor.fetchone()
            if row:
                solution = row[0]
    
    return {
        "success": True,
        "attempts": attempts,
        "total_attempts": total_attempts,
        "can_view_solution": can_view,
        "already_passed": last_passed,
        "solution": solution
    }

@app.get("/api/exercises/difficulty-analysis", tags=["Exercises"])
async def get_exercise_difficulty_analysis(token_data: TokenData = Depends(verify_teacher)):
    """Analyze exercise difficulty based on student performance and suggest adjustments"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT 
            e.id, e.title, e.difficulty as current_difficulty, e.points, e.module_id,
            m.title as module_title,
            COUNT(ea.id) as total_attempts,
            COALESCE(AVG(ea.score), 0) as avg_score,
            COUNT(CASE WHEN ea.passed = TRUE THEN 1 END) as passed_count,
            COUNT(DISTINCT ea.student_id) as unique_students
        FROM exercises e
        JOIN modules m ON e.module_id = m.id
        LEFT JOIN exercise_attempts ea ON e.id = ea.exercise_id
        WHERE m.teacher_id = %s OR %s IN (SELECT id FROM users WHERE role = 'admin')
        GROUP BY e.id, e.title, e.difficulty, e.points, e.module_id, m.title
        HAVING COUNT(ea.id) > 0
        ORDER BY CAST(AVG(ea.score) AS DECIMAL) ASC
    """
    suggestions = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, token_data.user_id))
        for row in cursor.fetchall():
            ex_id = row[0]
            title = row[1]
            current_diff = row[2]
            points = row[3]
            module_id = row[4]
            module_title = row[5]
            total_attempts = row[6] or 0
            avg_score = float(row[7] or 0)
            passed_count = row[8] or 0
            unique_students = row[9] or 0
            pass_rate = (passed_count / total_attempts * 100) if total_attempts > 0 else 0

            suggestion = None
            suggested_diff = current_diff
            if pass_rate < 30 and current_diff > 1:
                suggestion = {
                    "type": "too_hard",
                    "message": f"Ejercicio muy difícil: solo {round(pass_rate)}% de acierto en {total_attempts} intentos. Considera reducir dificultad de {current_diff} a {max(1, current_diff - 1)}.",
                    "alternative": f"Puedes agregar una versión más guiada o reducir la complejidad del código esperado."
                }
                suggested_diff = max(1, current_diff - 1)
            elif pass_rate > 85 and current_diff < 5:
                suggestion = {
                    "type": "too_easy",
                    "message": f"Ejercicio muy fácil: {round(pass_rate)}% de acierto. Considera subir dificultad de {current_diff} a {min(5, current_diff + 1)}.",
                    "alternative": f"Puedes agregar variantes que requieran lógica más compleja o combinar conceptos."
                }
                suggested_diff = min(5, current_diff + 1)
            elif unique_students >= 3 and avg_score < 50:
                suggestion = {
                    "type": "needs_review",
                    "message": f"Los estudiantes tienen dificultades (promedio {round(avg_score)}%). Revisa el enunciado o agrega ejercicios de refuerzo previos.",
                    "alternative": f"Considera agregar un ejercicio intermedio que sirva de puente antes de este."
                }

            if suggestion:
                suggestions.append({
                    "exercise_id": ex_id,
                    "title": title,
                    "module_title": module_title,
                    "module_id": module_id,
                    "current_difficulty": current_diff,
                    "suggested_difficulty": suggested_diff,
                    "pass_rate": round(pass_rate, 1),
                    "avg_score": round(avg_score, 1),
                    "total_attempts": total_attempts,
                    "unique_students": unique_students,
                    **suggestion
                })

    return {"success": True, "suggestions": suggestions}

# ============================================
# Routes - Module Completion
# ============================================

@app.post("/api/modules/complete", tags=["Modules"])
async def complete_module(
    request: ModuleComplete,
    token_data: TokenData = Depends(verify_token)
):
    """Mark a module as completed (manual completion by student)"""
    student_id = token_data.user_id
    module_id = request.module_id
    
    # Check enrollment
    enroll_query = "SELECT id, status FROM enrollments WHERE student_id = %s AND module_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(enroll_query, (student_id, module_id))
        enrollment = cursor.fetchone()
    
    if not enrollment:
        raise HTTPException(status_code=400, detail="Not enrolled in this module")
    
    if enrollment[1] == "completed":
        return {"success": True, "message": "Module already completed"}
    
    # Check all lessons are completed
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM lessons WHERE module_id = %s
        """, (module_id,))
        total_lessons = cursor.fetchone()[0] or 0
    
    if total_lessons > 0:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM lesson_completions
                WHERE module_id = %s AND student_id = %s
            """, (module_id, student_id))
            completed_lessons = cursor.fetchone()[0] or 0
        
        if completed_lessons < total_lessons:
            return {"success": False, "message": f"Completa todas las {total_lessons} lecciones primero ({completed_lessons}/{total_lessons})"}
    
    # Mark enrollment as completed
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            UPDATE enrollments SET status = 'completed', completed_at = NOW()
            WHERE student_id = %s AND module_id = %s
        """, (student_id, module_id))
    
    # Update progress
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO progress (student_id, module_id, percentage, is_completed, last_activity)
            VALUES (%s, %s, 100.0, TRUE, NOW())
            ON CONFLICT (student_id, module_id) DO UPDATE SET
                percentage = 100.0, is_completed = TRUE, last_activity = NOW()
        """, (student_id, module_id))
    
    # Add points for completion
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("UPDATE users SET points = COALESCE(points, 0) + 50 WHERE id = %s", (student_id,))
    
    # Check and award achievements
    await check_and_award_achievements(student_id)
    
    # Log event
    await event_repository.log_event("module_completed", student_id, {"module_id": module_id, "manual": True})
    
    return {"success": True, "message": "Module completed!", "points_earned": 50}

@app.get("/api/modules/{module_id}/progress", tags=["Modules"])
async def get_module_progress(module_id: int, token_data: TokenData = Depends(verify_token)):
    """Get the student's progress for a module"""
    query = """
        SELECT p.percentage, p.completed_exercises, p.total_exercises, 
               p.points_earned, p.is_completed, p.last_activity,
               e.status as enrollment_status
        FROM progress p
        JOIN enrollments e ON e.student_id = p.student_id AND e.module_id = p.module_id
        WHERE p.student_id = %s AND p.module_id = %s
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id, module_id))
        row = cursor.fetchone()
    
    if not row:
        # Check if enrolled without progress
        enroll_query = "SELECT status FROM enrollments WHERE student_id = %s AND module_id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(enroll_query, (token_data.user_id, module_id))
            enr = cursor.fetchone()
        
        if enr:
            return {
                "success": True,
                "progress": {
                    "percentage": 0, "completed_exercises": 0, "total_exercises": 0,
                    "points_earned": 0, "is_completed": False,
                    "enrollment_status": enr[0]
                }
            }
        
        # Not enrolled
        # Get total exercises count
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM exercises WHERE module_id = %s", (module_id,))
            total = cursor.fetchone()[0]
        
        return {
            "success": True,
            "progress": {
                "percentage": 0, "completed_exercises": 0, "total_exercises": total,
                "points_earned": 0, "is_completed": False, "enrollment_status": None
            }
        }
    
    return {
        "success": True,
        "progress": {
            "percentage": float(row[0]) if row[0] else 0,
            "completed_exercises": row[1] or 0,
            "total_exercises": row[2] or 0,
            "points_earned": row[3] or 0,
            "is_completed": row[4] or False,
            "last_activity": row[5].isoformat() if row[5] else None,
            "enrollment_status": row[6]
        }
    }

@app.get("/api/modules/{module_id}/lessons", tags=["Modules"])
async def get_module_lessons(module_id: int, token_data: TokenData = Depends(verify_token)):
    """Get all lessons for a module with exercise completion status"""
    student_id = token_data.user_id

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT id, title, theory_content, "order"
            FROM lessons WHERE module_id = %s ORDER BY "order" ASC
        """, (module_id,))
        lesson_rows = cursor.fetchall()

    lessons = []
    for row in lesson_rows:
        lesson_id, title, theory, order_num = row

        # Get exercises for this lesson
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT e.id, e.title, e.description, e.instructions, e.difficulty, e.points, e.solution_output,
                       COALESCE((SELECT passed FROM exercise_attempts WHERE student_id = %s AND exercise_id = e.id ORDER BY submitted_at DESC LIMIT 1), FALSE) as passed,
                       (SELECT attempt_count FROM exercise_attempts WHERE student_id = %s AND exercise_id = e.id ORDER BY submitted_at DESC LIMIT 1) as attempts
                FROM exercises e
                WHERE e.lesson_id = %s
                ORDER BY e."order" ASC
            """, (student_id, student_id, lesson_id))
            exercise_rows = cursor.fetchall()

        exercises = []
        for er in exercise_rows:
            exercises.append({
                "id": er[0], "title": er[1], "description": er[2],
                "instructions": er[3], "difficulty": er[4], "points": er[5],
                "solution": er[6], "passed": bool(er[7]),
                "attempts": er[8] or 0
            })

        # Check if lesson is completed
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM lesson_completions WHERE student_id = %s AND lesson_id = %s
            """, (student_id, lesson_id))
            lesson_done = cursor.fetchone() is not None

        # Count total and passed exercises
        total_ex = len(exercises)
        passed_ex = sum(1 for ex in exercises if ex["passed"])

        lessons.append({
            "id": lesson_id, "title": title, "theory": theory,
            "order": order_num, "completed": lesson_done,
            "total_exercises": total_ex, "passed_exercises": passed_ex,
            "exercises": exercises
        })

    # Get module info
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT title, lesson_count FROM modules WHERE id = %s", (module_id,))
        mod = cursor.fetchone()
        mod_title = mod[0] if mod else ""
        mod_lesson_count = mod[1] or 0

    total_lessons = len(lessons)
    completed_lessons = sum(1 for l in lessons if l["completed"])

    return {
        "success": True,
        "module_id": module_id,
        "module_title": mod_title,
        "lessons": lessons,
        "total_lessons": total_lessons or mod_lesson_count,
        "completed_lessons": completed_lessons,
        "all_completed": total_lessons > 0 and completed_lessons >= total_lessons
    }

@app.post("/api/lessons/{lesson_id}/complete", tags=["Lessons"])
async def complete_lesson(lesson_id: int, token_data: TokenData = Depends(verify_token)):
    """Mark a lesson as completed (for lessons without exercises)"""
    student_id = token_data.user_id
    from infrastructure.adapters.output.postgres.connection import PostgresConnection

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT module_id FROM lessons WHERE id = %s", (lesson_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Lesson not found")
        module_id = row[0]

        cursor.execute("""
            INSERT INTO lesson_completions (student_id, lesson_id, module_id)
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (student_id, lesson_id, module_id))

    return {"success": True, "message": "Lesson completed"}

# --- Module Lesson CRUD (for admin / teacher module editor) ---

@app.post("/api/modules/{module_id}/lessons", tags=["Modules"])
async def create_module_lesson(module_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Create a lesson in a module (teacher must own the module)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    body = await request.json()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        cursor.execute("""
            INSERT INTO lessons (module_id, title, theory_content, "order")
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (module_id, body.get("title", "Nueva Lección"), body.get("theory_content", ""), body.get("order", 0)))
        lesson_id = cursor.fetchone()[0]
        cursor.execute("UPDATE modules SET lesson_count = (SELECT COUNT(*) FROM lessons WHERE module_id = %s) WHERE id = %s", (module_id, module_id))
    return {"success": True, "lesson_id": lesson_id}

@app.put("/api/modules/{module_id}/lessons/{lesson_id}", tags=["Modules"])
async def update_module_lesson(module_id: int, lesson_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Update a lesson (teacher must own the module)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
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
            query = f"UPDATE lessons SET {', '.join(fields)} WHERE id = %s AND module_id = %s"
            cursor.execute(query, tuple(values))
    return {"success": True, "message": "Lesson updated"}

@app.delete("/api/modules/{module_id}/lessons/{lesson_id}", tags=["Modules"])
async def delete_module_lesson(module_id: int, lesson_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a lesson (teacher must own the module)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
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

@app.post("/api/modules/{module_id}/exercises", tags=["Modules"])
async def create_module_exercise(module_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Create an exercise in a module (teacher must own the module)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    body = await request.json()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        cursor.execute("""
            INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points,
                solution_output, solution_type, test_code, "order")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (module_id, body.get("lesson_id"), body.get("title", "Nuevo Ejercicio"),
              body.get("description", ""), body.get("instructions", ""),
              body.get("difficulty", 1), body.get("points", 10),
              body.get("solution_output"), body.get("solution_type", "output"),
              body.get("test_code"), body.get("order", 0)))
        exercise_id = cursor.fetchone()[0]
    return {"success": True, "exercise_id": exercise_id}

@app.put("/api/modules/{module_id}/exercises/{exercise_id}", tags=["Modules"])
async def update_module_exercise(module_id: int, exercise_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Update an exercise (teacher must own the module)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    body = await request.json()
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        fields = []; values = []
        for key in ("title", "description", "instructions", "difficulty", "points",
                     "solution_output", "solution_type", "test_code", "lesson_id"):
            if key in body:
                col = key
                fields.append(f"{col} = %s"); values.append(body[key])
        if "order" in body:
            fields.append('"order" = %s'); values.append(body["order"])
        if fields:
            values.extend([exercise_id, module_id])
            query = f"UPDATE exercises SET {', '.join(fields)} WHERE id = %s AND module_id = %s"
            cursor.execute(query, tuple(values))
    return {"success": True, "message": "Exercise updated"}

@app.delete("/api/modules/{module_id}/exercises/{exercise_id}", tags=["Modules"])
async def delete_module_exercise(module_id: int, exercise_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete an exercise (teacher must own the module)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT teacher_id FROM modules WHERE id = %s", (module_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        if row[0] != token_data.user_id and token_data.role != "admin":
            raise HTTPException(status_code=403, detail="Not your module")
        cursor.execute("DELETE FROM exercises WHERE id = %s AND module_id = %s", (exercise_id, module_id))
    return {"success": True, "message": "Exercise deleted"}

# ============================================
# Routes - Achievements
# ============================================

async def check_and_award_achievements(user_id: int):
    """Check all achievement criteria and award any newly earned ones"""
    try:
        # Get user's current achievements
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.id, a.criteria FROM achievements a
                JOIN user_achievements ua ON ua.achievement_id = a.id
                WHERE ua.user_id = %s
            """, (user_id,))
            earned_ids = {row[0] for row in cursor.fetchall()}
        
        # Get all achievements
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
                    cursor.execute(
                        "SELECT COUNT(*) FROM exercise_attempts WHERE student_id = %s AND passed = TRUE",
                        (user_id,)
                    )
                    total = cursor.fetchone()[0] or 0
                    if total >= count:
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
                        total = cursor.fetchone()[0] or 0
                        if total > 0:
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
                    total = cursor.fetchone()[0] or 0
                    if total >= count:
                        earned = True
            
            elif ach_type == "streak_days":
                count = criteria.get("count", 7)
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute(
                        "SELECT COALESCE(streak_days, 0) FROM users WHERE id = %s",
                        (user_id,)
                    )
                    streak = cursor.fetchone()[0] or 0
                    if streak >= count:
                        earned = True
            
            elif ach_type == "challenge_complete":
                count = criteria.get("count", 1)
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM challenge_attempts WHERE student_id = %s AND passed = TRUE",
                        (user_id,)
                    )
                    total = cursor.fetchone()[0] or 0
                    if total >= count:
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
                    total = cursor.fetchone()[0] or 0
                    if total >= count:
                        earned = True
            
            if earned:
                with PostgresConnection.get_cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_achievements (user_id, achievement_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING
                    """, (user_id, ach_id))
                    cursor.execute(
                        "UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s",
                        (points, user_id)
                    )
                new_achievements.append({"id": ach_id, "name": name})
        
        if new_achievements:
            await event_repository.log_event("achievements_awarded", user_id, {
                "count": len(new_achievements),
                "achievements": [a["name"] for a in new_achievements]
            })
        
        return new_achievements
    except Exception as e:
        print(f"[WARN] Achievement check error: {e}")
        return []

@app.get("/api/achievements", tags=["Achievements"])
async def list_achievements(token_data: TokenData = Depends(verify_token)):
    """List all achievements with user's earned status"""
    # Get all achievements
    query_ach = "SELECT id, name, description, icon, points, criteria FROM achievements ORDER BY id"
    achievements = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query_ach)
        for row in cursor.fetchall():
            achievements.append({
                "id": row[0], "name": row[1], "description": row[2],
                "icon": row[3] or "star", "points": row[4],
                "criteria": row[5]
            })
    
    # Get user's earned achievements
    query_user = """
        SELECT ua.achievement_id, ua.earned_at
        FROM user_achievements ua WHERE ua.user_id = %s
    """
    earned = {}
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query_user, (token_data.user_id,))
        for row in cursor.fetchall():
            earned[row[0]] = row[1].isoformat() if row[1] else None
    
    result = []
    for ach in achievements:
        result.append({
            **ach,
            "is_locked": ach["id"] not in earned,
            "earned_at": earned.get(ach["id"])
        })
    
    return {"success": True, "achievements": result}

@app.get("/api/achievements/recent", tags=["Achievements"])
async def get_recent_achievements(token_data: TokenData = Depends(verify_token)):
    """Get recent achievements for the current user"""
    query = """
        SELECT a.id, a.name, a.description, a.icon, a.points, ua.earned_at
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = %s
        ORDER BY ua.earned_at DESC
        LIMIT 10
    """
    achievements = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id,))
        for row in cursor.fetchall():
            achievements.append({
                "id": row[0], "name": row[1], "description": row[2],
                "icon": row[3] or "star", "points": row[4],
                "earned_at": row[5].isoformat() if row[5] else None
            })
    
    return {"success": True, "achievements": achievements}

# ============================================
# Routes - Modules
# ============================================

@app.get("/api/modules", tags=["Modules"])
async def list_modules():
    """List all published modules (including global)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT m.id, m.title, m.description, m.theory_content, m.teacher_id,
               m.status, m."order", m.is_published, m.is_global, m.difficulty, m.lesson_count,
               m.created_at, u.full_name as teacher_name
        FROM modules m
        LEFT JOIN users u ON m.teacher_id = u.id
        WHERE m.is_published = TRUE AND m.status = 'approved'
        ORDER BY m."order" ASC
    """
    modules = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            modules.append({
                "id": row[0], "title": row[1], "description": row[2],
                "theory_content": row[3], "teacher_id": row[4],
                "status": row[5], "order": row[6], "is_published": row[7],
                "is_global": row[8], "difficulty": row[9], "lesson_count": row[10],
                "created_at": row[11].isoformat() if row[11] else None,
                "teacher_name": row[12]
            })
    return {"success": True, "modules": modules}

@app.get("/api/modules/search", tags=["Modules"])
async def search_modules(q: str = "", token_data: TokenData = Depends(verify_token)):
    """Search modules dynamically"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT m.id, m.title, m.description, m.teacher_id, u.full_name as teacher_name 
        FROM modules m
        JOIN users u ON m.teacher_id = u.id
        WHERE m.is_published = TRUE AND m.status = 'approved'
        AND (m.title ILIKE %s OR u.full_name ILIKE %s)
        ORDER BY m.title ASC
    """
    
    results = []
    search_term = f"%{q}%"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (search_term, search_term))
        rows = cursor.fetchall()
        for row in rows:
            results.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "teacher_id": row[3],
                "teacher_name": row[4]
            })
            
    return {"success": True, "results": results}

@app.get("/api/modules/enrolled", tags=["Modules"])
async def get_enrolled_modules(token_data: TokenData = Depends(verify_token)):
    """Get modules the student is enrolled in"""
    # Fetch enrollments
    enrollments = await enrollment_repository.get_by_student(token_data.user_id)
    
    # We want to return module details as well. We can do this by getting each module.
    # A more efficient way is a custom query or joining, but here we can just loop as it's a small scale.
    # We'll return full module info along with enrollment status.
    result = []
    for enr in enrollments:
        module = await module_repository.get_by_id(enr.module_id)
        if module:
            mod_dict = module.to_dict()
            mod_dict["enrollment_status"] = enr.status
            mod_dict["enrolled_at"] = enr.enrolled_at.isoformat() if enr.enrolled_at else None
            result.append(mod_dict)
            
    return {"success": True, "modules": result}

@app.get("/api/modules/{module_id}", tags=["Modules"])
async def get_module(module_id: int):
    """Get module by ID with lessons and exercises"""
    module = await module_repository.get_by_id(module_id)
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    result = module.to_dict()
    
    # Include lessons with exercises
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT id, title, theory_content, "order"
            FROM lessons WHERE module_id = %s ORDER BY "order" ASC
        """, (module_id,))
        lesson_rows = cursor.fetchall()
    
    lessons = []
    for row in lesson_rows:
        lesson_id, title, theory, order_num = row
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, description, instructions, difficulty, points, solution_output, solution_type, "order"
                FROM exercises WHERE lesson_id = %s ORDER BY "order" ASC
            """, (lesson_id,))
            ex_rows = cursor.fetchall()
        
        exercises = []
        for er in ex_rows:
            exercises.append({
                "id": er[0], "title": er[1], "description": er[2],
                "instructions": er[3], "difficulty": er[4], "points": er[5],
                "solution_output": er[6], "solution_type": er[7], "order": er[8]
            })
        
        lessons.append({
            "id": lesson_id, "title": title, "theory": theory,
            "order": order_num, "exercises": exercises
        })
    
    result["lessons"] = lessons
    return {"success": True, "module": result}

@app.get("/api/modules/{module_id}/exercises", tags=["Modules"])
async def get_module_exercises(module_id: int):
    """Get exercises for a module"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT id, module_id, title, description, theory_content, instructions, difficulty, points, "order"
        FROM exercises WHERE module_id = %s ORDER BY "order" ASC
    """
    exercises = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id,))
        rows = cursor.fetchall()
        for row in rows:
            exercises.append({
                "id": row[0],
                "module_id": row[1],
                "title": row[2],
                "description": row[3],
                "theory_content": row[4],
                "instructions": row[5],
                "difficulty": row[6],
                "points": row[7],
                "order": row[8]
            })
    return {"success": True, "exercises": exercises}

@app.get("/api/exercises", tags=["Exercises"])
async def get_all_exercises():
    """Get all exercises without theory content"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT e.id, e.module_id, e.title, e.description, e.instructions, e.difficulty, e.points, m.title as module_title
        FROM exercises e
        JOIN modules m ON e.module_id = m.id
        WHERE m.is_published = TRUE
        ORDER BY m."order", e."order" ASC
    """
    exercises = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            exercises.append({
                "id": row[0],
                "module_id": row[1],
                "title": row[2],
                "description": row[3],
                "instructions": row[4],
                "difficulty": row[5],
                "points": row[6],
                "module_title": row[7]
            })
    return {"success": True, "exercises": exercises}

@app.post("/api/modules", tags=["Modules"])
async def create_module(
    request: ModuleCreate,
    token_data: TokenData = Depends(verify_teacher)
):
    """Create a new module"""
    from domain.entities.module import Module, ContentStatus
    
    module = Module(
        id=None,
        title=request.title,
        description=request.description,
        teacher_id=token_data.user_id,
        status=ContentStatus.DRAFT,
        order=request.order,
        is_published=request.is_published
    )
    
    created_module = await module_repository.create(module)
    
    await event_repository.log_event(
        "module_created",
        token_data.user_id,
        {"module_id": created_module.id, "title": created_module.title}
    )
    
    return {"success": True, "module": created_module.to_dict()}

@app.put("/api/modules/{module_id}", tags=["Modules"])
async def update_module(
    module_id: int,
    request: ModuleUpdate,
    token_data: TokenData = Depends(verify_teacher)
):
    """Update a module"""
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

@app.delete("/api/modules/{module_id}", tags=["Modules"])
async def request_module_deletion(
    module_id: int,
    token_data: TokenData = Depends(verify_teacher)
):
    """Request module deletion (requires admin approval)"""
    from domain.entities.module import ContentStatus
    
    module = await module_repository.get_by_id(module_id)
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    if module.teacher_id != token_data.user_id and token_data.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this module")
        
    module.status = ContentStatus.PENDING_DELETION
    await module_repository.update(module)
    
    await event_repository.log_event(
        "module_deletion_requested",
        token_data.user_id,
        {"module_id": module.id}
    )
    
    return {"success": True, "message": "Module deletion requested and pending admin approval"}

@app.post("/api/modules/{module_id}/enroll", tags=["Modules"])
async def enroll_module(
    module_id: int,
    token_data: TokenData = Depends(verify_token)
):
    """Enroll in a module"""
    use_case = EnrollStudentUseCase(user_repository, module_repository, event_repository, enrollment_repository)
    result = await use_case.execute(token_data.user_id, module_id)
    
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    
    return result

# ============================================
# Routes - Events/Metrics
# ============================================

@app.post("/api/events", tags=["Metrics"])
async def log_event(
    event_type: str,
    data: dict,
    token_data: TokenData = Depends(verify_token)
):
    """Log an event"""
    event_id = await event_repository.log_event(event_type, token_data.user_id, data)
    return {"success": True, "event_id": event_id}

@app.get("/api/user-history", tags=["Metrics"])
async def get_user_history(token_data: TokenData = Depends(verify_token)):
    """Get user's event history"""
    history = await event_repository.get_user_events(token_data.user_id)
    return {"success": True, "history": history}

# ============================================
# Routes - Teacher
# ============================================

@app.get("/api/teacher/dashboard", tags=["Teacher"])
async def get_teacher_dashboard(token_data: TokenData = Depends(verify_teacher)):
    """Get teacher dashboard metrics"""
    use_case = TeacherDashboardUseCase(teacher_repository)
    result = await use_case.get_metrics(token_data.user_id)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return result

@app.get("/api/teacher/students", tags=["Teacher"])
async def get_teacher_students(token_data: TokenData = Depends(verify_teacher)):
    """Get students enrolled in teacher's modules"""
    use_case = TeacherDashboardUseCase(teacher_repository)
    result = await use_case.get_students(token_data.user_id)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return result

@app.get("/api/teacher/students/{student_id}", tags=["Teacher"])
async def get_teacher_student_details(student_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Get specific student details for a teacher"""
    use_case = TeacherDashboardUseCase(teacher_repository)
    result = await use_case.get_student_detail(token_data.user_id, student_id)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return result

@app.get("/api/teacher/alerts", tags=["Teacher"])
async def get_teacher_alerts(token_data: TokenData = Depends(verify_teacher)):
    """Get dynamic AI alerts for the teacher dashboard"""
    use_case = GenerateAIAlertsUseCase(teacher_repository)
    result = await use_case.execute(token_data.user_id)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return result

# ============================================
# Routes - Admin
# ============================================

@app.get("/api/admin/users", tags=["Admin"])
async def get_all_users(token_data: TokenData = Depends(verify_admin)):
    """List all users"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = "SELECT id, email, full_name, role, is_active, points, streak_days, created_at FROM users ORDER BY created_at DESC"
    
    users = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            users.append({
                "id": row[0],
                "email": row[1],
                "full_name": row[2],
                "role": row[3],
                "is_active": row[4],
                "points": row[5],
                "streak_days": row[6],
                "created_at": row[7].isoformat() if row[7] else None
            })
            
    return {"success": True, "users": users}

@app.put("/api/admin/users/{user_id}/role", tags=["Admin"])
async def update_user_role(
    user_id: int, 
    request: UserRoleUpdate, 
    token_data: TokenData = Depends(verify_admin)
):
    """Update user role"""
    from domain.entities.user import UserRole
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    try:
        valid_role = UserRole(request.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    query = "UPDATE users SET role = %s WHERE id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (valid_role.value, user_id))
        
    return {"success": True, "message": "User role updated successfully"}

@app.get("/api/admin/teachers/pending", tags=["Admin"])
async def get_pending_teachers(token_data: TokenData = Depends(verify_admin)):
    """List users who requested to be teachers"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT id, email, full_name, teacher_request_status, created_at
        FROM users WHERE teacher_request_status = 'pending'
        ORDER BY created_at DESC
    """
    requests = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            requests.append({
                "id": row[0], "email": row[1], "name": row[2],
                "status": row[3], "date": row[4].strftime("%Y-%m-%d") if row[4] else ""
            })
    return {"success": True, "requests": requests}

@app.post("/api/admin/teachers/approve/{user_id}", tags=["Admin"])
async def approve_teacher(user_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve a teacher request"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            UPDATE users SET role = 'teacher', teacher_request_status = 'approved'
            WHERE id = %s AND teacher_request_status = 'pending'
        """, (user_id,))
    
    await event_repository.log_event("teacher_approved", token_data.user_id, {"user_id": user_id})
    return {"success": True, "message": f"Teacher {user_id} approved"}

@app.post("/api/admin/teachers/reject/{user_id}", tags=["Admin"])
async def reject_teacher(user_id: int, token_data: TokenData = Depends(verify_admin)):
    """Reject a teacher request"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            UPDATE users SET teacher_request_status = 'rejected'
            WHERE id = %s AND teacher_request_status = 'pending'
        """, (user_id,))
    
    return {"success": True, "message": f"Teacher {user_id} rejected"}

@app.post("/api/admin/modules/{module_id}/approve-deletion", tags=["Admin"])
async def approve_module_deletion(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve module deletion"""
    module = await module_repository.get_by_id(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    await module_repository.delete(module_id)
    
    await event_repository.log_event(
        "module_deleted",
        token_data.user_id,
        {"module_id": module_id, "title": module.title}
    )
    
    return {"success": True, "message": "Module deleted successfully"}

@app.post("/api/admin/modules/{module_id}/reject-deletion", tags=["Admin"])
async def reject_module_deletion(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Reject module deletion and set back to draft/approved"""
    from domain.entities.module import ContentStatus
    
    module = await module_repository.get_by_id(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    module.status = ContentStatus.DRAFT
    await module_repository.update(module)
    
    return {"success": True, "message": "Module deletion rejected, set to draft"}

# ============================================
# Routes - Dashboards (Student, Admin, Challenges)
# ============================================

@app.get("/api/dashboard/student", tags=["Student"])
async def get_student_dashboard(token_data: TokenData = Depends(verify_token)):
    """Get student dashboard data - fully synced with DB"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    student_id = token_data.user_id
    
    # 1. Progress Stats
    query_progress = """
        SELECT 
            COUNT(DISTINCT e.id) as total_modules,
            COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.id END) as completed_modules
        FROM enrollments e
        WHERE e.student_id = %s
    """
    
    # 2. Completed exercises count
    query_exercises = """
        SELECT COUNT(DISTINCT exercise_id) FROM exercise_attempts
        WHERE student_id = %s AND passed = TRUE
    """
    
    # 3. Total exercises available for enrolled modules
    query_total_ex = """
        SELECT COUNT(*) FROM exercises e
        JOIN enrollments en ON en.module_id = e.module_id
        WHERE en.student_id = %s AND en.status IN ('active', 'completed')
    """
    
    # 4. Recent Achievements
    query_achievements = """
        SELECT a.name, a.description, a.icon, ua.earned_at
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = %s
        ORDER BY ua.earned_at DESC
        LIMIT 3
    """
    
    # 5. Get user points and streak
    query_user = """
        SELECT points, streak_days FROM users WHERE id = %s
    """
    
    # 6. Get weekly activity from MongoDB events
    weekly_activity = [
        {"day": "Lun", "puntos": 0},
        {"day": "Mar", "puntos": 0},
        {"day": "Mié", "puntos": 0},
        {"day": "Jue", "puntos": 0},
        {"day": "Vie", "puntos": 0},
        {"day": "Sáb", "puntos": 0},
        {"day": "Dom", "puntos": 0},
    ]
    
    # Try to get real activity from MongoDB
    try:
        from datetime import timedelta
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        mongo_events = (await event_repository.get_db())["events"].aggregate([
            {"$match": {
                "user_id": student_id,
                "timestamp": {"$gte": week_ago}
            }},
            {"$group": {
                "_id": {"$dayOfWeek": "$timestamp"},
                "total_points": {"$sum": "$metadata.points_earned"}
            }}
        ])
        day_map = {2: "Lun", 3: "Mar", 4: "Mié", 5: "Jue", 6: "Vie", 7: "Sáb", 1: "Dom"}
        for ev in mongo_events:
            day_num = ev["_id"]
            day_name = day_map.get(day_num, "")
            for entry in weekly_activity:
                if entry["day"] == day_name:
                    entry["puntos"] = ev.get("total_points", 0) or 0
    except Exception as e:
        print(f"[WARN] MongoDB activity fetch failed: {e}")

    progress = {"completedLessons": 0, "totalLessons": 0, "currentModule": "Ninguno", "nextLesson": "Ninguno"}
    recent_achievements = []
    points = 0
    streak_days = 0
    completed_exercises = 0
    total_exercises = 0

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query_progress, (student_id,))
        prog_row = cursor.fetchone()
        if prog_row:
            progress["totalLessons"] = prog_row[0] or 0
            progress["completedLessons"] = prog_row[1] or 0
        
        # Get current module
        cursor.execute("""
            SELECT m.title FROM modules m
            JOIN enrollments e ON e.module_id = m.id
            WHERE e.student_id = %s AND e.status = 'active'
            ORDER BY m."order" ASC LIMIT 1
        """, (student_id,))
        cur_row = cursor.fetchone()
        if cur_row:
            progress["currentModule"] = cur_row[0]
        
        cursor.execute(query_exercises, (student_id,))
        ex_row = cursor.fetchone()
        completed_exercises = ex_row[0] or 0
        
        cursor.execute(query_total_ex, (student_id,))
        tot_row = cursor.fetchone()
        total_exercises = tot_row[0] or 0
        
        cursor.execute(query_achievements, (student_id,))
        for row in cursor.fetchall():
            recent_achievements.append({
                "name": row[0], "description": row[1],
                "icon": row[2] or "star",
                "earnedAt": row[3].isoformat() if row[3] else ""
            })
        
        cursor.execute(query_user, (student_id,))
        user_row = cursor.fetchone()
        if user_row:
            points = user_row[0] or 0
            streak_days = user_row[1] or 0
    
    # 7. Total achievements count
    achievement_count = len(recent_achievements)
    # Actually get full count
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM user_achievements WHERE user_id = %s", (student_id,))
        row = cursor.fetchone()
        achievement_count = row[0] if row else 0
    
    # Save progress snapshot to MongoDB
    try:
        db = await event_repository.get_db()
        if db is not None:
            db["progress_snapshots"].insert_one({
                "user_id": student_id,
                "timestamp": datetime.now(timezone.utc),
                "completed_modules": progress["completedLessons"],
                "total_modules": progress["totalLessons"],
                "completed_exercises": completed_exercises,
                "total_exercises": total_exercises,
                "points": points,
                "streak_days": streak_days
            })
    except Exception as e:
        print(f"[WARN] MongoDB snapshot failed: {e}")
            
    return {
        "success": True,
        "dashboard": {
            "progress": progress,
            "recentAchievements": recent_achievements,
            "weeklyActivity": weekly_activity,
            "points": points,
            "streakDays": streak_days,
            "completedExercises": completed_exercises,
            "totalExercises": total_exercises,
            "achievementCount": achievement_count
        }
    }

@app.get("/api/dashboard/admin", tags=["Admin"])
async def get_admin_dashboard(token_data: TokenData = Depends(verify_admin)):
    """Get admin dashboard stats - synced with DB via stored procedures"""
    from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
    
    stats_data = ProcedureRunner.get_admin_stats()
    stats = {
        "totalUsers": 0, "activeStudents": 0, "activeTeachers": 0,
        "totalModules": 0, "publishedModules": 0,
        "pendingTeachers": 0, "pendingReviews": 0,
        "totalEnrollments": 0, "totalAchievements": 0, "totalExercises": 0,
    }
    if stats_data:
        stats = {
            "totalUsers": stats_data.get("total_users", 0),
            "activeStudents": stats_data.get("active_students", 0),
            "activeTeachers": stats_data.get("active_teachers", 0),
            "totalModules": stats_data.get("total_modules", 0),
            "publishedModules": stats_data.get("published_modules", 0),
            "pendingTeachers": stats_data.get("pending_teachers", 0),
            "pendingReviews": stats_data.get("pending_reviews", 0),
            "totalEnrollments": stats_data.get("total_enrollments", 0),
            "totalAchievements": stats_data.get("total_achievements", 0),
            "totalExercises": stats_data.get("total_exercises", 0),
        }
    
    # Sync with MongoDB
    try:
        db_stats = await event_repository.get_db()
        db_stats["admin_stats"].insert_one({
            "timestamp": datetime.now(timezone.utc), **stats
        })
    except:
        pass
            
    return {"success": True, "stats": stats}

@app.get("/api/admin/audit-logs", tags=["Admin"])
async def get_audit_logs(limit: int = 50, token_data: TokenData = Depends(verify_admin)):
    """Get audit logs from MongoDB events"""
    try:
        db = await event_repository.get_db()
        events = list(db.events.find().sort("timestamp", -1).limit(limit))
        for event in events:
            event["_id"] = str(event["_id"])
            if "timestamp" in event:
                event["timestamp"] = event["timestamp"].isoformat()
        return {"success": True, "events": events}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# Routes - Admin Content Management
# ============================================

@app.get("/api/admin/modules", tags=["Admin"])
async def admin_list_modules(
    status: Optional[str] = None,
    search: Optional[str] = None,
    token_data: TokenData = Depends(verify_admin),
):
    """List all modules for admin management (editor view, not student view).
    Shows ALL modules with status, lesson count, exercise count, enrollment count.
    Supports filtering by status and search by title."""
    from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner

    modules = ProcedureRunner.get_admin_modules(status_filter=status, search=search)
    for m in modules:
        if m.get("created_at") and hasattr(m["created_at"], "isoformat"):
            m["created_at"] = m["created_at"].isoformat()
        else:
            m["created_at"] = str(m["created_at"]) if m.get("created_at") else None

    return {
        "success": True,
        "modules": modules,
        "total": len(modules),
    }

@app.get("/api/admin/modules/{module_id}", tags=["Admin"])
async def admin_get_module(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Get full module details with lessons and exercises for admin editing.
    Admin sees ALL modules as an editor, not as a student consumer."""
    from infrastructure.adapters.output.postgres.procedure_runner import ProcedureRunner
    import json

    mod_data = ProcedureRunner.get_module_detail_for_admin(module_id)
    if not mod_data:
        raise HTTPException(status_code=404, detail="Module not found")

    if mod_data.get("created_at") and hasattr(mod_data["created_at"], "isoformat"):
        mod_data["created_at"] = mod_data["created_at"].isoformat()

    for field in ["lessons", "exercises"]:
        val = mod_data.get(field)
        if isinstance(val, str):
            try:
                mod_data[field] = json.loads(val)
            except:
                mod_data[field] = []
        elif val is None:
            mod_data[field] = []

    return {"success": True, "module": mod_data}

@app.post("/api/admin/modules/{module_id}/approve", tags=["Admin"])
async def admin_approve_module(module_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve a module (set status to approved and publish)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            UPDATE modules SET status = 'approved', is_published = TRUE
            WHERE id = %s
        """, (module_id,))
    
    await event_repository.log_event("module_approved", token_data.user_id, {"module_id": module_id})
    return {"success": True, "message": "Module approved and published"}

@app.post("/api/admin/modules/{module_id}/reject", tags=["Admin"])
async def admin_reject_module(module_id: int, request: Request, token_data: TokenData = Depends(verify_admin)):
    """Reject a module with feedback"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    body = await request.json()
    feedback = body.get("feedback", "")
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            UPDATE modules SET status = 'rejected' WHERE id = %s
        """, (module_id,))
    
    await event_repository.log_event("module_rejected", token_data.user_id, {
        "module_id": module_id, "feedback": feedback
    })
    return {"success": True, "message": "Module rejected"}

@app.put("/api/admin/modules/{module_id}/content", tags=["Admin"])
async def admin_update_module_content(module_id: int, request: Request, token_data: TokenData = Depends(verify_admin)):
    """Admin directly edits module content (theory, lessons, etc.)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    body = await request.json()
    
    # Update module fields
    module_fields = ["title", "description", "theory_content", "difficulty", "lesson_count"]
    updates = []
    values = []
    for field in module_fields:
        if field in body:
            updates.append(f"{field} = %s")
            values.append(body[field])
    
    if updates:
        values.append(module_id)
        query = f"UPDATE modules SET {', '.join(updates)} WHERE id = %s"
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, tuple(values))
    
    # Update lessons if provided
    if "lessons" in body:
        with PostgresConnection.get_cursor() as cursor:
            for lesson in body["lessons"]:
                if "id" in lesson:
                    cursor.execute("""
                        UPDATE lessons SET title = %s, theory_content = %s, "order" = %s
                        WHERE id = %s AND module_id = %s
                    """, (lesson.get("title"), lesson.get("theory_content"), 
                          lesson.get("order", 0), lesson["id"], module_id))
    
    # Update exercises if provided
    if "exercises" in body:
        with PostgresConnection.get_cursor() as cursor:
            for ex in body["exercises"]:
                if "id" in ex:
                    cursor.execute("""
                        UPDATE exercises SET title = %s, description = %s, instructions = %s,
                            difficulty = %s, points = %s, "order" = %s,
                            solution_output = %s, solution_type = %s
                        WHERE id = %s AND module_id = %s
                    """, (ex.get("title"), ex.get("description"), ex.get("instructions"),
                          ex.get("difficulty", 1), ex.get("points", 10), ex.get("order", 0),
                          ex.get("solution_output"), ex.get("solution_type", "output"),
                          ex["id"], module_id))
    
    await event_repository.log_event("module_content_edited", token_data.user_id, {"module_id": module_id})
    
    return {"success": True, "message": "Module content updated"}

@app.get("/api/admin/content-review", tags=["Admin"])
async def admin_content_review_list(token_data: TokenData = Depends(verify_admin)):
    """List modules pending review"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT m.id, m.title, m.description, m.status, m.created_at,
               u.full_name as teacher_name
        FROM modules m
        LEFT JOIN users u ON m.teacher_id = u.id
        WHERE m.status IN ('pending_review', 'pending_deletion', 'draft')
        ORDER BY m.status, m.created_at DESC
    """
    items = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            items.append({
                "id": row[0], "title": row[1], "description": row[2],
                "status": row[3], "created_at": row[4].isoformat() if row[4] else None,
                "teacher_name": row[5]
            })
    return {"success": True, "items": items}

@app.get("/api/challenges", tags=["Challenges"])
async def list_challenges(token_data: TokenData = Depends(verify_token)):
    """Get all challenges"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    role = token_data.role
    
    if role == "student":
        # Students only see published challenges
        query = """
            SELECT c.id, c.title, c.description, c.difficulty, c.points, 
                   u.full_name as author_name, c.base_code, c.deadline, c.is_published,
                   COALESCE(ca.passed, FALSE) as user_passed,
                   COALESCE(ca.attempt_count, 0) as user_attempts
            FROM challenges c
            JOIN users u ON c.teacher_id = u.id
            LEFT JOIN challenge_attempts ca ON ca.challenge_id = c.id AND ca.student_id = %s
            WHERE c.is_published = TRUE
            ORDER BY c.created_at DESC
        """
        params = (token_data.user_id,)
    else:
        # Teachers/admins see all their challenges
        query = """
            SELECT c.id, c.title, c.description, c.difficulty, c.points, 
                   u.full_name as author_name, c.base_code, c.deadline, c.is_published,
                   FALSE as user_passed, 0 as user_attempts
            FROM challenges c
            JOIN users u ON c.teacher_id = u.id
            ORDER BY c.created_at DESC
        """
        params = ()
    
    challenges = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        for row in rows:
            deadline_str = None
            if row[7]:
                try:
                    deadline_str = row[7].isoformat() if hasattr(row[7], 'isoformat') else str(row[7])
                except:
                    deadline_str = str(row[7])
            
            challenges.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "difficulty": row[3],
                "points": row[4],
                "author_name": row[5],
                "base_code": row[6] or "",
                "deadline": deadline_str,
                "is_published": row[8],
                "user_passed": row[9],
                "user_attempts": row[10]
            })
            
    return {"success": True, "challenges": challenges}

@app.get("/api/challenges/{challenge_id}", tags=["Challenges"])
async def get_challenge(challenge_id: int, token_data: TokenData = Depends(verify_token)):
    """Get a single challenge with full details"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    query = """
        SELECT c.id, c.title, c.description, c.instructions, c.difficulty, c.points,
               c.teacher_id, u.full_name as author_name, c.base_code, c.solution_code,
               c.solution_type, c.solution_output, c.test_code, c.deadline, c.is_published,
               c.max_attempts, c.created_at
        FROM challenges c
        JOIN users u ON c.teacher_id = u.id
        WHERE c.id = %s
    """
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (challenge_id,))
        row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check deadline and get user attempts
    deadline = row[13]
    deadline_passed = False
    if deadline:
        try:
            if isinstance(deadline, str):
                deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            else:
                deadline_dt = deadline
            deadline_passed = datetime.now(timezone.utc) > deadline_dt
        except:
            pass
    
    # Get user attempts
    user_attempts = 0
    user_passed = False
    if token_data.role == "student":
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT attempt_count, passed FROM challenge_attempts 
                WHERE challenge_id = %s AND student_id = %s
                ORDER BY submitted_at DESC LIMIT 1
            """, (challenge_id, token_data.user_id))
            arow = cursor.fetchone()
            if arow:
                user_attempts = arow[0] or 0
                user_passed = arow[1]
    
    # Determine if solution should be shown
    show_solution = False
    if token_data.role != "student":
        show_solution = True  # Teachers always see it
    elif deadline_passed:
        show_solution = True  # Show after deadline
    elif user_passed:
        show_solution = True  # Show if already passed
    
    deadline_str = None
    if deadline:
        try:
            deadline_str = deadline.isoformat() if hasattr(deadline, 'isoformat') else str(deadline)
        except:
            deadline_str = str(deadline)
    
    return {
        "success": True,
        "challenge": {
            "id": row[0], "title": row[1], "description": row[2],
            "instructions": row[3], "difficulty": row[4], "points": row[5],
            "teacher_id": row[6], "author_name": row[7],
            "base_code": row[8] or "",
            "solution_code": row[9] if show_solution else None,
            "solution_type": row[10],
            "solution_output": row[11] if show_solution else None,
            "test_code": row[12] if show_solution else None,
            "deadline": deadline_str,
            "is_published": row[14],
            "max_attempts": row[15],
            "created_at": row[16].isoformat() if row[16] else None,
            "deadline_passed": deadline_passed,
            "user_attempts": user_attempts,
            "user_passed": user_passed
        }
    }

@app.post("/api/challenges", tags=["Challenges"])
async def create_challenge(request: ChallengeCreate, token_data: TokenData = Depends(verify_teacher)):
    """Create a new challenge with code, solution, deadline"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    deadline_val = None
    if request.deadline:
        try:
            deadline_val = datetime.fromisoformat(request.deadline.replace('Z', '+00:00'))
        except:
            deadline_val = None
    
    query = """
        INSERT INTO challenges (title, description, instructions, difficulty, points, teacher_id,
                               base_code, solution_code, solution_type, solution_output, test_code,
                               deadline, is_published, max_attempts)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (
            request.title, request.description, request.instructions,
            request.difficulty, request.points, token_data.user_id,
            request.base_code, request.solution_code, request.solution_type,
            request.solution_output, request.test_code,
            deadline_val, request.is_published, request.max_attempts
        ))
        challenge_id = cursor.fetchone()[0]
    
    await event_repository.log_event("challenge_created", token_data.user_id, {
        "challenge_id": challenge_id, "title": request.title
    })
    
    return {"success": True, "challenge_id": challenge_id}

@app.put("/api/challenges/{challenge_id}", tags=["Challenges"])
async def update_challenge(challenge_id: int, request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Update a challenge"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    import json
    
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
    
    # Verify ownership
    query = f"UPDATE challenges SET {', '.join(fields)} WHERE id = %s AND teacher_id = %s"
    values.append(token_data.user_id)
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(values))
    
    return {"success": True, "message": "Challenge updated"}

@app.delete("/api/challenges/{challenge_id}", tags=["Challenges"])
async def delete_challenge(challenge_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a challenge"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = "DELETE FROM challenges WHERE id = %s AND teacher_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (challenge_id, token_data.user_id))
    return {"success": True, "message": "Challenge deleted"}

@app.post("/api/challenges/submit", tags=["Challenges"])
async def submit_challenge(
    request: ChallengeSubmit,
    token_data: TokenData = Depends(verify_token)
):
    """Submit a challenge attempt with code execution and grading"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    student_id = token_data.user_id
    
    # Get the challenge
    query = """
        SELECT id, title, description, instructions, difficulty, points,
               base_code, solution_code, solution_type, solution_output, test_code,
               deadline, max_attempts
        FROM challenges WHERE id = %s
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (request.challenge_id,))
        row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    challenge = {
        "id": row[0], "title": row[1], "description": row[2],
        "instructions": row[3], "difficulty": row[4], "points": row[5],
        "base_code": row[6] or "", "solution_code": row[7],
        "solution_type": row[8] or "output", "solution_output": row[9],
        "test_code": row[10], "deadline": row[11], "max_attempts": row[12] or 0
    }
    
    # Check deadline
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
    
    # Check max attempts
    if challenge["max_attempts"] > 0:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM challenge_attempts
                WHERE challenge_id = %s AND student_id = %s
            """, (request.challenge_id, student_id))
            total_attempts = cursor.fetchone()[0] or 0
            if total_attempts >= challenge["max_attempts"]:
                raise HTTPException(status_code=400, detail="Maximum attempts reached")
    
    # Check if already passed
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT passed FROM challenge_attempts
            WHERE challenge_id = %s AND student_id = %s AND passed = TRUE
        """, (request.challenge_id, student_id))
        if cursor.fetchone():
            return {"success": True, "passed": True, "message": "Already passed this challenge"}
    
    # Execute and grade via sandbox
    grading_result = await sandbox_service.execute_and_compare(
        code=request.code,
        expected_output=challenge["solution_output"],
        solution_type=challenge["solution_type"],
        test_code=challenge["test_code"],
    )
    passed = grading_result["passed"]
    score = grading_result["score"]
    error = grading_result.get("error")
    output = grading_result.get("output", "")

    # Record attempt
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO challenge_attempts (challenge_id, student_id, passed, score, attempt_count, submitted_code)
            VALUES (%s, %s, %s, %s,
                (SELECT COALESCE(MAX(attempt_count), 0) + 1 FROM challenge_attempts WHERE challenge_id = %s AND student_id = %s),
                %s)
        """, (request.challenge_id, student_id, passed, score,
              request.challenge_id, student_id, request.code))

    # Award points if passed
    if passed:
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute("UPDATE users SET points = COALESCE(points, 0) + %s WHERE id = %s",
                          (challenge["points"], student_id))

        await check_and_award_achievements(student_id)
        await event_repository.log_event("challenge_passed", student_id, {
            "challenge_id": request.challenge_id,
            "points_earned": challenge["points"]
        })

    return {
        "success": True,
        "passed": passed,
        "score": score,
        "output": output if not error else None,
        "error": error,
        "points_earned": challenge["points"] if passed else 0
    }

@app.get("/api/teacher/pending-enrollments", tags=["Teacher"])
async def get_pending_enrollments(token_data: TokenData = Depends(verify_teacher)):
    """Get ALL pending enrollment requests across all teacher's classes"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT ce.id, ce.student_id, ce.class_id, ce.status, ce.enrolled_at,
               u.full_name, u.email, c.title as class_title
        FROM class_enrollments ce
        JOIN users u ON ce.student_id = u.id
        JOIN classes c ON ce.class_id = c.id
        WHERE c.teacher_id = %s AND ce.status = 'pending'
        ORDER BY ce.enrolled_at DESC
    """
    requests = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id,))
        for row in cursor.fetchall():
            requests.append({
                "id": row[0], "student_id": row[1], "class_id": row[2],
                "status": row[3],
                "enrolled_at": row[4].isoformat() if row[4] else None,
                "student_name": row[5], "student_email": row[6],
                "class_title": row[7]
            })
    return {"success": True, "requests": requests}

@app.post("/api/teacher/enrollments/approve", tags=["Teacher"])
async def approve_enrollment_batch(request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Approve an enrollment request"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    body = await request.json()
    enrollment_id = body.get("enrollment_id")
    class_id = body.get("class_id")
    student_id = body.get("student_id")
    
    if enrollment_id:
        query = """
            UPDATE class_enrollments SET status = 'approved', approved_at = CURRENT_TIMESTAMP
            WHERE id = %s AND class_id IN (SELECT id FROM classes WHERE teacher_id = %s)
        """
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (enrollment_id, token_data.user_id))
    elif class_id and student_id:
        query = """
            UPDATE class_enrollments SET status = 'approved', approved_at = CURRENT_TIMESTAMP
            WHERE class_id = %s AND student_id = %s
            AND class_id IN (SELECT id FROM classes WHERE teacher_id = %s)
        """
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (class_id, student_id, token_data.user_id))
    else:
        raise HTTPException(status_code=400, detail="Provide enrollment_id or (class_id + student_id)")
    
    await event_repository.log_event("enrollment_approved", token_data.user_id, {
        "enrollment_id": enrollment_id, "student_id": student_id, "class_id": class_id
    })
    
    return {"success": True, "message": "Enrollment approved"}

@app.post("/api/teacher/enrollments/reject", tags=["Teacher"])
async def reject_enrollment_batch(request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Reject an enrollment request"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    body = await request.json()
    enrollment_id = body.get("enrollment_id")
    class_id = body.get("class_id")
    student_id = body.get("student_id")
    
    if enrollment_id:
        query = """
            UPDATE class_enrollments SET status = 'rejected'
            WHERE id = %s AND class_id IN (SELECT id FROM classes WHERE teacher_id = %s)
        """
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (enrollment_id, token_data.user_id))
    elif class_id and student_id:
        query = """
            UPDATE class_enrollments SET status = 'rejected'
            WHERE class_id = %s AND student_id = %s
            AND class_id IN (SELECT id FROM classes WHERE teacher_id = %s)
        """
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (class_id, student_id, token_data.user_id))
    else:
        raise HTTPException(status_code=400, detail="Provide enrollment_id or (class_id + student_id)")
    
    return {"success": True, "message": "Enrollment rejected"}

@app.post("/api/classes/{class_id}/unenroll/{student_id}", tags=["Teacher"])
async def unenroll_student(class_id: int, student_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Unenroll a student from a class (teacher must own the class)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="No eres el docente de esta clase")
    
    query = "DELETE FROM class_enrollments WHERE class_id = %s AND student_id = %s"
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, student_id))
        
    return {"success": True, "message": "Student unenrolled"}

# ============================================
# Routes - Classes System
# ============================================

# --- Classes CRUD ---

@app.get("/api/classes", tags=["Classes"])
async def list_classes(token_data: Optional[TokenData] = Depends(verify_token_optional)):
    """List all published classes (teachers see only their own; students see all)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT c.id, c.title, c.description, c.category, c.difficulty, 
               c.teacher_id, c.is_published, c.created_at,
               u.full_name as teacher_name,
               COUNT(DISTINCT cm.id) as module_count,
               COUNT(DISTINCT ce.id) as student_count
        FROM classes c
        JOIN users u ON c.teacher_id = u.id
        LEFT JOIN class_modules cm ON cm.class_id = c.id
        LEFT JOIN class_enrollments ce ON ce.class_id = c.id AND ce.status = 'approved'
        WHERE c.is_published = TRUE
    """
    params = []
    if token_data and token_data.role in ("teacher", "admin"):
        query += " AND c.teacher_id = %s"
        params.append(token_data.user_id)
    query += " GROUP BY c.id, u.full_name ORDER BY c.created_at DESC"
    classes = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(params) if params else None)
        for row in cursor.fetchall():
            classes.append({
                "id": row[0], "title": row[1], "description": row[2],
                "category": row[3], "difficulty": row[4], "teacher_id": row[5],
                "is_published": row[6], "created_at": row[7].isoformat() if row[7] else None,
                "teacher_name": row[8], "module_count": row[9], "student_count": row[10]
            })
    return {"success": True, "classes": classes}

@app.get("/api/classes/my-classes", tags=["Classes"])
async def get_my_classes(token_data: TokenData = Depends(verify_teacher)):
    """Get teacher's own classes"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT c.id, c.title, c.description, c.category, c.difficulty, 
               c.teacher_id, c.is_published, c.created_at,
               COUNT(DISTINCT cm.id) as module_count,
               COUNT(DISTINCT ce.id) as student_count
        FROM classes c
        LEFT JOIN class_modules cm ON cm.class_id = c.id
        LEFT JOIN class_enrollments ce ON ce.class_id = c.id AND ce.status = 'approved'
        WHERE c.teacher_id = %s
        GROUP BY c.id
        ORDER BY c.created_at DESC
    """
    classes = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id,))
        for row in cursor.fetchall():
            classes.append({
                "id": row[0], "title": row[1], "description": row[2],
                "category": row[3], "difficulty": row[4], "teacher_id": row[5],
                "is_published": row[6], "created_at": row[7].isoformat() if row[7] else None,
                "module_count": row[8], "student_count": row[9]
            })
    return {"success": True, "classes": classes}

@app.get("/api/classes/enrolled", tags=["Classes"])
async def get_enrolled_classes(token_data: TokenData = Depends(verify_token)):
    """Get classes the student is enrolled in (approved only)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT c.id, c.title, c.description, c.category, c.difficulty,
               c.teacher_id, u.full_name as teacher_name,
               ce.status as enrollment_status, ce.enrolled_at, ce.approved_at
        FROM class_enrollments ce
        JOIN classes c ON ce.class_id = c.id
        JOIN users u ON c.teacher_id = u.id
        WHERE ce.student_id = %s
        ORDER BY ce.enrolled_at DESC
    """
    classes = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (token_data.user_id,))
        for row in cursor.fetchall():
            classes.append({
                "id": row[0], "title": row[1], "description": row[2],
                "category": row[3], "difficulty": row[4], "teacher_id": row[5],
                "teacher_name": row[6], "enrollment_status": row[7],
                "enrolled_at": row[8].isoformat() if row[8] else None,
                "approved_at": row[9].isoformat() if row[9] else None
            })
    return {"success": True, "classes": classes}

@app.get("/api/classes/{class_id}", tags=["Classes"])
async def get_class(class_id: int, token_data: Optional[TokenData] = Depends(verify_token_optional)):
    """Get class by ID with modules"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query_class = """
        SELECT c.id, c.title, c.description, c.category, c.difficulty, 
               c.teacher_id, c.is_published, c.created_at, u.full_name as teacher_name
        FROM classes c
        JOIN users u ON c.teacher_id = u.id
        WHERE c.id = %s
    """
    query_modules = """
        SELECT cm.id, cm.title, cm.description, cm.theory_content, cm."order", cm.created_at,
               COUNT(DISTINCT ce.id) as exercise_count
        FROM class_modules cm
        LEFT JOIN class_exercises ce ON ce.class_module_id = cm.id
        WHERE cm.class_id = %s
        GROUP BY cm.id
        ORDER BY cm."order" ASC
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query_class, (class_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Class not found")
        cls = {
            "id": row[0], "title": row[1], "description": row[2],
            "category": row[3], "difficulty": row[4], "teacher_id": row[5],
            "is_published": row[6], "created_at": row[7].isoformat() if row[7] else None,
            "teacher_name": row[8]
        }
        if token_data:
            cursor.execute("""
                SELECT status FROM class_enrollments WHERE student_id = %s AND class_id = %s
            """, (token_data.user_id, class_id))
            enr = cursor.fetchone()
            if enr:
                cls["enrollment_status"] = enr[0]
        cursor.execute(query_modules, (class_id,))
        modules = []
        for mrow in cursor.fetchall():
            modules.append({
                "id": mrow[0], "title": mrow[1], "description": mrow[2],
                "theory_content": mrow[3], "order": mrow[4],
                "created_at": mrow[5].isoformat() if mrow[5] else None,
                "exercise_count": mrow[6]
            })
        cls["modules"] = modules
    return {"success": True, "class": cls}

@app.post("/api/classes", tags=["Classes"])
async def create_class(request: ClassCreate, token_data: TokenData = Depends(verify_teacher)):
    """Create a new class"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        INSERT INTO classes (title, description, category, difficulty, teacher_id, is_published)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (request.title, request.description, request.category,
                               request.difficulty, token_data.user_id, request.is_published))
        class_id = cursor.fetchone()[0]
    return {"success": True, "class_id": class_id}

@app.put("/api/classes/{class_id}", tags=["Classes"])
async def update_class(class_id: int, request: ClassUpdate, token_data: TokenData = Depends(verify_teacher)):
    """Update a class"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    fields = []
    values = []
    if request.title is not None:
        fields.append("title = %s"); values.append(request.title)
    if request.description is not None:
        fields.append("description = %s"); values.append(request.description)
    if request.category is not None:
        fields.append("category = %s"); values.append(request.category)
    if request.difficulty is not None:
        fields.append("difficulty = %s"); values.append(request.difficulty)
    if request.is_published is not None:
        fields.append("is_published = %s"); values.append(request.is_published)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(class_id)
    query = f"UPDATE classes SET {', '.join(fields)} WHERE id = %s AND teacher_id = %s"
    values.append(token_data.user_id)
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(values))
    return {"success": True, "message": "Class updated"}

@app.delete("/api/classes/{class_id}", tags=["Classes"])
async def delete_class(class_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a class"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = "DELETE FROM classes WHERE id = %s AND teacher_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, token_data.user_id))
    return {"success": True, "message": "Class deleted"}

# --- Class Enrollment ---

@app.post("/api/classes/{class_id}/enroll", tags=["Classes"])
async def enroll_class(class_id: int, token_data: TokenData = Depends(verify_token)):
    """Request enrollment in a class"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT status FROM class_enrollments
            WHERE student_id = %s AND class_id = %s
        """, (token_data.user_id, class_id))
        row = cursor.fetchone()
        if row and row[0] == "approved":
            raise HTTPException(status_code=400, detail="Ya estás matriculado en esta clase")
        # Allow re-request if rejected or no previous enrollment
        query = """
            INSERT INTO class_enrollments (student_id, class_id, status)
            VALUES (%s, %s, 'pending')
            ON CONFLICT (student_id, class_id) DO UPDATE SET status = 'pending'
            RETURNING id
        """
        cursor.execute(query, (token_data.user_id, class_id))
        enrollment_id = cursor.fetchone()[0]
    return {"success": True, "enrollment_id": enrollment_id, "status": "pending"}

@app.get("/api/classes/{class_id}/requests", tags=["Classes"])
async def get_enrollment_requests(class_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Get pending enrollment requests for a class (teacher only)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT ce.id, ce.student_id, ce.status, ce.enrolled_at,
               u.full_name, u.email
        FROM class_enrollments ce
        JOIN users u ON ce.student_id = u.id
        JOIN classes c ON ce.class_id = c.id
        WHERE ce.class_id = %s AND c.teacher_id = %s
        ORDER BY ce.enrolled_at DESC
    """
    requests = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, token_data.user_id))
        for row in cursor.fetchall():
            requests.append({
                "id": row[0], "student_id": row[1], "status": row[2],
                "enrolled_at": row[3].isoformat() if row[3] else None,
                "student_name": row[4], "student_email": row[5]
            })
    return {"success": True, "requests": requests}

@app.post("/api/classes/{class_id}/approve/{student_id}", tags=["Classes"])
async def approve_enrollment(class_id: int, student_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Approve a student's enrollment request"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        UPDATE class_enrollments
        SET status = 'approved', approved_at = CURRENT_TIMESTAMP
        WHERE class_id = %s AND student_id = %s
        AND class_id IN (SELECT id FROM classes WHERE teacher_id = %s)
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, student_id, token_data.user_id))
    return {"success": True, "message": "Enrollment approved"}

@app.post("/api/classes/{class_id}/reject/{student_id}", tags=["Classes"])
async def reject_enrollment(class_id: int, student_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Reject a student's enrollment request"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        UPDATE class_enrollments
        SET status = 'rejected'
        WHERE class_id = %s AND student_id = %s
        AND class_id IN (SELECT id FROM classes WHERE teacher_id = %s)
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, student_id, token_data.user_id))
    return {"success": True, "message": "Enrollment rejected"}

# --- Class Modules CRUD ---

@app.get("/api/classes/{class_id}/modules", tags=["Classes"])
async def list_class_modules(class_id: int, token_data: TokenData = Depends(verify_token)):
    """List modules in a class"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT cm.id, cm.title, cm.description, cm.theory_content, cm."order",
               COUNT(DISTINCT ce.id) as exercise_count
        FROM class_modules cm
        LEFT JOIN class_exercises ce ON ce.class_module_id = cm.id
        WHERE cm.class_id = %s
        GROUP BY cm.id
        ORDER BY cm."order" ASC
    """
    modules = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id,))
        for row in cursor.fetchall():
            modules.append({
                "id": row[0], "title": row[1], "description": row[2],
                "theory_content": row[3], "order": row[4], "exercise_count": row[5]
            })
    return {"success": True, "modules": modules}

@app.get("/api/classes/{class_id}/modules/{module_id}", tags=["Classes"])
async def get_class_module(
    class_id: int, module_id: int,
    token_data: TokenData = Depends(verify_token),
):
    """Get a single class module with its exercises (enrollment required)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT status FROM class_enrollments
            WHERE student_id = %s AND class_id = %s AND status = 'approved'
        """, (token_data.user_id, class_id))
        enrollment = cursor.fetchone()
        if not enrollment:
            raise HTTPException(status_code=403, detail="No estás matriculado en esta clase")

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("""
            SELECT cm.id, cm.title, cm.description, cm.theory_content, cm."order"
            FROM class_modules cm WHERE cm.id = %s AND cm.class_id = %s
        """, (module_id, class_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Module not found")
        mod = {
            "id": row[0], "title": row[1], "description": row[2],
            "theory_content": row[3], "order": row[4]
        }
        cursor.execute("""
            SELECT ce.id, ce.title, ce.description, ce.instructions, ce.exercise_type,
                   ce.difficulty, ce.points, ce."order", ce.metadata,
                   ce.solution_output, ce.solution_type, ce.test_code
            FROM class_exercises ce WHERE ce.class_module_id = %s ORDER BY ce."order" ASC
        """, (module_id,))
        exercises = []
        for er in cursor.fetchall():
            exercises.append({
                "id": er[0], "title": er[1], "description": er[2],
                "instructions": er[3], "exercise_type": er[4],
                "difficulty": er[5], "points": er[6], "order": er[7],
                "metadata": er[8], "solution_output": er[9],
                "solution_type": er[10], "test_code": er[11]
            })
        mod["exercises"] = exercises
    return {"success": True, "module": mod}

@app.post("/api/classes/{class_id}/modules", tags=["Classes"])
async def create_class_module(class_id: int, request: ClassModuleCreate, token_data: TokenData = Depends(verify_teacher)):
    """Create a module in a class (teacher must own the class)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not your class")
    query = """
        INSERT INTO class_modules (class_id, title, description, theory_content, "order")
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, request.title, request.description, request.theory_content, request.order))
        module_id = cursor.fetchone()[0]
    return {"success": True, "module_id": module_id}

@app.put("/api/classes/{class_id}/modules/{module_id}", tags=["Classes"])
async def update_class_module(class_id: int, module_id: int, request: ClassModuleUpdate, token_data: TokenData = Depends(verify_teacher)):
    """Update a class module (teacher must own the class)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not your class")
    fields = []
    values = []
    if request.title is not None:
        fields.append("title = %s"); values.append(request.title)
    if request.description is not None:
        fields.append("description = %s"); values.append(request.description)
    if request.theory_content is not None:
        fields.append("theory_content = %s"); values.append(request.theory_content)
    if request.order is not None:
        fields.append('"order" = %s'); values.append(request.order)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.extend([module_id, class_id])
    query = f"UPDATE class_modules SET {', '.join(fields)} WHERE id = %s AND class_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(values))
    return {"success": True, "message": "Module updated"}

@app.delete("/api/classes/{class_id}/modules/{module_id}", tags=["Classes"])
async def delete_class_module(class_id: int, module_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Delete a class module (teacher must own the class)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not your class")
    query = "DELETE FROM class_modules WHERE id = %s AND class_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id, class_id))
    return {"success": True, "message": "Module deleted"}

# --- Class Exercises CRUD ---

@app.get("/api/classes/{class_id}/modules/{module_id}/exercises", tags=["Classes"])
async def list_class_exercises(class_id: int, module_id: int, token_data: TokenData = Depends(verify_token)):
    """List exercises for a class module"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT ce.id, ce.title, ce.description, ce.instructions, ce.exercise_type,
               ce.difficulty, ce.points, ce."order", ce.metadata,
               ce.solution_output, ce.solution_type, ce.test_code
        FROM class_exercises ce
        JOIN class_modules cm ON ce.class_module_id = cm.id
        WHERE cm.id = %s AND cm.class_id = %s
        ORDER BY ce."order" ASC
    """
    exercises = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id, class_id))
        for row in cursor.fetchall():
            exercises.append({
                "id": row[0], "title": row[1], "description": row[2],
                "instructions": row[3], "exercise_type": row[4],
                "difficulty": row[5], "points": row[6], "order": row[7],
                "metadata": row[8], "solution_output": row[9],
                "solution_type": row[10], "test_code": row[11]
            })
    return {"success": True, "exercises": exercises}

@app.post("/api/classes/{class_id}/modules/{module_id}/exercises", tags=["Classes"])
async def create_class_exercise(
    class_id: int, module_id: int, request: ClassExerciseCreate,
    token_data: TokenData = Depends(verify_teacher)
):
    """Create an exercise in a class module (teacher must own the class)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    import json
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not your class")
    query = """
        INSERT INTO class_exercises (class_module_id, title, description, instructions, exercise_type, difficulty, points, "order", metadata, solution_output, solution_type, test_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    metadata_json = json.dumps(request.metadata) if request.metadata else '{}'
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id, request.title, request.description, request.instructions,
                               request.exercise_type, request.difficulty, request.points,
                               request.order, metadata_json,
                               request.solution_output, request.solution_type, request.test_code))
        exercise_id = cursor.fetchone()[0]
    return {"success": True, "exercise_id": exercise_id}

@app.put("/api/classes/{class_id}/modules/{module_id}/exercises/{exercise_id}", tags=["Classes"])
async def update_class_exercise(
    class_id: int, module_id: int, exercise_id: int,
    request: ClassExerciseUpdate, token_data: TokenData = Depends(verify_teacher)
):
    """Update a class exercise (teacher must own the class)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    import json
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not your class")
    fields = []; values = []
    if request.title is not None:
        fields.append("title = %s"); values.append(request.title)
    if request.description is not None:
        fields.append("description = %s"); values.append(request.description)
    if request.instructions is not None:
        fields.append("instructions = %s"); values.append(request.instructions)
    if request.difficulty is not None:
        fields.append("difficulty = %s"); values.append(request.difficulty)
    if request.points is not None:
        fields.append("points = %s"); values.append(request.points)
    if request.order is not None:
        fields.append('"order" = %s'); values.append(request.order)
    if request.solution_output is not None:
        fields.append("solution_output = %s"); values.append(request.solution_output)
    if request.solution_type is not None:
        fields.append("solution_type = %s"); values.append(request.solution_type)
    if request.test_code is not None:
        fields.append("test_code = %s"); values.append(request.test_code)
    if request.metadata is not None:
        fields.append("metadata = %s"); values.append(json.dumps(request.metadata))
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    values.extend([exercise_id, module_id])
    query = f"UPDATE class_exercises SET {', '.join(fields)} WHERE id = %s AND class_module_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, tuple(values))
    return {"success": True, "message": "Exercise updated"}

@app.delete("/api/classes/{class_id}/modules/{module_id}/exercises/{exercise_id}", tags=["Classes"])
async def delete_class_exercise(
    class_id: int, module_id: int, exercise_id: int,
    token_data: TokenData = Depends(verify_teacher)
):
    """Delete a class exercise (teacher must own the class)"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM classes WHERE id = %s AND teacher_id = %s", (class_id, token_data.user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Not your class")
    query = "DELETE FROM class_exercises WHERE id = %s AND class_module_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (exercise_id, module_id))
    return {"success": True, "message": "Exercise deleted"}

# ============================================
# AI Routes - RAG, Tutor, Exercise Generation
# ============================================

@app.post("/api/ai/rag/index", tags=["AI"])
async def ai_rag_index(request: RAGIndexRequest, token_data: TokenData = Depends(verify_teacher)):
    """Index a document chunk into the RAG knowledge base"""
    try:
        await rag_service.index_content(
            text=request.text,
            source_type=request.source_type,
            source_id=request.source_id,
            metadata=request.metadata,
        )
        return {"success": True, "message": "Content indexed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing error: {e}")

@app.post("/api/ai/rag/search", tags=["AI"])
async def ai_rag_search(request: RAGSearchRequest, token_data: TokenData = Depends(verify_token)):
    """Search the RAG knowledge base"""
    try:
        results = await rag_service.search(
            query=request.query,
            top_k=request.top_k,
            source_type=request.source_type,
        )
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")

@app.post("/api/ai/tutor/ask-v2", tags=["AI"])
async def ai_tutor_ask(request: AITutorAskRequest, token_data: TokenData = Depends(verify_token)):
    """Ask the AI tutor a question (LLM-based)"""
    try:
        response = await ai_tutor_service.answer_question(
            message=request.message,
            student_level=request.student_level,
            student_context={"user_id": token_data.user_id},
        )
        return {"success": True, "response": response, "source": "llm_tutor"}
    except Exception as e:
        print(f"[AI Tutor] Error: {e}")
        raise HTTPException(status_code=500, detail="Error al consultar el tutor")

@app.post("/api/ai/tutor/hint", tags=["AI"])
async def ai_tutor_hint(request: Request, token_data: TokenData = Depends(verify_token)):
    """Get a contextual hint for an exercise (LLM-based)"""
    body = await request.json()
    try:
        response = await ai_tutor_service.generate_hint(
            exercise_title=body.get("title", ""),
            exercise_desc=body.get("description", ""),
            student_code=body.get("code", ""),
            error_message=body.get("error"),
            attempts=body.get("attempts", 1),
            student_level=body.get("level", "beginner"),
        )
        return {"success": True, "hint": response}
    except Exception as e:
        print(f"[AI Hint] Error: {e}")
        raise HTTPException(status_code=500, detail="Error al generar ayuda")

@app.post("/api/ai/exercises/suggest", tags=["AI"])
async def ai_exercises_suggest(request: ExerciseSuggestionRequest, token_data: TokenData = Depends(verify_teacher)):
    """Generate exercise variant suggestions using AI"""
    try:
        suggestions = await exercise_generator_service.generate_suggestions(
            exercise_id=request.exercise_id,
            title=request.title,
            description=request.description,
            instructions=request.instructions,
            solution=request.solution,
            difficulty=request.difficulty,
        )
        saved = []
        for s in suggestions:
            sid = await exercise_generator_service.save_suggestion(
                original_exercise_id=request.exercise_id,
                suggested_title=s.get("suggested_title", ""),
                suggested_description=s.get("suggested_description", ""),
                suggested_instructions=s.get("suggested_instructions", ""),
                suggested_solution=s.get("suggested_solution", ""),
                rationale=s.get("rationale", ""),
                created_by=token_data.user_id,
            )
            saved.append({"id": sid, **s})
        return {"success": True, "suggestions": saved}
    except Exception as e:
        print(f"[Exercise Gen] Error: {e}")
        raise HTTPException(status_code=500, detail="Error al generar sugerencias")

@app.get("/api/ai/exercises/suggestions", tags=["AI"])
async def ai_list_suggestions(token_data: TokenData = Depends(verify_admin)):
    """List pending exercise suggestions"""
    try:
        suggestions = await exercise_generator_service.list_pending_suggestions()
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/exercises/suggestions/{suggestion_id}/approve", tags=["AI"])
async def ai_approve_suggestion(suggestion_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve an exercise suggestion"""
    result = await exercise_generator_service.approve_suggestion(suggestion_id, token_data.user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Suggestion not found or already processed")
    return {"success": True, "message": "Suggestion approved"}

@app.post("/api/ai/exercises/suggestions/{suggestion_id}/reject", tags=["AI"])
async def ai_reject_suggestion(suggestion_id: int, token_data: TokenData = Depends(verify_admin)):
    """Reject an exercise suggestion"""
    try:
        await exercise_generator_service.reject_suggestion(suggestion_id, token_data.user_id)
        return {"success": True, "message": "Suggestion rejected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Error Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
