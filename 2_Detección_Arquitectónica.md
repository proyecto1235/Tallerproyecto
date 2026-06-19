# Auditoría de Software — Detección Arquitectónica

**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Auditor:** Asistente de IA (análisis automatizado)  
**Propósito:** Identificar patrones arquitectónicos presentes en el código fuente y estructura del proyecto.

---

## Metodología

Se analizó:
1. Estructura de directorios completa
2. Relaciones entre módulos (imports, dependencias)
3. Separación de responsabilidades
4. Patrones de diseño en el código fuente
5. Flujo de datos entre componentes
6. Archivos de configuración y despliegue

---

## Arquitecturas Evaluadas

### 1. Arquitectura Hexagonal (Puertos y Adaptadores)

| Aspecto | Detalle |
|---------|---------|
| **Estado** | ✅ Implementada |
| **Confianza** | Muy Alta (95%) |
| **Carpetas involucradas** | `backend/domain/`, `backend/application/`, `backend/infrastructure/` |

#### Evidencias

**Estructura explícita de capas:**

```
backend/
├── domain/              # Núcleo del negocio
│   ├── entities/        # 8 entidades de negocio
│   ├── ports/           # 5 interfaces/puertos
│   └── valueObjects/
├── application/         # Casos de uso y servicios
│   ├── services/        # 9 servicios de aplicación
│   ├── useCases/        # 5 casos de uso
│   └── services/analytics/
│       ├── analytics_router.py
│       ├── metrics_service.py
│       └── scheduler_service.py
├── infrastructure/      # Adaptadores (implementaciones)
│   └── adapters/
│       ├── output/      # Adaptadores de salida
│       │   ├── postgres/    # Repositorios PostgreSQL
│       │   ├── mongo/       # Repositorios MongoDB
│       │   ├── redis/       # Caché
│       │   └── docker/      # Sandbox Docker
│       └── input/      # Adaptadores de entrada
│           └── analytics_router.py
├── config/              # Configuración externa
├── app/                 # Framework (FastAPI) + Schemas
└── scripts/             # Scripts de inicialización
```

**Puertos (interfaces) definidos en `domain/ports/`:**

| Archivo | Propósito |
|---------|-----------|
| `user_repository.py` | Puerto de repositorio de usuarios |
| `module_repository.py` | Puerto de repositorio de módulos |
| `enrollment_repository.py` | Puerto de repositorio de inscripciones |
| `teacher_repository.py` | Puerto de repositorio de docentes |
| `ai_service.py` | Puerto de servicio de IA |

**Implementaciones concretas en `infrastructure/adapters/output/`:**

| Archivo | Puerto que implementa |
|---------|----------------------|
| `postgres/user_repository_impl.py` | `UserRepository` |
| `postgres/module_repository_impl.py` | `ModuleRepository` |
| `postgres/enrollment_repository_impl.py` | `EnrollmentRepository` |
| `postgres/teacher_repository_impl.py` | `TeacherRepository` |
| `mongo/event_repository_impl.py` | Eventos/logs (no definido como puerto explícito) |
| `mongo/behavioral_repository.py` | Repositorio conductual |
| `redis/cache.py` | Caché de IA |

**Inversión de dependencias** — Los casos de uso (`application/useCases/`) dependen de puertos (interfaces), no de implementaciones concretas:

```python
# application/useCases/get_recommendations.py
class GetRecommendationsUseCase:
    def __init__(self, ai_service: AIService, module_repository: ModuleRepository, ...):
        # Depende de interfaces, no de implementaciones
        ...
```

**Inyección de dependencias centralizada:**

```python
# backend/app/main.py líneas 124-130
from app.dependencies import (
    user_repository, module_repository, enrollment_repository, ...
)
# backend/app/dependencies.py (implícito) — punto único de wiring
```

#### Justificación Técnica

La estructura del backend sigue fielmente los principios de la **Arquitectura Hexagonal** (también conocida como Puertos y Adaptadores):

1. **Domain** contiene las entidades de negocio (`user.py`, `module.py`, `exercise.py`, etc.) y los puertos (interfaces) que definen contratos.
2. **Application** contiene la lógica de aplicación: casos de uso orquestados y servicios que coordinan el dominio.
3. **Infrastructure** contiene los adaptadores concretos que implementan los puertos (PostgreSQL, MongoDB, Redis, Docker).
4. **Config** mantiene la configuración externa (variables de entorno, conexiones).
5. **App** es el punto de entrada del framework (FastAPI), que conecta los adaptadores de entrada (REST) con los casos de uso.

El flujo es: **FastAPI (controller) → UseCase → Port (interface) ← Adapter (implementation)**. Ninguna capa interna conoce los detalles externos. Esto es prueba directa de **Arquitectura Hexagonal**.

---

### 2. Arquitectura por Capas (Layered Architecture)

| Aspecto | Detalle |
|---------|---------|
| **Estado** | ✅ Implementada (como subestructura de la hexagonal) |
| **Confianza** | Alta (75%) |
| **Carpetas involucradas** | `backend/domain/`, `backend/application/`, `backend/infrastructure/`, `backend/app/`, `backend/config/` |

#### Evidencias

La estructura de directorios revela una clara separación en capas:

```
Capa 1: Config        → backend/config/         (settings, database_init)
Capa 2: Domain        → backend/domain/          (entities, ports, valueObjects)
Capa 3: Application   → backend/application/     (services, useCases)
Capa 4: Infrastructure→ backend/infrastructure/  (adapters output/input)
Capa 5: Presentation  → backend/app/             (main.py, schemas, routers)
```

Las dependencias fluyen de arriba hacia abajo: `app/ → application/ → domain/ ← infrastructure/`. La capa de infraestructura implementa los puertos definidos en dominio (inversión de dependencia limpia).

#### Justificación Técnica

Si bien la arquitectura por capas está presente, es una consecuencia directa de aplicar Arquitectura Hexagonal. La diferencia clave es que en la arquitectura por capas tradicional, la capa superior depende de la inferior directamente. En Hexagonal, se invierte esa dependencia mediante puertos. Como ambas coexisten armoniosamente, se considera que la arquitectura por capas es **un subproducto natural** del diseño hexagonal, no un patrón independiente aquí.

---

### 3. MVC (Model-View-Controller)

| Aspecto | Detalle |
|---------|---------|
| **Estado** | ❌ No implementado |
| **Confianza** | Muy Alta (0%) |
| **Razón** | No existe carpeta `controllers/`, `views/` ni `models/` con ese rol. FastAPI usa routers, no controladores. El frontend usa App Router de Next.js (componentes + páginas), no vistas MVC. |

#### Evidencias

- **Backend**: No hay una carpeta `controllers/`. Las rutas se definen directamente en `backend/app/main.py` como funciones decoradas con `@app.get/post`. Coexisten con la lógica _inline_ en lugar de estar separadas en controladores.
- **Frontend**: Next.js App Router no sigue MVC. Usa componentes React en `frontend/app/` y `frontend/components/`, con server actions en `frontend/app/actions/`.
- **Modelos de datos**: Están en `backend/domain/entities/` (entidades de dominio) y `backend/app/schemas/` (DTOs de Pydantic), no en un directorio `models/` tradicional.

#### Justificación Técnica

MVC no es aplicable. El backend usa **routers + casos de uso + entidades** (no controllers + models + views). El frontend usa **componentes + server actions + hooks** (no views + controllers).

---

### 4. Microservicios

| Aspecto | Detalle |
|---------|---------|
| **Estado** | ❌ No implementado |
| **Confianza** | Alta (10%) — es un **monolito con servicios satélite** |

#### Evidencias

- **Backend único** — todo el backend es un solo proceso FastAPI en `backend/`.
- **Frontend único** — todo el frontend es un solo proceso Next.js.
- **Docker Compose** — todos los servicios se orquestan juntos, no como microservicios independientes.
- **Base de datos compartida** — PostgreSQL y MongoDB son accedidos por el mismo backend.
- **Sin API Gateway** — el frontend se comunica directamente con el backend.
- **Sin service discovery, message broker ni event bus** — no hay RabbitMQ, Kafka, NATS, etc.

#### Justificación Técnica

Aunque hay múltiples contenedores (backend, frontend, postgres, mongo, redis, ollama), esto **no** constituye microservicios. Son servicios de soporte (bases de datos, caché, IA) para un backend monolítico. No hay despliegue independiente, escalado autónomo ni comunicación asíncrona entre servicios de aplicación.

---

### 5. Modular Monolith

| Aspecto | Detalle |
|---------|---------|
| **Estado** | ✅ Implementado (como patrón de organización interna del monolito) |
| **Confianza** | Alta (80%) |
| **Carpetas involucradas** | `backend/application/services/ml/`, `backend/application/services/analytics/`, `backend/app/schemas/` |

#### Evidencias

El backend es un **monolito** (un solo proceso FastAPI) pero está organizado en **módulos internos** con alta cohesión:

```
backend/application/services/
├── ml/                   # Módulo de Machine Learning (12 archivos)
│   ├── orchestrator.py
│   ├── recommender.py
│   ├── feature_extractor.py
│   ├── dropout_predictor.py
│   └── ...
├── analytics/            # Módulo de Analítica (4 archivos)
│   ├── analytics_router.py
│   ├── metrics_service.py
│   └── scheduler_service.py
├── ai_service_impl.py    # Servicio principal de IA
├── ai_tutor_service.py   # Tutor inteligente
├── embedding_service.py  # Embeddings
├── rag_service.py        # RAG
├── intelligent_tutor.py  # Tutor basado en reglas+LLM
├── sandbox_service.py    # Sandbox de código
└── exercise_generator_service.py
```

#### Justificación Técnica

Es un **monolito modular**: un solo deployment, una sola base de código, pero con módulos internos claramente delimitados (`ml/`, `analytics/`, `services/`). Cada módulo tiene responsabilidades bien definidas y puede ser teóricamente extraído a un microservicio si fuera necesario. Este patrón es ideal para proyectos que empiezan como monolito pero planean escalar a microservicios.

---

### 6. Event Driven Architecture

| Aspecto | Detalle |
|---------|---------|
| **Estado** | ❌ No implementado (con trazas mínimas de eventos) |
| **Confianza** | Baja (15%) |

#### Evidencias

- **No hay message broker** — no se usa RabbitMQ, Kafka, Redis Streams, ni Pub/Sub.
- **No hay event bus** — los eventos no se publican/consumen de forma estructurada.
- **Fire-and-forget con asyncio** — se usa `asyncio.create_task()` en algunos puntos para logging no bloqueante:
  ```python
  # backend/app/main.py línea 232
  asyncio.create_task(event_repository.log_event("user_login", user.id, ...))
  ```
- **Logging a MongoDB** — los eventos se registran en MongoDB para auditoría, pero nadie los consume en tiempo real.
- **APScheduler** — tareas programadas (cron-like), no dirigidas por eventos.

#### Justificación Técnica

No hay arquitectura dirigida por eventos. Solo hay **registro de eventos** (event sourcing ligero) para auditoría y analítica. No hay productores/consumidores, ni procesamiento asíncrono de eventos de negocio. Los `create_task` son para no bloquear la respuesta HTTP, no para un sistema de eventos.

---

### 7. Clean Architecture

| Aspecto | Detalle |
|---------|---------|
| **Estado** | ⚠️ Parcialmente implementado (como variante de Hexagonal) |
| **Confianza** | Media (60%) |

#### Evidencias

**Cumplimiento de principios**:

| Principio Clean Architecture | ¿Cumple? | Evidencia |
|------------------------------|----------|-----------|
| **Independencia del Framework** | ✅ Sí | FastAPI es solo el point-of-entry. El dominio no importa FastAPI. |
| **Testeable** | ✅ Sí | 28 tests backend, dominio testeable sin infraestructura. |
| **Independencia de la UI** | ✅ Sí | Frontend Next.js separado completamente del backend. |
| **Independencia de la DB** | ✅ Sí | Puertos de repositorio → implementaciones intercambiables. |
| **Regla de Dependencia (hacia adentro)** | ✅ Sí | `domain/` no conoce `infrastructure/`, `application/` depende de puertos. |
| **Casos de uso como entry point** | ✅ Sí | `application/useCases/` son los orquestadores. |
| **DTOs de entrada/salida** | ✅ Sí | `app/schemas/` (Pydantic) como DTOs. |
| **Capa de presentación separada** | ⚠️ Parcial | Rutas definidas en `main.py` mezclan controller + lógica. |

**Incumplimiento parcial**:

- Las rutas en `backend/app/main.py` mezclan la capa de presentación con lógica de negocio (consultas SQL inline, creación de tokens). Esto viola el principio de separación estricta de Clean Architecture.
- No hay una capa de **controllers** pura — los endpoints hacen demasiado trabajo directo.
- Algunas entidades (`user.py`) tienen métodos que exponen datos directamente en lugar de usar DTOs de salida.

#### Justificación Técnica

Clean Architecture comparte principios con Hexagonal (inversión de dependencias, casos de uso centrales). RoboLearn implementa Hexagonal más fielmente que Clean Architecture. La diferencia principal es que Clean Architecture exige 4 capas (Entities → Use Cases → Interface Adapters → Frameworks & Drivers) con DTOs estrictos, mientras que Hexagonal es más flexible con 3 zonas (Domain → Application → Infrastructure). RoboLearn se alinea mejor con Hexagonal.

---

## Tabla Resumen de Arquitecturas

| Arquitectura | Estado | Confianza | ¿Predominante? |
|--------------|--------|-----------|----------------|
| **Arquitectura Hexagonal** | ✅ Implementada | 95% | **SÍ** |
| Arquitectura por Capas | ✅ Presente (subordinada) | 75% | No |
| Clean Architecture | ⚠️ Parcial | 60% | No |
| Modular Monolith | ✅ Presente | 80% | Coexiste |
| MVC | ❌ No implementada | 0% | No |
| Microservicios | ❌ No implementada | 10% | No |
| Event Driven | ❌ No implementada | 15% | No |

---

## Diagrama de Arquitectura (Texto)

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 16)                    │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Páginas    │  │ Componentes  │  │ Server Actions       │  │
│  │ (App Router)│  │ (shadcn/ui)  │  │ (auth.ts)            │  │
│  └─────┬─────┘  └──────┬───────┘  └──────────┬───────────┘  │
│        │               │                     │               │
│        └───────────────┴─────────────────────┘               │
│                         │ HTTP (JWT cookie)                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│               BACKEND (FastAPI - Hexagonal)                  │
│                          │                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CAPA DE PRESENTACIÓN (app/)              │   │
│  │  main.py (routers) + schemas/ + dependencies.py       │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────┴───────────────────────────────┐   │
│  │              CAPA DE APLICACIÓN (application/)        │   │
│  │  ┌──────────────┐  ┌─────────────────────────────┐   │   │
│  │  │ Use Cases    │  │ Services                    │   │   │
│  │  │ (5 casos)    │  │ (IA, Tutor, RAG, Embeddings)│   │   │
│  │  └──────┬───────┘  │ (ML, Analytics, Sandbox)   │   │   │
│  │         │          └─────────────────────────────┘   │   │
│  │         └──────────────────────────┐                  │   │
│  └────────────────────────────────────┼──────────────────┘   │
│                                       │                      │
│  ┌────────────────────────────────────┼──────────────────┐   │
│  │          PUERTOS (domain/ports/)   │                  │   │
│  │  UserRepo  ModuleRepo  Enrollment  TeacherRepo  AI    │   │
│  └────────────────────────────────────┼──────────────────┘   │
│                                       │                      │
│  ┌────────────────────────────────────┼──────────────────┐   │
│  │         ADAPTADORES (infrastructure/)                  │   │
│  │  ┌──────────┐  ┌────────┐  ┌───────┐  ┌──────────┐   │   │
│  │  │PostgreSQL│  │ MongoDB│  │ Redis │  │ Docker   │   │   │
│  │  │(adapters)│  │(adapt.)│  │(cache)│  │(sandbox) │   │   │
│  │  └────┬─────┘  └───┬────┘  └───┬───┘  └──────────┘   │   │
│  └───────┼─────────────┼──────────┼──────────────────────┘   │
└──────────┼─────────────┼──────────┼──────────────────────────┘
           │             │          │
     ┌─────┴─────┐ ┌─────┴──────┐ ┌┴──────┐
     │ PostgreSQL│ │  MongoDB   │ │ Redis │
     │  + vector  │ │  (eventos) │ │(cache)│
     └───────────┘ └────────────┘ └───────┘

┌─────────────────────────────────────────────────────────────┐
│              SERVICIOS SATÉLITE (Docker Compose)             │
│  ┌──────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │  Ollama  │  │   Dialogflow    │  │     OpenAI       │   │
│  │ (local)  │  │ (Google Cloud)  │  │  (fallback)      │   │
│  └──────────┘  └─────────────────┘  └──────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ML Pipeline (independiente, scripts Python)          │   │
│  │  RandomForest, KMeans, IsolationForest               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Conclusión Final

**La arquitectura predominante del proyecto RoboLearn es la Arquitectura Hexagonal (Puertos y Adaptadores), con un 95% de confianza.**

### Justificación de la conclusión

1. **Estructura explícita**: Las carpetas `domain/`, `application/`, `infrastructure/` reflejan directamente los conceptos de Hexagonal: dominio puro, casos de uso de aplicación, y adaptadores concretos.

2. **Puertos e interfaces**: `domain/ports/` contiene 5 interfaces que definen contratos. `infrastructure/adapters/output/` contiene las implementaciones concretas de esos puertos.

3. **Inversión de dependencias**: Los casos de uso (`application/useCases/`) reciben por constructor interfaces del dominio, no implementaciones concretas. El wiring se hace centralizadamente en `app/dependencies.py`.

4. **Aislamiento del dominio**: Las entidades en `domain/entities/` no importan nada de infraestructura, ni de FastAPI, ni de bases de datos. Son Python puro.

5. **Flexibilidad de adaptadores**: PostgreSQL, MongoDB y Redis son intercambiables. Los repositorios tienen múltiples implementaciones para el mismo puerto (por ejemplo, `UserRepositoryImpl` en PostgreSQL, `EventRepository` en MongoDB).

### Patrón secundario

**Modular Monolith** coexiste como patrón organizativo interno. El monolito está dividido en módulos internos (`ml/`, `analytics/`, `services/`) con alta cohesión y bajo acoplamiento, listos para ser extraídos a microservicios si el proyecto escala.

### Recomendaciones

Para fortalecer la arquitectura:
1. **Separar rutas de lógica** — Mover la lógica de negocio que está inline en `main.py` a casos de uso o servicios dedicados.
2. **Centralizar DTOs de salida** — Actualmente algunas entidades serializan datos directamente. Usar DTOs explícitos para todas las respuestas.
3. **Evaluar extracción de módulos** — Si el proyecto crece, considerar mover `ml/` y `analytics/` a microservicios independientes.
4. **Agregar event bus** — Para escenarios asíncronos (notificaciones, actualización de métricas), un message broker ligero (Redis Streams o RabbitMQ) mejoraría la resiliencia.

---

*Fin del reporte de Detección Arquitectónica.*
