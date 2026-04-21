from typing import Optional, List
from domain.entities.module import Module, ContentStatus
from domain.ports.module_repository import ModuleRepository
from infrastructure.adapters.output.postgres.connection import PostgresConnection
from datetime import datetime

class ModuleRepositoryImpl(ModuleRepository):
    """PostgreSQL implementation of ModuleRepository"""
    
    async def create(self, module: Module) -> Module:
        """Create a new module"""
        query = """
            INSERT INTO modules (title, description, teacher_id, status, "order", is_published, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    module.title,
                    module.description,
                    module.teacher_id,
                    module.status.value,
                    module.order,
                    module.is_published,
                    module.created_at,
                    module.updated_at,
                ),
            )
            module_id = cursor.fetchone()[0]
            module.id = module_id
            return module
    
    async def get_by_id(self, module_id: int) -> Optional[Module]:
        """Get module by ID"""
        query = """
            SELECT id, title, description, teacher_id, status, "order", is_published, created_at, updated_at 
            FROM modules WHERE id = %s
        """
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (module_id,))
            row = cursor.fetchone()
            return self._row_to_module(row) if row else None
    
    async def get_by_teacher(self, teacher_id: int) -> List[Module]:
        """Get modules by teacher"""
        query = """
            SELECT id, title, description, teacher_id, status, "order", is_published, created_at, updated_at 
            FROM modules WHERE teacher_id = %s ORDER BY "order" ASC
        """
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (teacher_id,))
            rows = cursor.fetchall()
            return [self._row_to_module(row) for row in rows]
    
    async def list_published(self) -> List[Module]:
        """Get all published modules"""
        query = """
            SELECT id, title, description, teacher_id, status, "order", is_published, created_at, updated_at 
            FROM modules WHERE is_published = TRUE AND status = 'approved' ORDER BY "order" ASC
        """
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_module(row) for row in rows]
    
    async def update(self, module: Module) -> Module:
        """Update module"""
        query = """
            UPDATE modules 
            SET title = %s, description = %s, teacher_id = %s, status = %s, 
                "order" = %s, is_published = %s, updated_at = %s
            WHERE id = %s
        """
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    module.title,
                    module.description,
                    module.teacher_id,
                    module.status.value,
                    module.order,
                    module.is_published,
                    datetime.now(),
                    module.id,
                ),
            )
        return module
    
    async def delete(self, module_id: int) -> bool:
        """Delete module"""
        query = "DELETE FROM modules WHERE id = %s"
        
        with PostgresConnection.get_cursor() as cursor:
            cursor.execute(query, (module_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def _row_to_module(row) -> Module:
        """Convert database row to Module entity"""
        return Module(
            id=row[0],
            title=row[1],
            description=row[2],
            teacher_id=row[3],
            status=ContentStatus(row[4]),
            order=row[5],
            is_published=row[6],
            created_at=row[7],
            updated_at=row[8],
        )
