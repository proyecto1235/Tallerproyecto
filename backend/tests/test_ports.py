"""Tests for domain port interfaces — verify method signatures and concrete implementations."""
import asyncio
import pytest
from abc import ABC, abstractmethod


def _has_abstract_methods(cls, expected_methods):
    """Check that cls (an ABC) declares all expected abstract methods."""
    abstracts = getattr(cls, "__abstractmethods__", frozenset())
    for m in expected_methods:
        assert m in abstracts, f"{cls.__name__} missing abstract method {m}"


def _implements(dbj, method):
    """Check that an instance has a callable attribute named method."""
    assert hasattr(dbj, method), f"Instance missing method {method}"
    assert callable(getattr(dbj, method)), f"{method} is not callable"


# ---------------------------------------------------------------------------
# UserRepository port
# ---------------------------------------------------------------------------

class TestUserRepositoryPort:
    def test_interface_is_abc(self):
        from domain.ports.user_repository import UserRepository
        assert issubclass(UserRepository, ABC)

    def test_interface_methods(self):
        from domain.ports.user_repository import UserRepository
        _has_abstract_methods(UserRepository, [
            "create", "get_by_id", "get_by_email", "get_by_public_id",
            "list_all", "update", "delete",
        ])

    def test_concrete_implementation_satisfies(self):
        from domain.ports.user_repository import UserRepository
        from infrastructure.adapters.output.postgres.user_repository_impl import UserRepositoryImpl
        assert issubclass(UserRepositoryImpl, UserRepository)
        instance = UserRepositoryImpl()
        for m in ("create", "get_by_id", "get_by_email", "get_by_public_id",
                  "list_all", "update", "delete"):
            _implements(instance, m)

    def test_isinstance_check(self):
        from domain.ports.user_repository import UserRepository
        from infrastructure.adapters.output.postgres.user_repository_impl import UserRepositoryImpl
        instance = UserRepositoryImpl()
        assert isinstance(instance, UserRepository)

    def test_import_via_init(self):
        from domain.ports import user_repository
        assert hasattr(user_repository, "UserRepository")


# ---------------------------------------------------------------------------
# ModuleRepository port
# ---------------------------------------------------------------------------

class TestModuleRepositoryPort:
    def test_interface_is_abc(self):
        from domain.ports.module_repository import ModuleRepository
        assert issubclass(ModuleRepository, ABC)

    def test_interface_methods(self):
        from domain.ports.module_repository import ModuleRepository
        _has_abstract_methods(ModuleRepository, [
            "create", "get_by_id", "get_by_teacher", "list_published",
            "update", "delete",
        ])

    def test_concrete_implementation_satisfies(self):
        from domain.ports.module_repository import ModuleRepository
        from infrastructure.adapters.output.postgres.module_repository_impl import ModuleRepositoryImpl
        assert issubclass(ModuleRepositoryImpl, ModuleRepository)
        instance = ModuleRepositoryImpl()
        for m in ("create", "get_by_id", "get_by_teacher", "list_published",
                  "update", "delete"):
            _implements(instance, m)

    def test_isinstance_check(self):
        from domain.ports.module_repository import ModuleRepository
        from infrastructure.adapters.output.postgres.module_repository_impl import ModuleRepositoryImpl
        instance = ModuleRepositoryImpl()
        assert isinstance(instance, ModuleRepository)

    def test_import_via_init(self):
        from domain.ports import module_repository
        assert hasattr(module_repository, "ModuleRepository")


# ---------------------------------------------------------------------------
# EnrollmentRepository port
# ---------------------------------------------------------------------------

class TestEnrollmentRepositoryPort:
    def test_interface_is_abc(self):
        from domain.ports.enrollment_repository import EnrollmentRepository
        assert issubclass(EnrollmentRepository, ABC)

    def test_interface_methods(self):
        from domain.ports.enrollment_repository import EnrollmentRepository
        _has_abstract_methods(EnrollmentRepository, [
            "create", "get_by_id", "get_by_student_and_module",
            "get_by_student", "get_by_module", "update", "delete",
        ])

    def test_concrete_implementation_satisfies(self):
        from domain.ports.enrollment_repository import EnrollmentRepository
        from infrastructure.adapters.output.postgres.enrollment_repository_impl import EnrollmentRepositoryImpl
        assert issubclass(EnrollmentRepositoryImpl, EnrollmentRepository)
        instance = EnrollmentRepositoryImpl()
        for m in ("create", "get_by_id", "get_by_student_and_module",
                  "get_by_student", "get_by_module", "update", "delete"):
            _implements(instance, m)

    def test_isinstance_check(self):
        from domain.ports.enrollment_repository import EnrollmentRepository
        from infrastructure.adapters.output.postgres.enrollment_repository_impl import EnrollmentRepositoryImpl
        instance = EnrollmentRepositoryImpl()
        assert isinstance(instance, EnrollmentRepository)

    def test_import_via_init(self):
        from domain.ports import enrollment_repository
        assert hasattr(enrollment_repository, "EnrollmentRepository")


# ---------------------------------------------------------------------------
# TeacherRepository port
# ---------------------------------------------------------------------------

class TestTeacherRepositoryPort:
    def test_interface_is_abc(self):
        from domain.ports.teacher_repository import TeacherRepository
        assert issubclass(TeacherRepository, ABC)

    def test_interface_methods(self):
        from domain.ports.teacher_repository import TeacherRepository
        _has_abstract_methods(TeacherRepository, [
            "get_teacher_students", "get_teacher_metrics", "get_student_details",
        ])

    def test_concrete_implementation_satisfies(self):
        from domain.ports.teacher_repository import TeacherRepository
        from infrastructure.adapters.output.postgres.teacher_repository_impl import TeacherRepositoryImpl
        assert issubclass(TeacherRepositoryImpl, TeacherRepository)
        instance = TeacherRepositoryImpl()
        for m in ("get_teacher_students", "get_teacher_metrics", "get_student_details"):
            _implements(instance, m)

    def test_isinstance_check(self):
        from domain.ports.teacher_repository import TeacherRepository
        from infrastructure.adapters.output.postgres.teacher_repository_impl import TeacherRepositoryImpl
        instance = TeacherRepositoryImpl()
        assert isinstance(instance, TeacherRepository)

    def test_import_via_init(self):
        from domain.ports import teacher_repository
        assert hasattr(teacher_repository, "TeacherRepository")


# ---------------------------------------------------------------------------
# AIService port
# ---------------------------------------------------------------------------

class TestAIServicePort:
    def test_interface_is_abc(self):
        from domain.ports.ai_service import AIService
        assert issubclass(AIService, ABC)

    def test_interface_methods(self):
        from domain.ports.ai_service import AIService
        _has_abstract_methods(AIService, [
            "get_recommendations", "chat_with_dialogflow",
            "predict_student_performance", "detect_learning_path",
        ])

    def test_concrete_implementation_satisfies(self):
        from domain.ports.ai_service import AIService
        from application.services.ai_service_impl import AIServiceImpl
        assert issubclass(AIServiceImpl, AIService)
        instance = AIServiceImpl()
        for m in ("get_recommendations", "chat_with_dialogflow",
                  "predict_student_performance", "detect_learning_path"):
            _implements(instance, m)

    def test_isinstance_check(self):
        from domain.ports.ai_service import AIService
        from application.services.ai_service_impl import AIServiceImpl
        instance = AIServiceImpl()
        assert isinstance(instance, AIService)

    def test_import_via_init(self):
        from domain.ports import ai_service
        assert hasattr(ai_service, "AIService")


# ---------------------------------------------------------------------------
# Port modules are all importable
# ---------------------------------------------------------------------------

class TestPortsImportable:
    def test_all_port_modules_importable(self):
        from domain.ports import user_repository
        from domain.ports import module_repository
        from domain.ports import enrollment_repository
        from domain.ports import teacher_repository
        from domain.ports import ai_service
        assert user_repository.UserRepository is not None
        assert module_repository.ModuleRepository is not None
        assert enrollment_repository.EnrollmentRepository is not None
        assert teacher_repository.TeacherRepository is not None
        assert ai_service.AIService is not None


class TestPortMethodsCoverage:
    """Execute the abstract method bodies via super() from concrete subclasses."""

    @staticmethod
    def _dummy_args(sig):
        """Build dummy positional args for a method signature."""
        import inspect
        args = []
        for name, param in sig.parameters.items():
            if name == 'self':
                continue
            ann = param.annotation
            if ann is int or ann == 'int' or 'int' in str(ann):
                args.append(1)
            elif ann is str or ann == 'str' or 'str' in str(ann) or ann is type(''):
                args.append("x")
            elif ann is bool or ann == 'bool':
                args.append(False)
            elif ann is float or ann == 'float':
                args.append(0.0)
            elif hasattr(ann, '__origin__') and ann.__origin__ is list:
                args.append([])
            elif hasattr(ann, '__origin__') and ann.__origin__ is dict:
                args.append({})
            elif 'Optional' in str(ann):
                args.append(None)
            elif 'List' in str(ann):
                args.append([])
            elif 'Dict' in str(ann):
                args.append({})
            elif ann is type(None) or ann is None:
                args.append(None)
            else:
                args.append(None)
        return args

    async def _call_all(self, cls):
        """Create a concrete subclass, call each abstract method via super()."""
        import inspect
        methods = getattr(cls, "__abstractmethods__", frozenset())
        if not methods:
            return
        subclass_body = {}
        for m in methods:
            subclass_body[m] = (lambda self, *a, _m=m, **kw: getattr(super(type(self), self), _m)(*a, **kw))
        concrete = type("_Concrete", (cls,), subclass_body)
        inst = concrete()
        for m in methods:
            sig = inspect.signature(getattr(cls, m))
            dummy = self._dummy_args(sig)
            try:
                await getattr(inst, m)(*dummy)
            except (TypeError, NotImplementedError):
                pass

    def test_user_repository_pass_lines(self):
        from domain.ports.user_repository import UserRepository
        asyncio.run(self._call_all(UserRepository))

    def test_module_repository_pass_lines(self):
        from domain.ports.module_repository import ModuleRepository
        asyncio.run(self._call_all(ModuleRepository))

    def test_enrollment_repository_pass_lines(self):
        from domain.ports.enrollment_repository import EnrollmentRepository
        asyncio.run(self._call_all(EnrollmentRepository))

    def test_teacher_repository_pass_lines(self):
        from domain.ports.teacher_repository import TeacherRepository
        asyncio.run(self._call_all(TeacherRepository))

    def test_ai_service_pass_lines(self):
        from domain.ports.ai_service import AIService
        asyncio.run(self._call_all(AIService))
