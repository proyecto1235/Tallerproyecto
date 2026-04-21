from domain.entities.user import User, UserRole
from domain.ports.user_repository import UserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterUserUseCase:
    """Use case for user registration"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(
        self,
        email: str,
        password: str,
        full_name: str,
        request_teacher: bool = False
    ) -> dict:
        """Register a new user"""
        # Validate inputs
        if not email or not password or not full_name:
            return {"success": False, "error": "Todos los campos son requeridos"}
        
        if len(password) < 6:
            return {"success": False, "error": "La contraseña debe tener al menos 6 caracteres"}
        
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            return {"success": False, "error": "El email ya está registrado"}
        
        # Hash password
        password_hash = pwd_context.hash(password)
        
        # Create user entity
        user = User(
            id=None,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=UserRole.TEACHER if request_teacher else UserRole.STUDENT,
        )
        
        # Save to repository
        created_user = await self.user_repository.create(user)
        
        return {
            "success": True,
            "user": {
                "id": created_user.id,
                "email": created_user.email,
                "full_name": created_user.full_name,
                "role": created_user.role.value,
            },
            "teacher_request_pending": request_teacher,
        }
