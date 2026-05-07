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
    metadata: Optional[dict] = None

class ClassExerciseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    exercise_type: Optional[str] = None
    difficulty: Optional[int] = None
    points: Optional[int] = None
    order: Optional[int] = None
    metadata: Optional[dict] = None

class UserRoleUpdate(BaseModel):
    role: str

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

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        content={"message": f"Internal Server Error: {str(exc)}", "type": type(exc).__name__},
    )

async def verify_token(request: Request) -> TokenData:
    """Verify JWT token from cookies"""
    token = request.cookies.get("auth-token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
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
    """Verify user is a teacher or admin"""
    if token_data.role not in [UserRole.TEACHER.value, UserRole.ADMIN.value]:
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

# ============================================
# Initialize Repositories
# ============================================

user_repository = UserRepositoryImpl()
module_repository = ModuleRepositoryImpl()
enrollment_repository = EnrollmentRepositoryImpl()
teacher_repository = TeacherRepositoryImpl()
event_repository = EventRepository()
ai_service = AIServiceImpl()

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
async def register(request: RegisterRequest, response: Response):
    """Register a new user"""
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
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )
    
    return {
        "success": True,
        "user": user,
        "teacher_request_pending": result.get("teacher_request_pending", False)
    }

@app.post("/api/auth/login", tags=["Auth"])
async def login(request: LoginRequest, response: Response):
    """Login user"""
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
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    # Log event to MongoDB (non-critical, don't crash on failure)
    try:
        await event_repository.log_event("user_login", user.id, {"email": user.email})
    except Exception as e:
        print(f"DEBUG: MongoDB log failed (non-critical): {e}")

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
        }
    }

@app.post("/api/auth/logout", tags=["Auth"])
async def logout(response: Response, token_data: TokenData = Depends(verify_token)):
    """Logout user"""
    # Delete the cookie
    response.delete_cookie(key="auth-token")
    
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

@app.get("/api/users/{user_id}", tags=["Users"])
async def get_user(user_id: int):
    """Get user by ID"""
    user = await user_repository.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't expose password hash
    user_data = user.to_dict()
    user_data.pop("password_hash", None)
    return {"success": True, "user": user_data}

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
# Routes - Chatbot (Dialogflow)
# ============================================

@app.post("/api/chatbot/public", tags=["Chatbot"])
async def chat_public(request: PublicChatRequest):
    """Chat with Dialogflow agent (no auth required, for anonymous users)"""
    session_id = request.session_id or f"anon_{datetime.now(timezone.utc).timestamp()}"
    response = await ai_service.chat_with_dialogflow(session_id, request.message)
    return {"success": True, "message": response, "session_id": session_id}

@app.post("/api/chatbot", tags=["Chatbot"])
async def chat(
    request: ChatRequest,
    token_data: TokenData = Depends(verify_token)
):
    """Chat with Dialogflow agent"""
    session_id = f"user_{token_data.user_id}_session"
    
    response = await ai_service.chat_with_dialogflow(session_id, request.message)
    
    await event_repository.log_chat_interaction(
        token_data.user_id,
        request.message,
        response,
        session_id
    )
    
    return {
        "success": True,
        "message": response
    }

# ============================================
# Routes - Interactive Execution
# ============================================

@app.post("/api/execute-code", tags=["Interactive"])
async def execute_code(
    request: ExecuteRequest,
    token_data: TokenData = Depends(verify_token)
):
    """Execute Python code for interactive exercises"""
    import io
    import sys
    from contextlib import redirect_stdout
    
    actions = []
    
    # Define functions that the user can call in their script
    def jump():
        actions.append("jump")
        
    def forward(steps=1):
        actions.append(f"forward_{steps}")
        
    # Set up safe-ish environment (Note: Not truly secure for production, fine for educational demo)
    env = {
        "jump": jump,
        "forward": forward,
        "__builtins__": __builtins__
    }
    
    f = io.StringIO()
    error = None
    
    try:
        with redirect_stdout(f):
            # We use exec to run the code
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
    """Get module by ID"""
    module = await module_repository.get_by_id(module_id)
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {"success": True, "module": module.to_dict()}

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
    # Dummy list for now
    return {"success": True, "requests": []}

@app.post("/api/admin/teachers/approve/{user_id}", tags=["Admin"])
async def approve_teacher(user_id: int, token_data: TokenData = Depends(verify_admin)):
    """Approve a teacher request"""
    # Implementation would update role to TEACHER
    return {"success": True, "message": f"Teacher {user_id} approved"}

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
    """Get student dashboard data"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    # 1. Progress Stats
    query_progress = """
        SELECT 
            COUNT(DISTINCT e.id) as total_modules,
            COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.id END) as completed_modules
        FROM enrollments e
        WHERE e.student_id = %s
    """
    
    # 2. Recent Achievements
    query_achievements = """
        SELECT a.name, a.icon, ua.earned_at
        FROM user_achievements ua
        JOIN achievements a ON ua.achievement_id = a.id
        WHERE ua.user_id = %s
        ORDER BY ua.earned_at DESC
        LIMIT 3
    """
    
    # 3. Weekly Activity (Mocked for now since event_repository in mongo is complex to aggregate here)
    weekly_activity = [
        {"day": "Lun", "puntos": 0},
        {"day": "Mar", "puntos": 0},
        {"day": "Mié", "puntos": 0},
        {"day": "Jue", "puntos": 0},
        {"day": "Vie", "puntos": 0},
        {"day": "Sáb", "puntos": 0},
        {"day": "Dom", "puntos": 0},
    ]

    progress = {"completedLessons": 0, "totalLessons": 0, "currentModule": "Ninguno", "nextLesson": "Ninguno"}
    recent_achievements = []

    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query_progress, (token_data.user_id,))
        prog_row = cursor.fetchone()
        if prog_row:
            progress["totalLessons"] = prog_row[0] or 0
            progress["completedLessons"] = prog_row[1] or 0
            
        cursor.execute(query_achievements, (token_data.user_id,))
        achv_rows = cursor.fetchall()
        for row in achv_rows:
            # earned_at is datetime, format as string or "Hace x dias"
            recent_achievements.append({
                "name": row[0],
                "icon": row[1] or "star",
                "earnedAt": row[2].strftime("%Y-%m-%d") if row[2] else ""
            })
            
    return {
        "success": True,
        "dashboard": {
            "progress": progress,
            "recentAchievements": recent_achievements,
            "weeklyActivity": weekly_activity
        }
    }

@app.get("/api/dashboard/admin", tags=["Admin"])
async def get_admin_dashboard(token_data: TokenData = Depends(verify_admin)):
    """Get admin dashboard stats"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    stats = {"totalUsers": 0, "activeStudents": 0, "activeTeachers": 0, "totalModules": 0}
    
    query = """
        SELECT
            (SELECT COUNT(*) FROM users) as total_users,
            (SELECT COUNT(*) FROM users WHERE role = 'student' AND is_active = TRUE) as active_students,
            (SELECT COUNT(*) FROM users WHERE role = 'teacher' AND is_active = TRUE) as active_teachers,
            (SELECT COUNT(*) FROM modules) as total_modules
    """
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            stats["totalUsers"] = row[0]
            stats["activeStudents"] = row[1]
            stats["activeTeachers"] = row[2]
            stats["totalModules"] = row[3]
            
    return {"success": True, "stats": stats}

@app.get("/api/challenges", tags=["Challenges"])
async def list_challenges(token_data: TokenData = Depends(verify_token)):
    """Get all challenges"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    query = """
        SELECT c.id, c.title, c.description, c.difficulty, c.points, u.full_name as author_name
        FROM challenges c
        JOIN users u ON c.teacher_id = u.id
        ORDER BY c.created_at DESC
    """
    
    challenges = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            challenges.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "difficulty": row[3],
                "points": row[4],
                "author_name": row[5]
            })
            
    return {"success": True, "challenges": challenges}

@app.post("/api/challenges", tags=["Challenges"])
async def create_challenge(request: Request, token_data: TokenData = Depends(verify_teacher)):
    """Create a new challenge"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    body = await request.json()
    title = body.get("title")
    description = body.get("description")
    instructions = body.get("instructions")
    difficulty = body.get("difficulty", 1)
    points = body.get("points", 100)
    
    query = """
        INSERT INTO challenges (title, description, instructions, difficulty, points, teacher_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (title, description, instructions, difficulty, points, token_data.user_id))
        challenge_id = cursor.fetchone()[0]
        
    return {"success": True, "challenge_id": challenge_id}

@app.post("/api/classes/{class_id}/unenroll/{student_id}", tags=["Teacher"])
async def unenroll_student(class_id: int, student_id: int, token_data: TokenData = Depends(verify_teacher)):
    """Unenroll a student from a class/module"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    
    query = "DELETE FROM enrollments WHERE module_id = %s AND student_id = %s"
    
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (class_id, student_id))
        
    return {"success": True, "message": "Student unenrolled"}

# ============================================
# Routes - Classes System
# ============================================

# --- Classes CRUD ---

@app.get("/api/classes", tags=["Classes"])
async def list_classes():
    """List all published classes"""
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
        GROUP BY c.id, u.full_name
        ORDER BY c.created_at DESC
    """
    classes = []
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query)
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

@app.get("/api/classes/{class_id}", tags=["Classes"])
async def get_class(class_id: int):
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
    query = """
        INSERT INTO class_enrollments (student_id, class_id, status)
        VALUES (%s, %s, 'pending')
        ON CONFLICT (student_id, class_id) DO UPDATE SET status = 'pending'
        RETURNING id
    """
    with PostgresConnection.get_cursor() as cursor:
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
        WHERE ce.student_id = %s AND ce.status = 'approved'
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

# --- Class Modules CRUD ---

@app.get("/api/classes/{class_id}/modules", tags=["Classes"])
async def list_class_modules(class_id: int):
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

@app.post("/api/classes/{class_id}/modules", tags=["Classes"])
async def create_class_module(class_id: int, request: ClassModuleCreate, token_data: TokenData = Depends(verify_teacher)):
    """Create a module in a class"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
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
    """Update a class module"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
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
    """Delete a class module"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = "DELETE FROM class_modules WHERE id = %s AND class_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id, class_id))
    return {"success": True, "message": "Module deleted"}

# --- Class Exercises CRUD ---

@app.get("/api/classes/{class_id}/modules/{module_id}/exercises", tags=["Classes"])
async def list_class_exercises(class_id: int, module_id: int):
    """List exercises for a class module"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = """
        SELECT ce.id, ce.title, ce.description, ce.instructions, ce.exercise_type,
               ce.difficulty, ce.points, ce."order", ce.metadata
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
                "metadata": row[8]
            })
    return {"success": True, "exercises": exercises}

@app.post("/api/classes/{class_id}/modules/{module_id}/exercises", tags=["Classes"])
async def create_class_exercise(
    class_id: int, module_id: int, request: ClassExerciseCreate,
    token_data: TokenData = Depends(verify_teacher)
):
    """Create an exercise in a class module"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    import json
    query = """
        INSERT INTO class_exercises (class_module_id, title, description, instructions, exercise_type, difficulty, points, "order", metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    metadata_json = json.dumps(request.metadata) if request.metadata else '{}'
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (module_id, request.title, request.description, request.instructions,
                               request.exercise_type, request.difficulty, request.points,
                               request.order, metadata_json))
        exercise_id = cursor.fetchone()[0]
    return {"success": True, "exercise_id": exercise_id}

@app.put("/api/classes/{class_id}/modules/{module_id}/exercises/{exercise_id}", tags=["Classes"])
async def update_class_exercise(
    class_id: int, module_id: int, exercise_id: int,
    request: ClassExerciseUpdate, token_data: TokenData = Depends(verify_teacher)
):
    """Update a class exercise"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    import json
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
    """Delete a class exercise"""
    from infrastructure.adapters.output.postgres.connection import PostgresConnection
    query = "DELETE FROM class_exercises WHERE id = %s AND class_module_id = %s"
    with PostgresConnection.get_cursor() as cursor:
        cursor.execute(query, (exercise_id, module_id))
    return {"success": True, "message": "Exercise deleted"}

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
