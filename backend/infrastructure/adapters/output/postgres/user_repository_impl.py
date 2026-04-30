from typing import Optional, List
from domain.entities.user import User, UserRole, TeacherRequestStatus
from domain.ports.user_repository import UserRepository
from infrastructure.adapters.output.postgres.connection import PostgresConnection
import psycopg2
from datetime import datetime

class UserRepositoryImpl(UserRepository):
    """PostgreSQL implementation of UserRepository"""
    
    async def create(self, user: User) -> User:
        """Create a new user in PostgreSQL"""
        query = """
            INSERT INTO users (email, password_hash, full_name, role, is_active, avatar_url, bio, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    user.email,
                    user.password_hash,
                    user.full_name,
                    user.role.value,
                    user.is_active,
                    user.avatar_url,
                    user.bio,
                    user.created_at,
                    user.updated_at,
                ),
            )
            user_id = cursor.fetchone()[0]
            user.id = user_id
            return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = "SELECT id, email, password_hash, full_name, role, is_active, teacher_request_status, avatar_url, bio, created_at, updated_at FROM users WHERE id = %s"
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = "SELECT id, email, password_hash, full_name, role, is_active, teacher_request_status, avatar_url, bio, created_at, updated_at FROM users WHERE email = %s"
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
    
    async def list_all(self) -> List[User]:
        """Get all users"""
        query = "SELECT id, email, password_hash, full_name, role, is_active, teacher_request_status, avatar_url, bio, created_at, updated_at FROM users ORDER BY created_at DESC"
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]
    
    async def update(self, user: User) -> User:
        """Update user"""
        query = """
            UPDATE users 
            SET email = %s, password_hash = %s, full_name = %s, role = %s, 
                is_active = %s, teacher_request_status = %s, avatar_url = %s, bio = %s, updated_at = %s
            WHERE id = %s
        """
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    user.email,
                    user.password_hash,
                    user.full_name,
                    user.role.value,
                    user.is_active,
                    user.teacher_request_status.value if user.teacher_request_status else None,
                    user.avatar_url,
                    user.bio,
                    datetime.now(),
                    user.id,
                ),
            )
        return user
    
    async def delete(self, user_id: int) -> bool:
        """Delete user"""
        query = "DELETE FROM users WHERE id = %s"
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def _row_to_user(row) -> User:
        """Convert database row to User entity"""
        return User(
            id=row[0],
            email=row[1],
            password_hash=row[2],
            full_name=row[3],
            role=UserRole(row[4]),
            is_active=row[5],
            teacher_request_status=TeacherRequestStatus(row[6]) if row[6] else None,
            avatar_url=row[7],
            bio=row[8],
            created_at=row[9],
            updated_at=row[10],
        )
