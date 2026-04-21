# Arquitectura Hexagonal - Robolearn

## Introducción a la Arquitectura Hexagonal

La arquitectura hexagonal (también llamada "puertos y adaptadores") es un patrón arquitectónico que aísla la lógica de negocio del mundo exterior. Esto permite que la aplicación sea agnóstica respecto a los detalles de implementación como base de datos, frameworks HTTP, etc.

## Principios Clave

1. **Independencia de Framework** - La lógica de negocio no depende de FastAPI
2. **Independencia de BD** - Puedes cambiar PostgreSQL por otra BD sin cambiar la lógica
3. **Testabilidad** - Fácil escribir tests sin necesidad de BD real
4. **Flexibilidad** - Agregar nuevas adapters es simple

## Capas de la Arquitectura

### 1. Capa de Dominio (`domain/`)
El corazón de la aplicación. Contiene la lógica de negocio pura.

#### Entidades (`domain/entities/`)
Representan conceptos del negocio con identidad única:

```python
# user.py
class User:
    def __init__(self, id, email, password_hash, full_name, role):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.role = role  # student, teacher, admin
    
    def to_dict(self):
        # Serializar para respuestas HTTP
        pass
```

**Características:**
- No conocen sobre BD, HTTP, frameworks
- Contienen lógica de negocio pura
- Son testables sin dependencias externas

#### Puertos (`domain/ports/`)
Interfaces/contratos que definen cómo interactuar con sistemas externos.

```python
# user_repository.py
from abc import ABC, abstractmethod

class UserRepository(ABC):
    """Puerto para persistencia de usuarios"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
```

**Propósito:**
- Definen contratos sin implementación
- Permiten inyección de dependencias
- Aíslan el dominio de detalles técnicos

#### Value Objects (`domain/valueObjects/`)
Objetos sin identidad única, inmutables, definidos por su contenido:

```python
# progress.py
class Progress:
    def __init__(self, user_id, module_id, percentage, ...):
        if not 0 <= percentage <= 100:
            raise ValueError("Porcentaje inválido")
        self.user_id = user_id
        self.module_id = module_id
        self.percentage = percentage
```

### 2. Capa de Aplicación (`application/`)
Orquesta el dominio para resolver casos de uso específicos.

#### Use Cases (`application/useCases/`)
Implementan un flujo de negocio específico:

```python
# register_user.py
class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, email, password, full_name):
        # 1. Validar entrada
        # 2. Hashear contraseña
        # 3. Crear entidad User
        # 4. Guardar con repositorio
        # 5. Retornar resultado
```

**Características:**
- Implementan lógica de orchestration
- Usan repositorios inyectados
- Retornan DTOs (no entidades)

#### Servicios (`application/services/`)
Servicios reutilizables que múltiples casos de uso pueden usar:

```python
# ai_recommender.py
class RecommendationService:
    def __init__(self, ai_service: AIService, event_repo: EventRepository):
        self.ai_service = ai_service
        self.event_repo = event_repo
    
    async def get_personalized_recommendations(self, user_id: int):
        # Usar servicios inyectados
```

### 3. Capa de Infraestructura (`infrastructure/`)
Implementa los puertos con detalles técnicos reales.

#### Adaptadores de Salida (`infrastructure/adapters/output/`)
Implementan los puertos de persistencia:

```python
# postgres/user_repository_impl.py
class UserRepositoryImpl(UserRepository):
    """Implementación real usando PostgreSQL"""
    
    async def create(self, user: User) -> User:
        # Código SQL real
        cursor.execute("INSERT INTO users ...")
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        # Consulta SQL real
        cursor.execute("SELECT * FROM users WHERE email = %s")
        return self._row_to_user(row)
```

**Características:**
- Concretas, específicas para cada tecnología
- Usan drivers reales (psycopg2, pymongo)
- Convertir entre BD y entidades de dominio

#### Adaptadores de Entrada (`infrastructure/adapters/input/`)
Exponen la aplicación al mundo exterior:

```python
# main.py (FastAPI)
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    use_case = RegisterUserUseCase(user_repository)
    result = await use_case.execute(
        request.email,
        request.password,
        request.full_name
    )
    return result
```

## Flujo de una Solicitud

```
Solicitud HTTP
    ↓
[Adapter de Entrada] - main.py (FastAPI route)
    ↓
[Use Case] - RegisterUserUseCase
    ↓
[Entidad de Dominio] - User, validación
    ↓
[Puerto] - UserRepository (contrato)
    ↓
[Adapter de Salida] - UserRepositoryImpl (PostgreSQL)
    ↓
Acceso a BD
    ↓
[Respuesta serializada]
    ↓
HTTP Response
```

## Inyección de Dependencias

En FastAPI, se inyectan las dependencias directamente:

```python
# Forma 1: En el route
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    # Crear instancias
    user_repo = UserRepositoryImpl()
    use_case = RegisterUserUseCase(user_repo)
    result = await use_case.execute(...)

# Forma 2: Mejor - Usar dependency container (futuro)
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    user_repository = providers.Singleton(UserRepositoryImpl)
    register_use_case = providers.Factory(
        RegisterUserUseCase,
        user_repository=user_repository
    )

# En el route:
@app.post("/api/auth/register")
async def register(
    request: RegisterRequest,
    use_case = Depends(lambda: container.register_use_case())
):
    result = await use_case.execute(...)
```

## Beneficios Práctica

### 1. Testing
Sin necesidad de BD real:

```python
# test_register_user.py
class MockUserRepository(UserRepository):
    async def create(self, user: User) -> User:
        return user

def test_register_user():
    repo = MockUserRepository()
    use_case = RegisterUserUseCase(repo)
    result = await use_case.execute(
        "test@example.com",
        "password123",
        "Test User"
    )
    assert result.success
```

### 2. Cambiar BD
Cambiar de PostgreSQL a otra BD:

```python
# Antes: PostgreSQL
class UserRepositoryImpl(UserRepository):
    async def create(self, user: User) -> User:
        cursor.execute("INSERT INTO users ...")

# Después: MongoDB
class UserRepositoryMongo(UserRepository):
    async def create(self, user: User) -> User:
        collection.insert_one(user.to_dict())

# En main.py, solo cambiar:
# user_repository = UserRepositoryImpl()
user_repository = UserRepositoryMongo()
```

### 3. Agregar Features
Agregar nuevo use case sin tocar existentes:

```python
# Nuevo use case
class GetUserRecommendationsUseCase:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def execute(self, user_id: int):
        # Nueva lógica
        pass

# En main.py:
@app.get("/api/recommendations")
async def get_recommendations(user_id: int):
    use_case = GetUserRecommendationsUseCase(ai_service)
    return await use_case.execute(user_id)
```

## Estructura de Carpetas Explicada

```
backend/
├── app/
│   └── main.py
│       # Entra aquí: HTTP Request
│       # Crea instancias de Use Cases
│       # Retorna: HTTP Response
│
├── config/
│   └── settings.py
│       # Configuración centralizada
│       # Variables de entorno
│       # Parámetros globales
│
├── domain/                    ← NÚCLEO (Lógica Pura)
│   ├── entities/
│   │   ├── user.py           # Entity: User
│   │   ├── module.py         # Entity: Module
│   │   └── exercise.py       # Entity: Exercise
│   ├── ports/
│   │   ├── user_repository.py        # Interface
│   │   ├── module_repository.py      # Interface
│   │   └── ai_service.py             # Interface
│   └── valueObjects/
│       └── progress.py       # Value Object: Progress
│
├── application/               ← ORQUESTACIÓN
│   ├── useCases/
│   │   ├── register_user.py          # Use Case
│   │   ├── get_recommendations.py    # Use Case
│   │   └── enroll_student.py         # Use Case
│   └── services/
│       ├── ai_recommender.py         # Servicio
│       └── ai_service_impl.py        # Implementación
│
└── infrastructure/            ← DETALLES TÉCNICOS
    └── adapters/
        ├── input/
        │   ├── main.py               # Adapter: HTTP (FastAPI)
        │   ├── user_controller.py    # Controlador
        │   └── module_controller.py  # Controlador
        └── output/
            ├── postgres/
            │   ├── connection.py                   # Pool de conexiones
            │   ├── user_repository_impl.py        # Adapter: PostgreSQL
            │   └── module_repository_impl.py      # Adapter: PostgreSQL
            └── mongo/
                ├── db.py                          # Conexión
                └── event_repository_impl.py       # Adapter: MongoDB
```

## Decisiones de Diseño

### ¿Por qué async/await?
- FastAPI nativo
- Mejor performance con I/O (BD, HTTP)
- Permite manejo de múltiples requests

### ¿Por qué PostgreSQL + MongoDB?
- **PostgreSQL**: Datos estructurados (usuarios, módulos)
- **MongoDB**: Datos no estructurados (eventos, métricas)

### ¿Por qué JWT?
- Stateless (sin sesiones en servidor)
- Escalable
- Funciona bien en microservicios

### ¿Por qué Scikit-learn?
- Ligero (ML sin deep learning)
- Búsqueda de vecinos cercanos (NearestNeighbors)
- Recomendaciones basadas en similitud

## Extensión Futura

### Agregar Redis (Caché)

```python
# Nuevo puerto
class CacheRepository(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int):
        pass

# Implementación
class RedisCache(CacheRepository):
    async def get(self, key: str):
        return await self.redis.get(key)
    
    async def set(self, key: str, value: Any, ttl: int):
        await self.redis.set(key, value, ex=ttl)

# Usar en use cases
class RegisterUserUseCase:
    def __init__(self, user_repo, cache_repo):
        self.user_repo = user_repo
        self.cache = cache_repo
    
    async def execute(self, email, ...):
        # Lógica
        # Cachear resultado
        await self.cache.set(f"user:{email}", user, ttl=3600)
```

### Agregar Event Bus

```python
# Nuevo puerto
class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent):
        pass

# Use cases publican eventos
class RegisterUserUseCase:
    def __init__(self, user_repo, event_bus):
        self.event_bus = event_bus
    
    async def execute(self, email, ...):
        user = await self.user_repo.create(...)
        # Publicar evento
        event = UserRegisteredEvent(user_id=user.id, email=user.email)
        await self.event_bus.publish(event)
```

## Referencias

- [Uncle Bob's Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Ports and Adapters Pattern](https://alistair.cockburn.us/hexagonal-architecture/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)

---

**Versión**: 1.0.0  
**Última actualización**: 2026-04-21
