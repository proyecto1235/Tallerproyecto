from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from config.database_init import initialize_database
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository
from app.exceptions import register_error_handlers
from app.logging_config import logger

# ---- Router Imports ----
from infrastructure.adapters.input.auth_router import router as auth_router
from infrastructure.adapters.input.users_router import router as users_router
from infrastructure.adapters.input.modules_router import router as modules_router
from infrastructure.adapters.input.exercises_router import router as exercises_router
from infrastructure.adapters.input.challenges_router import router as challenges_router
from infrastructure.adapters.input.classes_router import router as classes_router
from infrastructure.adapters.input.ai_router import router as ai_router
from infrastructure.adapters.input.analytics_router import router as analytics_router
from infrastructure.adapters.input.dashboard_router import router as dashboard_router
from infrastructure.adapters.input.admin_router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Robolearn API...")
    if settings.google_credentials_path:
        cred_path = os.path.abspath(settings.google_credentials_path)
        if os.path.exists(cred_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
            logger.info(f"Google credentials loaded from: {cred_path}")
        else:
            logger.warning(f"Google credentials file not found at: {cred_path}")
    initialize_database()
    PostgresConnection.init_pool()
    yield
    logger.info("Shutting down Robolearn API...")
    PostgresConnection.close_pool()
    EventRepository.close()


app = FastAPI(title="Robolearn API", version="1.0.0", lifespan=lifespan)

register_error_handlers(app)

# ---- Middleware ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        logger.info(f"[AUDIT] {ip} - {request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.node_env == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if "Content-Security-Policy" not in response.headers:
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
    return response


# ---- Include Routers ----
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(modules_router)
app.include_router(exercises_router)
app.include_router(challenges_router)
app.include_router(classes_router)
app.include_router(ai_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)
app.include_router(admin_router)

# ---- Health ----
@app.get("/", tags=["Health"])
async def root():
    return {"message": "Robolearn API running", "version": "1.0.0"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"success": True, "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
