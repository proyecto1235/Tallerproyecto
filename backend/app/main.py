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
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository
from application.services.ai_service_impl import AIServiceImpl
from application.services.ai_recommender import RecommendationService
from application.useCases.register_user import RegisterUserUseCase
from application.useCases.get_recommendations import GetRecommendationsUseCase
from application.useCases.enroll_student import EnrollStudentUseCase
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

# ============================================
# Lifespan Events
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Robolearn API...")
    
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
# Routes - Modules
# ============================================

@app.get("/api/modules", tags=["Modules"])
async def list_modules():
    """List all published modules"""
    modules = await module_repository.list_published()
    return {
        "success": True,
        "modules": [m.to_dict() for m in modules]
    }

@app.get("/api/modules/{module_id}", tags=["Modules"])
async def get_module(module_id: int):
    """Get module by ID"""
    module = await module_repository.get_by_id(module_id)
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {"success": True, "module": module.to_dict()}

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
    use_case = EnrollStudentUseCase(user_repository, module_repository, event_repository)
    result = await use_case.execute(token_data.user_id, module_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
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
    return {
        "success": True,
        "metrics": {
            "active_students": 15,
            "average_score": 85,
            "alerts": ["Student 3 is struggling with loops"]
        }
    }

# ============================================
# Routes - Admin
# ============================================

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
