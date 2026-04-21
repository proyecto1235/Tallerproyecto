from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.module import Module

class ModuleRepository(ABC):
    """Port for module persistence"""
    
    @abstractmethod
    async def create(self, module: Module) -> Module:
        """Create a new module"""
        pass
    
    @abstractmethod
    async def get_by_id(self, module_id: int) -> Optional[Module]:
        """Get module by ID"""
        pass
    
    @abstractmethod
    async def get_by_teacher(self, teacher_id: int) -> List[Module]:
        """Get modules by teacher"""
        pass
    
    @abstractmethod
    async def list_published(self) -> List[Module]:
        """Get all published modules"""
        pass
    
    @abstractmethod
    async def update(self, module: Module) -> Module:
        """Update module"""
        pass
    
    @abstractmethod
    async def delete(self, module_id: int) -> bool:
        """Delete module"""
        pass
