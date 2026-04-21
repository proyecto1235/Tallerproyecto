from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
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

# ============================================
# Lifespan Events
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Robolearn API...")
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

async def verify_token(credentials: HTTPAuthCredentials) -> TokenData:
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
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
async def register(request: RegisterRequest):
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
    
    return {
        "success": True,
        "user": user,
        "token": token,
        "teacher_request_pending": result.get("teacher_request_pending", False)
    }

@app.post("/api/auth/login", tags=["Auth"])
async def login(request: LoginRequest):
    """Login user"""
    user = await user_repository.get_by_email(request.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not pwd_context.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is not active")
    
    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    })
    
    await event_repository.log_event(
        "user_login",
        user.id,
        {"email": user.email}
    )
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        },
        "token": token
    }

@app.post("/api/auth/logout", tags=["Auth"])
async def logout(token_data: TokenData = Depends(verify_token)):
    """Logout user"""
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
# Error Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "success": False,
        "error": exc.detail
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
