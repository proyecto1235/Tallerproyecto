# Reporte de Ingeniería Inversa

**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Rol:** Auditor de Software Senior — Ingeniería Inversa  
**Versión del Reporte:** 1.0

---

## 1. Resumen Ejecutivo

RoboLearn es una **plataforma educativa de programación asistida por inteligencia artificial**, desarrollada con un stack moderno (Next.js 16 + FastAPI + PostgreSQL + MongoDB + Redis + Ollama) y una arquitectura **Hexagonal (Puertos y Adaptadores)** con **Modular Monolith** interno.

El análisis de ingeniería inversa se realizó sobre **90+ archivos backend**, **60+ archivos frontend** y **15 archivos de ML Pipeline**, reconstruyendo la arquitectura completa del sistema sin documentación previa ni acceso al equipo de desarrollo.

### Hallazgos Principales

| Dimensión | Resultado |
|-----------|-----------|
| **Arquitectura** | Hexagonal (95% confianza) con Modular Monolith |
| **Lenguajes** | Python 3.11, TypeScript 5.7, SQL, Shell |
| **Frameworks** | FastAPI 0.109, Next.js 16.2.4, React 19.2.4 |
| **Bases de Datos** | PostgreSQL 16 + pgvector, MongoDB 7, Redis 7 |
| **IA/ML** | Ollama + Qwen2.5-Coder, Dialogflow, OpenAI, scikit-learn |
| **Endpoints** | 144 REST endpoints documentados |
| **Casos de Uso** | 5 formales + 11 implícitos |
| **Hallazgos** | 52 (11 críticos, 16 altos, 15 medios, 10 bajos) |

### Calificación General: 3.3/5

| Atributo | Nota |
|----------|:----:|
| Cohesión | 4/5 |
| Acoplamiento | 3/5 |
| Escalabilidad | 3/5 |
| Mantenibilidad | 4/5 |
| Testabilidad | 4/5 |
| Seguridad | 2/5 |

### Riesgo Más Crítico

**CVE-2024-33663** en `python-jose==3.3.0` (CVSS 9.3): algoritmo de confusión que permite falsificar cualquier JWT. **Compromiso total de autenticación.** Actualización urgente requerida.

---

## 2. Objetivos

1. **Reconstruir la arquitectura completa** del sistema RoboLearn a partir del código fuente.
2. **Identificar todas las tecnologías, frameworks y librerías** utilizadas.
3. **Detectar patrones arquitectónicos** y evaluar su implementación.
4. **Analizar dependencias** internas y externas, incluyendo vulnerabilidades.
5. **Reconstruir el modelo de dominio** (DDD) a partir del código.
6. **Mapear flujos de datos** entre componentes.
7. **Evaluar atributos de calidad**: seguridad, escalabilidad, mantenibilidad, testabilidad.
8. **Generar matriz de hallazgos** con recomendaciones priorizadas.

---

## 3. Alcance

### Incluye

| Componente | Path | Líneas (aprox.) |
|-----------|------|:---------------:|
| Backend API | `backend/` | ~10,000+ |
| Frontend Web | `frontend/` | ~8,000+ |
| ML Pipeline | `ml_pipeline/` | ~1,500+ |
| Infraestructura | `docker-compose.yml`, `Dockerfiles` | ~300+ |
| CI/CD | `.github/workflows/` | ~256+ |
| Tests | `tests/` | ~500+ |
| Scripts BD | `backend/scripts/` | ~2,000+ |
| **Total** | | **~22,000+** |

### Excluye

- `node_modules/`, `__pycache__/`, `.venv/` (directorios generados)
- `package-lock.json` (archivo lock generado)
- `cypress/` (no se analizó por no encontrarse directorio con contenido)
- Archivos binarios, imágenes, fuentes

---

## 4. Metodología

### 4.1 Auditoría

Se realizó un recorrido sistemático de toda la estructura del proyecto utilizando:

- **Exploración de directorios**: identificación de la estructura de carpetas y arquitectura de módulos.
- **Análisis de archivos de configuración**: `package.json`, `requirements.txt`, `docker-compose.yml`, `tsconfig.json`, `next.config.mjs`, `postcss.config.mjs`, `.env.example`.
- **Lectura de código fuente**: análisis de ~22,000+ líneas de código en Python, TypeScript, SQL y Shell.
- **Análisis estático de logs**: identificación de todos los puntos de logging (`logger.info`, `logger.error`, `logger.warning`, `logger.debug`, `print`) en el código fuente.

### 4.2 Instalación

No se ejecutó instalación real. Se reconstruyó el procedimiento de instalación a partir de:

- `docker-compose.yml`: servicios, imágenes, redes, volúmenes, healthchecks.
- `Dockerfile` (backend y frontend): comandos de build, dependencias.
- `.github/workflows/ci.yml`: dependencias instaladas en CI.
- Scripts de inicialización de bases de datos.

### 4.3 Configuración

Se analizaron todos los archivos de configuración del proyecto:

- `backend/config/settings.py`: modelo Pydantic Settings con validación de variables obligatorias.
- `backend/.env.example`: plantilla de 43 variables de entorno documentadas.
- `docker-compose.yml`: 191 líneas de configuración de 6 servicios.
- `frontend/proxy.ts`: middleware de Next.js para verificación JWT.
- `backend/app/logging_config.py`: configuración del logger.
- `backend/app/dependencies.py`: wiring de dependencias (305 líneas).

### 4.4 Ejecución

Se reconstruyó el flujo de ejecución del sistema mediante:

- Análisis del `lifespan` de FastAPI en `main.py` (inicialización, carga de credenciales, init de BD, pool de conexiones).
- Análisis del flujo de middleware HTTP (CORS, auditoría, headers de seguridad).
- Análisis del flujo de request → response (autenticación, validación, casos de uso, repositorios, respuesta).
- Análisis del flujo de inicialización de Docker Compose (healthchecks, scripts de BD, pull de modelos Ollama).

### 4.5 Ingeniería Inversa

Se aplicaron las siguientes técnicas:

- **Lectura de estructura de directorios**: mapeo de la arquitectura de capas (domain, application, infrastructure, app, config).
- **Análisis de imports**: trazado del grafo de dependencias entre módulos.
- **Reconstrucción de entidades**: identificación de entidades de dominio, value objects, enums y agregados a partir de clases Python y schemas SQL.
- **Reconstrucción de puertos e interfaces**: identificación de 5 puertos en `domain/ports/` y sus implementaciones en `infrastructure/adapters/`.
- **Mapeo de endpoints**: catalogación de 144 endpoints REST desde los decoradores `@app.get/post/put/delete` en `main.py`.
- **Trazado de flujos de datos**: identificación de flujos E2E (ejercicio, chatbot, ML pipeline, inicialización).
- **Análisis de vulnerabilidades**: búsqueda de CVEs en dependencias usando datos públicos.
- **Detección de antipatrones**: identificación de deuda técnica (exec(), main.py monolítico, fire-and-forget).

---

## 5. Inventario Tecnológico

### 5.1 Lenguajes de Programación

| Lenguaje | Versión | Ubicación | Frameworks Asociados |
|----------|---------|-----------|---------------------|
| Python | 3.11 | `backend/`, `ml_pipeline/` | FastAPI, Pydantic, scikit-learn |
| TypeScript | 5.7.3 | `frontend/` | Next.js, React, Tailwind |
| JavaScript | ES6+ | `frontend/` | (transpilado desde TS) |
| SQL (PL/pgSQL) | PostgreSQL 16 | `backend/scripts/` | psycopg2, pgvector |
| Shell | bash/sh | `.github/`, `Dockerfiles` | CI/CD, entrypoints |

### 5.2 Frameworks y Librerías Principales

| Categoría | Tecnología | Versión | Propósito |
|-----------|-----------|---------|-----------|
| Backend Framework | FastAPI | 0.109.0 | REST API |
| Backend Server | Uvicorn | 0.27.0 | ASGI server |
| Frontend Framework | Next.js | 16.2.4 | SSR + App Router |
| UI Library | React | 19.2.4 | Interfaz de usuario |
| CSS Framework | Tailwind CSS | 4.2.0 | Estilos utility-first |
| UI Components | shadcn/ui (Radix UI) | — | Componentes accesibles |
| Validación | Pydantic | 2.5.0 | Schemas + Settings |
| Autenticación | python-jose / jose | 3.3.0 / 6.2.2 | JWT |
| ML | scikit-learn | 1.8.0 | Modelos predictivos |
| LLM Local | Ollama + Qwen2.5-Coder | 1.5B | Tutor IA, RAG |
| Chatbot | Dialogflow CX (Google) | — | Chatbot conversacional |
| LLM Cloud | OpenAI (GPT-3.5-turbo) | — | Fallback de IA |

### 5.3 Bases de Datos

| Base de Datos | Versión | Propósito | Driver |
|---------------|---------|-----------|--------|
| PostgreSQL | 16 + pgvector | Datos transaccionales + embeddings RAG | psycopg2-binary 2.9.9 |
| MongoDB | 7 | Eventos, analítica conductual, predicciones | pymongo 4.6.0 |
| Redis | 7 Alpine | Caché IA, rate limiting, token blacklist | redis[hiredis] 5.1.0 |

### 5.4 Servicios Externos

| Servicio | Propósito | Autenticación | Modo de Falla |
|----------|-----------|---------------|---------------|
| Dialogflow CX (Google) | Chatbot primario | JSON credentials (GCP) | Fallback a Ollama |
| OpenAI API | Fallback IA | API Key | Fallback a IntelligentTutor |
| Docker Hub | Registro de imágenes CI/CD | Usuario + Password | Deploy bloqueado |
| Vercel Analytics | Analytics del frontend | Automático | Sin impacto |

### 5.5 Infraestructura DevOps

| Herramienta | Propósito |
|-------------|-----------|
| Docker Compose | Orquestación de 6 servicios |
| Docker Engine | Contenedores |
| GitHub Actions | CI/CD automatizado |
| Docker Buildx | Build multi-plataforma |
| Codecov | Reporte de cobertura |
| k6 | Pruebas de carga |
| flake8, mypy, isort | Linting Python |
| ESLint | Linting TypeScript |
| pytest + pytest-cov | Testing Python |
| vitest | Testing frontend |

---

## 6. Arquitectura Detectada

### 6.1 Patrón Predominante: Arquitectura Hexagonal (95% confianza)

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 16)                    │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Páginas    │  │ Componentes  │  │ Server Actions       │  │
│  │ (App Router)│  │ (shadcn/ui)  │  │ (auth.ts)            │  │
│  └────────────┘  └──────────────┘  └──────────────────────┘  │
│                         │ HTTP (JWT cookie)                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│               BACKEND (FastAPI - Hexagonal)                  │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │  PRESENTACIÓN: main.py (routers) + schemas/ + deps     │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │  APLICACIÓN: useCases/ (5) + services/ (9) + ML/     │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │  PUERTOS: domain/ports/ (5 interfaces)                │  │
│  └───────────────────────┬───────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │  ADAPTADORES: Postgres, Mongo, Redis, Docker           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Patrón Secundario: Modular Monolith (80% confianza)

El backend es un solo proceso FastAPI pero organizado en módulos internos extraíbles:

| Módulo | Path | Archivos | ¿Extraíble? |
|--------|------|----------|:-----------:|
| ML Predictivo | `application/services/ml/` | 12 | ✅ Sí |
| Analítica | `application/services/analytics/` | 4 | ✅ Sí |
| RAG + Embeddings | `application/services/rag_service.py` | 2 | ✅ Sí |
| Sandbox | `application/services/sandbox_service.py` | 2 | ✅ Sí |
| Tutor IA | `application/services/intelligent_tutor.py` | 3 | ✅ Sí |

### 6.3 Patrones Evaluados y Descartados

| Patrón | Estado | Razón |
|--------|--------|-------|
| MVC | ❌ No implementado | FastAPI usa routers, Next.js usa App Router |
| Microservicios | ❌ No implementado | Un solo backend, BD compartida, sin API Gateway |
| Event Driven | ❌ No implementado | Sin message broker, `create_task` no es event bus |
| Clean Architecture | ⚠️ Parcial (60%) | Comparte principios con Hexagonal pero menos estricta |

---

## 7. Dependencias

### 7.1 Resumen General

| Componente | Archivo | Prod | Dev | Total |
|-----------|---------|:---:|:---:|:----:|
| Backend | `backend/requirements.txt` | 19 | 0* | 19 |
| ML Pipeline | `ml_pipeline/requirements.txt` | 7 | 0 | 7 |
| Frontend | `frontend/package.json` | 42 | 9 | 51 |
| **Total** | | **68** | **9** | **77** |

*\* El backend no tiene separación dev/prod. pytest, flake8, mypy se instalan solo en CI.*

### 7.2 Dependencias Críticas

| Dependencia | Versión | Rol | Riesgo si Fallo |
|-------------|---------|-----|-----------------|
| FastAPI | 0.109.0 | Framework base del backend | API no funciona |
| Next.js | 16.2.4 | Framework base del frontend | UI no funciona |
| Pydantic | 2.5.0 | Validación de datos | Sin validación ni schemas |
| psycopg2-binary | 2.9.9 | Conexión PostgreSQL | Sin datos transaccionales |
| pymongo | 4.6.0 | Conexión MongoDB | Sin eventos ni analítica |
| scikit-learn | 1.8.0 | Modelos ML predictivos | Sin predicciones |
| bcrypt | 3.2.0 | Hashing de contraseñas | Sin autenticación segura |
| python-jose | 3.3.0 | JWT | **🔴 Vulnerabilidad CRÍTICA** |

### 7.3 Vulnerabilidades Detectadas

| CVE | Dependencia | Versión | CVSS | Tipo | Estado |
|-----|-------------|---------|:----:|------|--------|
| CVE-2024-33663 | python-jose | 3.3.0 | **9.3** | Algorithm confusion | 🔴 Sin parche |
| CVE-2024-33664 | python-jose | 3.3.0 | 5.3 | JWT Bomb (DoS) | 🔴 Sin parche |
| CVE-2026-44581 | next | 16.2.4 | — | XSS almacenado | 🟡 Sin parche |
| CVE-2026-44578 | next | 16.2.4 | — | SSRF via WebSocket | 🟡 Sin parche |
| CVE-2026-23869 | next | 16.2.4 | 7.5 | DoS Server Components | ✅ Parchado en 16.2.3 |

---

## 8. Configuración

### 8.1 Variables de Entorno

Se identificaron **43 variables de entorno** en 5 categorías:

| Categoría | Variables | Secretos | Obligatorias |
|-----------|:--------:|:--------:|:------------:|
| App | 5 | 0 | 0 |
| Seguridad/JWT | 5 | 3 | 1 |
| Bases de Datos | 11 | 3 | 8 |
| IA/ML | 8 | 3 | 0 |
| Frontend/Docker | 14 | 1 | 3 |
| **Total** | **43** | **14** | **14** |

### 8.2 Archivos de Configuración

| Archivo | Path | Rol |
|---------|------|-----|
| `.env.example` | `./` | Plantilla de 84 líneas |
| `settings.py` | `backend/config/` | Pydantic Settings con validación |
| `database_init.py` | `backend/config/` | Inicialización automática de BD |
| `docker-compose.yml` | `./` | Orquestación de 6 servicios (191 líneas) |
| `next.config.mjs` | `frontend/` | Configuración Next.js |
| `tsconfig.json` | `frontend/` | TypeScript estricto |
| `logging_config.py` | `backend/app/` | Logger a stdout con nivel INFO |
| `Dockerfile` | `backend/`, `frontend/` | Build de imágenes |
| `ci.yml` | `.github/workflows/` | Pipeline CI (206 líneas) |
| `deploy.yml` | `.github/workflows/` | Pipeline CD (50 líneas) |

### 8.3 Configuración de Redes Docker

```
frontend_net (bridge, público)
  ├── frontend:3000
  └── backend:8000

internal_net (bridge, INTERNO — aislado)
  ├── backend
  ├── postgres:5432
  ├── mongo:27017
  └── redis:6379

ai_net (bridge, semi-público)
  ├── backend
  └── ollama:11434
```

---

## 9. Ejecución

### 9.1 Flujo de Inicialización del Sistema

```
docker compose up
  │
  ├── postgres ─── docker-entrypoint-initdb.d/
  │                 ├── 01-init.sql (22 tablas, 8 stored procedures)
  │                 ├── 02-seed.sql (datos semilla)
  │                 ├── 03-massive.sql (datos masivos - desarrollo)
  │                 └── 05-pgvector.sql (extensión vector)
  │
  ├── mongo ─────── init-db.js (13 colecciones)
  │
  ├── redis ─────── redis-server --appendonly yes
  │
  ├── ollama ────── ollama serve + pull qwen2.5-coder:1.5b (~2.5GB)
  │
  └── backend ───── lifespan FastAPI
                    ├── Cargar Google Credentials (si existe)
                    ├── initialize_database() (crear DB, ejecutar scripts)
                    ├── PostgresConnection.init_pool() (pool 5-50)
                    └── Import analytics_router (lazy: numpy)
```

### 9.2 Flujo de Request → Response

```
Cliente Browser
  │
  ├── Next.js Middleware (proxy.ts)
  │     └── Verifica JWT en cookie "auth-token"
  │
  ├── Frontend → Backend (HTTP fetch)
  │     ├── Cookie: auth-token
  │     └── Headers: Content-Type, Accept
  │
  ├── FastAPI Middleware
  │     ├── CORS
  │     ├── Audit logging (rutas sensibles)
  │     └── Security Headers (CSP, HSTS, XFO, XCTO)
  │
  ├── Dependencies (dependencies.py)
  │     ├── verify_token → decode JWT → TokenData
  │     ├── verify_teacher → role check
  │     └── verify_admin → role check
  │
  ├── Route Handler (en main.py)
  │     ├── Use Case o lógica inline
  │     ├── Repository (interfaz → adapter)
  │     └── Database (PostgreSQL / MongoDB / Redis)
  │
  └── Response JSON → Client
        └── Error: AppException / HTTPException / 500
```

### 9.3 Flujo de Chatbot Omnicanal (4 Niveles de Fallback)

```
POST /api/chatbot
  │
  ├─ ¿Dialogflow configurado? → Sí → Dialogflow CX (Google)
  │                                   └─ Error → continuar
  │
  ├─ Ollama (local, Qwen2.5-Coder)
  │     └─ No disponible → continuar
  │
  ├─ ¿OPENAI_API_KEY? → Sí → OpenAI GPT-3.5-turbo
  │                       └─ Error → continuar
  │
  └─ IntelligentTutor (basado en reglas)
        └─ Detecta intención: saludo / pista / ejemplo / error
```

### 9.4 Flujo de Evaluación de Ejercicio

```
POST /api/exercises/submit {code, exercise_id}
  │
  ├── Buscar ejercicio (global o de clase)
  ├── Validar si ya fue aprobado
  ├── SandboxService.execute_and_compare()
  │     ├── AST parse validation
  │     ├── Blacklist de patrones peligrosos (bypasseable)
  │     ├── Docker container (64MB, 0.5CPU, sin red)
  │     └── Comparar stdout con solution_output
  ├── INSERT exercise_attempt (ON CONFLICT con retry)
  ├── if passed:
  │     ├── UPDATE progress
  │     ├── Otorgar puntos
  │     ├── Verificar logros
  │     └── Log evento en MongoDB (fire-and-forget)
  └── Response {passed, score, output, error}
```

---

## 10. Reconstrucción Arquitectónica

### 10.1 Diagrama de Capas (Backend)

```
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA             │ RESPONSABILIDAD               │ TECNOLOGÍA       │
├─────────────────────────────────────────────────────────────────────┤
│ Presentación     │ 144 endpoints REST,            │ FastAPI, Pydantic│
│ (app/)           │ middleware, schemas, DI        │ Uvicorn          │
├─────────────────────────────────────────────────────────────────────┤
│ Aplicación       │ 5 casos de uso,               │ Python puro      │
│ (application/)   │ 9 servicios (IA, ML, Tutor)   │ scikit-learn     │
├─────────────────────────────────────────────────────────────────────┤
│ Dominio          │ 7 entidades, 5 puertos,       │ Python puro      │
│ (domain/)        │ value objects, enums          │ (sin imports)    │
├─────────────────────────────────────────────────────────────────────┤
│ Infraestructura  │ 4 adaptadores Postgres,       │ psycopg2, PyMongo│
│ (infrastructure/)| 2 Mongo, 2 Redis, 1 Docker   │ redis, docker SDK│
├─────────────────────────────────────────────────────────────────────┤
│ Config           │ Settings, DB init             │ Pydantic Settings│
│ (config/)        │                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2 Patrón de Inversión de Dependencias

```
application/useCases/register_user.py
  │
  ├── depende de: domain/ports/user_repository.py (interfaz)
  │     ↑
  │     │ implementa
  │     │
  └── infrastructure/adapters/output/postgres/user_repository_impl.py

El caso de uso NO conoce la implementación concreta.
La inyección se hace en app/dependencies.py.

Beneficios:
  ✅ Repositorio intercambiable (PostgreSQL ↔ mock ↔ otra DB)
  ✅ Testable sin infraestructura real
  ✅ Dominio aislado de cambios externos
```

### 10.3 Catálogo de Componentes

| ID | Componente | Tipo | Capa | Archivos |
|:--:|-----------|------|------|----------|
| C01 | User | Entidad | Domain | `domain/entities/user.py` |
| C02 | Module | Entidad | Domain | `domain/entities/module.py` |
| C03 | Exercise | Entidad | Domain | `domain/entities/exercise.py` |
| C04 | Challenge | Entidad | Domain | `domain/entities/challenge.py` |
| C05 | Enrollment | Entidad | Domain | `domain/entities/enrollment.py` |
| C06 | Achievement | Entidad | Domain | `domain/entities/achievement.py` |
| C07 | Alert | Entidad | Domain | `domain/entities/alert.py` |
| C08 | Progress | Value Object | Domain | `domain/valueObjects/progress.py` |
| C09 | UserRepository | Puerto | Domain | `domain/ports/user_repository.py` |
| C10 | ModuleRepository | Puerto | Domain | `domain/ports/module_repository.py` |
| C11 | EnrollmentRepository | Puerto | Domain | `domain/ports/enrollment_repository.py` |
| C12 | TeacherRepository | Puerto | Domain | `domain/ports/teacher_repository.py` |
| C13 | AIService | Puerto | Domain | `domain/ports/ai_service.py` |
| C14 | RegisterUserUseCase | Caso de Uso | Application | `application/useCases/register_user.py` |
| C15 | EnrollStudentUseCase | Caso de Uso | Application | `application/useCases/enroll_student.py` |
| C16 | GetRecommendationsUseCase | Caso de Uso | Application | `application/useCases/get_recommendations.py` |
| C17 | TeacherDashboardUseCase | Caso de Uso | Application | `application/useCases/teacher_dashboard.py` |
| C18 | GenerateAIAlertsUseCase | Caso de Uso | Application | `application/useCases/generate_ai_alerts.py` |
| C19 | IntelligentTutor | Servicio | Application | `application/services/intelligent_tutor.py` |
| C20 | LLMService | Servicio | Application | `application/services/llm_service.py` |
| C21 | SandboxService | Servicio | Application | `application/services/sandbox_service.py` |
| C22 | RAGService | Servicio | Application | `application/services/rag_service.py` |
| C23 | MLOrchestrator | Servicio | Application | `application/services/ml/orchestrator.py` |
| C24 | UserRepositoryImpl | Adaptador | Infrastructure | `infrastructure/.../user_repository_impl.py` |
| C25 | ModuleRepositoryImpl | Adaptador | Infrastructure | `infrastructure/.../module_repository_impl.py` |
| C26 | EventRepository | Adaptador | Infrastructure | `infrastructure/.../event_repository_impl.py` |
| C27 | BehavioralRepository | Adaptador | Infrastructure | `infrastructure/.../behavioral_repository.py` |
| C28 | AICache | Adaptador | Infrastructure | `infrastructure/.../redis/cache.py` |
| C29 | RateLimiter | Adaptador | Infrastructure | `infrastructure/.../redis/rate_limiter.py` |
| C30 | CodeExecutor | Adaptador | Infrastructure | `infrastructure/.../docker/code_executor.py` |

### 10.4 Entidades Faltantes (Deuda Técnica)

| Entidad | Estado | Ubicación Actual | Impacto |
|---------|--------|-----------------|---------|
| **Lesson** | ❌ No existe | Manejo como dict en SQL + main.py | Modelo de dominio incompleto |
| **Class** (aula virtual) | ❌ No existe | Manejo como dict en SQL + main.py | Modelo de dominio incompleto |
| **ClassModule** | ❌ No existe | Tabla SQL sin entidad | Sin representación en dominio |
| **ClassExercise** | ❌ No existe | Tabla SQL sin entidad | Sin representación en dominio |
| **ExerciseAttempt** | ❌ No existe | Consulta SQL directa | Sin seguimiento formal |
| **ChallengeAttempt** | ❌ No existe | Consulta SQL directa | Sin seguimiento formal |

---

## 11. Modelo de Dominio

### 11.1 Mapa de Subdominios

| Subdominio | Tipo | Descripción |
|-----------|------|-------------|
| Catálogo de Contenido | **Core** | Módulos, lecciones, ejercicios, challenges |
| Gestión de Aprendizaje | **Core** | Inscripciones, progreso, logros |
| Analítica Predictiva | **Core** | ML para engagement, rendimiento, deserción, frustración |
| Tutoría Inteligente | **Core** | Asistencia IA (chatbot, pistas, explicaciones) |
| Aulas Virtuales | Soporte | Clases con contenido personalizado por teacher |
| Identidad y Acceso | Soporte | Auth, roles, autorización |
| Eventos y Métricas | Genérico | Tracking de comportamiento, snapshots |
| Ejecución de Código | Soporte | Sandbox seguro para código Python |

### 11.2 Agregados Identificados

| Agregado | Root | Entidades Internas |
|----------|------|-------------------|
| **Module** | Module | Lesson, Exercise, Enrollment (ref) |
| **User** | User | UserAchievement, Enrollment, ExerciseAttempt |
| **Class** | Class | ClassModule, ClassExercise, ClassEnrollment |
| **Challenge** | Challenge | ChallengeAttempt |
| **Achievement** | Achievement | UserAchievement |

### 11.3 Reglas de Negocio (20 identificadas)

| ID | Regla | Tipo |
|:--:|-------|------|
| BR1 | Email único en el sistema | Invariante |
| BR2 | Contraseña debe tener ≥6 caracteres | Validación |
| BR3 | Usuario inactivo no puede iniciar sesión | Invariante |
| BR4 | Solo admins pueden cambiar roles | Autorización |
| BR5 | Teacher no puede editar módulos de otros | Autorización |
| BR6 | Eliminación de módulo requiere aprobación admin | Proceso |
| BR7 | Módulo debe estar APPROVED + is_published para ser visible | Invariante |
| BR8 | Estudiante no puede inscribirse dos veces al mismo módulo | Invariante |
| BR9 | Módulos no publicados no son inscribibles | Validación |
| BR10 | Módulo se completa cuando todas las lecciones están completadas | Invariante |
| BR11 | 3 intentos fallidos → se muestra la solución | Presentación |
| BR12 | Dificultad debe estar entre 1 y 5 | Validación |
| BR13 | Progreso = ejercicios completados / totales × 100 | Cálculo |
| BR14 | Logro solo puede otorgarse una vez por estudiante | Invariante |
| BR15 | Alerta DIFFICULTY requiere ≥3 estudiantes y ≥40% bajo progreso | Generación |
| BR16 | SLOW_LEARNER requiere 7+ días y velocidad <30% del promedio | Generación |
| BR17 | FAST_LEARNER requiere velocidad >200% y progreso >50% | Generación |
| BR18 | Código sandbox no debe contener patrones peligrosos | Seguridad |
| BR19 | Sandbox Docker: 64MB, 0.5 CPU, sin red, solo lectura | Seguridad |
| BR20 | JWT expira después de ACCESS_TOKEN_EXPIRE_MINUTES | Seguridad |

---

## 12. APIs e Integraciones

### 12.1 APIs Expuestas (144 Endpoints)

| Categoría | Endpoints | Auth |
|-----------|:---------:|:----:|
| Health | 2 | ❌ Público |
| Autenticación | 3 | 2 ❌, 1 ✅ |
| Usuarios | 5 | 2 ✅, 3 ❌ |
| AI/ML Recomendaciones | 3 | ✅ |
| Analítica Predictiva | 6 | ✅ Teacher |
| Tutor Inteligente | 5 | ✅ Opcional |
| Chatbot | 3 | 1 ❌, 2 ✅ |
| Ejecución de Código | 1 | ✅ |
| Ejercicios | 4 | ✅ |
| Módulos | 18 | ✅ + Teacher |
| Lecciones | 1 | ✅ |
| Logros | 2 | ✅ |
| Eventos/Métricas | 2 | ✅ |
| Teacher Dashboard | 7 | ✅ Teacher |
| Admin | 15 | ✅ Admin |
| Dashboards | 2 | ✅ Student/Admin |
| Challenges | 7 | ✅ Teacher/Student |
| Clases | 25 | ✅ Teacher/Student |
| AI RAG/Tutor/Ejercicios | 8 | ✅ Teacher/Admin |
| Analytics Router | 6 | ✅ Teacher |
| Analytics Service | 6 | ✅ Teacher |
| **Total** | **144** | |

### 12.2 APIs Externas Consumidas

| API Externa | Propósito | Protocolo | Fallback |
|-------------|-----------|-----------|----------|
| Dialogflow CX | Chatbot primario | gRPC/HTTPS | Ollama |
| Ollama (local) | LLM local | HTTP REST | OpenAI |
| OpenAI API | LLM cloud (fallback) | HTTPS | IntelligentTutor |
| Docker Engine | Sandbox código | Docker Socket | Sin fallback |
| PostgreSQL | Base de datos principal | SQL/TCP | App no inicia |
| MongoDB | Base de datos analítica | MongoDB Wire | Degradación |
| Redis | Caché + rate limit | Redis Protocol | Degradación |

### 12.3 Integraciones Internas

| Componentes | Protocolo | Patrón | Frecuencia |
|-------------|-----------|--------|------------|
| Frontend ↔ Backend | HTTP REST | Síncrono (fetch) | Por request |
| Backend ↔ PostgreSQL | SQL (psycopg2) | Síncrono (pool) | Por request |
| Backend ↔ MongoDB | MongoDB Wire (pymongo) | Síncrono (fire-and-forget) | Por evento |
| Backend ↔ Redis | Redis Protocol (redis.asyncio) | Asíncrono | Por request |
| Backend ↔ Ollama | HTTP REST (httpx) | Síncrono | Por request IA |
| Backend ↔ Docker | Docker SDK (socket) | Síncrono | Por ejecución de código |

---

## 13. Hallazgos

### 13.1 Matriz Completa (52 Hallazgos)

#### 🔴 Críticos (11)

| ID | Hallazgo | Componente | Impacto |
|:--:|----------|------------|---------|
| H-001 | CVE-2024-33663 python-jose 3.3.0 (CVSS 9.3) | `requirements.txt` | Falsificación total de JWT |
| H-002 | Sandbox exec() con blacklist bypasseable | `sandbox_service.py` | RCE potencial |
| H-003 | JWT_SECRET compartido frontend/backend | `docker-compose.yml:167` | Compromiso de autenticación |
| H-004 | Contraseñas por defecto en docker-compose | `docker-compose.yml` | Acceso no autorizado a BD |
| H-005 | Init BD sin validación de scripts requeridos | `database_init.py` | App arranca sin esquema |
| H-006 | SQL Injection en database_init.py | `database_init.py:111` | Inyección SQL potencial |
| H-007 | Fire-and-forget sin manejo de errores | `main.py:232` | Datos de auditoría perdidos |
| H-008 | Sin TLS/HTTPS en ningún componente | `docker-compose.yml` | Tráfico en texto plano |
| H-009 | Token blacklist depende completamente de Redis | `dependencies.py:143-153` | Revocación no funciona sin Redis |
| H-010 | Rate limiting desactivado si Redis no disponible | `rate_limiter.py:19-22` | Sin protección DoS |
| H-011 | Validación de algoritmo JWT débil | `dependencies.py:95-108` | Algorithm confusion |

#### 🟡 Altos (16)

| ID | Hallazgo | Componente | Impacto |
|:--:|----------|------------|---------|
| H-012 | CVE-2026-44581 Next.js 16.2.4 | `package.json` | XSS almacenado |
| H-013 | main.py 4082 líneas monolítico | `main.py` | Mantenibilidad crítica |
| H-014 | Sin lock file Python | `requirements.txt` | Supply chain |
| H-015 | Lazy import numpy/scikit-learn frágil | `main.py:68` | Degradación silenciosa |
| H-016 | Conexiones BD sin validación al iniciar | `database_init.py:65` | App arranca con BD corrupta |
| H-017 | BehavioralRepository falla silenciosamente | `behavioral_repository.py:42-46` | Datos conductuales perdidos |
| H-018 | AICache/RateLimiter degradación sin notificar | `cache.py:19-23` | Operador no sabe |
| H-019 | Modelos ML y dataset no existen | `ml_pipeline/models/` | Analítica predictiva rota |
| H-020 | ON CONFLICT sin unique constraint | `main.py:1265` | Duplicados en BD |
| H-021 | k6 test endpoint incorrecto | `k6-load-test.js:100` | Pruebas de carga inválidas |
| H-022 | Sin ORM/ODM — SQL crudo y PyMongo directo | Todo el backend | Riesgo de errores |
| H-023 | Timeout 3s para agregaciones MongoDB | `main.py:593` | Dashboards parciales |
| H-024 | Sin validación de CORS_ORIGINS | `settings.py:56-63` | Exfiltración de datos |
| H-025 | Contraseña truncada a 72 caracteres | `main.py:205` | Seguridad reducida |
| H-026 | Sin separación dev/prod deps backend | CI/CD | Dependencias de test en prod |

#### 🟢 Medios (15)

| ID | Hallazgo | Componente | Impacto |
|:--:|----------|------------|---------|
| H-027 | Lesson sin entidad formal | `domain/entities/` | Modelo de dominio incompleto |
| H-028 | Class sin entidad formal | `domain/entities/` | Modelo de dominio incompleto |
| H-029 | Variable NODE_ENV sin uso real | `settings.py:24` | Complejidad innecesaria |
| H-030 | test_debug.txt residual | `backend/app/` | Artefacto en producción |
| H-031 | Sin healthcheck frontend Docker | `docker-compose.yml` | Frontend sin monitoreo |
| H-032 | bcrypt 3.2.0 obsoleto | `requirements.txt` | Mejoras de seguridad perdidas |
| H-033 | APScheduler sin persistencia | `scheduler_service.py` | Snapshots perdidos |
| H-034 | EventRepository sin garantía de entrega | `event_repository_impl.py` | Auditoría con lagunas |
| H-035 | Sin reintentos en servicios externos | `llm_service.py:50-55` | Fallos transitorios no recuperados |
| H-036 | Logging DEBUG no visible | `logging_config.py:8` | Depuración difícil |
| H-037 | Sin tests de integración | `tests/` | Flujo completo no validado |
| H-038 | ML Pipeline con datos sintéticos | `ml_pipeline/` | Modelos no validados con datos reales |
| H-039 | Sin monitoreo estructurado | `logging_config.py` | Sin observabilidad |
| H-040 | docker SDK 7.1.0 desactualizado | `requirements.txt` | Bugs no parcheados |
| H-041 | Google Credentials montado como volumen | `docker-compose.yml:143` | Exposición de credenciales GCP |

#### 🔵 Bajos (10)

| ID | Hallazgo | Componente | Impacto |
|:--:|----------|------------|---------|
| H-042 | Red interna sin cifrar | `docker-compose.yml:186-188` | Tráfico plano |
| H-043 | bcrypt error expone hash en log | `main.py:207` | Información sensible en logs |
| H-044 | Pydantic 2.5.0 desactualizado | `requirements.txt` | Mejoras no disponibles |
| H-045 | numpy 1.26.3 sin migrar a 2.x | `requirements.txt` | Deuda técnica |
| H-046 | CORS permite localhost en producción | `docker-compose.yml:131` | Riesgo bajo |
| H-047 | python-multipart 0.0.6 desactualizado | `requirements.txt` | Sin CVEs conocidos |
| H-048 | Sin feature flags | Todo el proyecto | Deploys riesgosos |
| H-049 | Puertos BD expuestos al host | `docker-compose.yml:13` | Acceso local a BD |
| H-050 | Sin documentación técnica formal | Todo el proyecto | Onboarding difícil |
| H-051 | Sin pruebas de carga para IA | `tests/load/` | Rendimiento IA desconocido |
| H-052 | httpx para streaming no óptimo | `llm_service.py:4` | Rendimiento subóptimo en futuro |

---

## 14. Riesgos

### 14.1 Matriz de Riesgos

| ID | Riesgo | Probabilidad | Impacto | Severidad | Mitigación |
|:--:|--------|:-----------:|:-------:|:---------:|------------|
| R-01 | **python-jose CVE-2024-33663 explotado** | Alta | Crítico | 🔴 | Actualizar a ≥3.4.0 urgente |
| R-02 | **exec() sandbox bypasseado (RCE)** | Media | Crítico | 🔴 | Usar siempre contenedor Docker |
| R-03 | **JWT_SECRET filtrado por frontend** | Baja | Crítico | 🟡 | Migrar a RS256 |
| R-04 | **PostgreSQL caído — app no funciona** | Baja | Crítico | 🟡 | Réplicas, failover automático |
| R-05 | **MongoDB caído — datos perdidos** | Media | Alto | 🟡 | Buffer local, replica set |
| R-06 | **Redis caído — sin rate limit, sin blacklist** | Media | Alto | 🟡 | Fallback en memoria |
| R-07 | **Next.js CVE-2026-44581 explotado** | Media | Alto | 🟡 | Actualizar a ≥16.2.5 |
| R-08 | **Modelos ML no entrenados en producción** | Alta | Medio | 🟢 | Generar en build de Docker |
| R-09 | **Ollama fuera de memoria (4GB)** | Media | Medio | 🟢 | Monitoreo, límites ajustables |
| R-10 | **Docker daemon caído — sandbox no funciona** | Media | Alto | 🟡 | Healthcheck, alerta |
| R-11 | **Fire-and-forget pierde eventos de auditoría** | Alta | Medio | 🟢 | Wrapper con retry + persistencia |
| R-12 | **Timeout agregaciones — dashboards vacíos** | Alta | Medio | 🟢 | Aumentar timeout, cachear resultados |
| R-13 | **Sin lock file — supply chain attack** | Baja | Alto | 🟡 | Generar requirements-lock.txt |
| R-14 | **Inconsistencia entre entornos sin lock file** | Alta | Medio | 🟢 | Lock file + hashes |
| R-15 | **Fuga de credenciales GCP por commit** | Baja | Alto | 🟡 | Gancho pre-commit, .gitignore |

### 14.2 Riesgo General del Proyecto

| Factor | Evaluación |
|--------|-----------|
| **Seguridad** | 🔴 ALTO — 11 hallazgos críticos, 1 CVE CVSS 9.3 |
| **Estabilidad** | 🟡 MEDIO — múltiples modos de degradación silenciosa |
| **Mantenibilidad** | 🟢 BUENO — arquitectura hexagonal, pero main.py duele |
| **Escalabilidad** | 🟡 MEDIO — PostgreSQL cuello de botella, Ollama no escala |
| **Madurez** | 🟢 BUENO — CI/CD completo, testing, estructura profesional |

---

## 15. Recomendaciones

### 15.1 Urgentes (Semanas 1-2)

| # | Recomendación | Hallazgos Relacionados | Esfuerzo |
|---|---------------|:----------------------:|:--------:|
| 1 | **Actualizar python-jose** a ≥3.4.0 o migrar a PyJWT | H-001 | 2-4 horas |
| 2 | **Reemplazar exec() por CodeExecutor Docker** — eliminar sandbox_service.py | H-002 | 1-2 días |
| 3 | **Separar JWT_SECRET** — migrar a RS256 con claves asimétricas | H-003, H-011 | 1-2 días |
| 4 | **Eliminar contraseñas por defecto** — fallar si .env no existe | H-004 | 2-4 horas |
| 5 | **Agregar TLS/HTTPS** — nginx/Caddy + Let's Encrypt | H-008 | 2-3 días |

### 15.2 Corto Plazo (Semanas 2-4)

| # | Recomendación | Hallazgos Relacionados | Esfuerzo |
|---|---------------|:----------------------:|:--------:|
| 6 | **Refactorizar main.py** en routers separados por dominio | H-013 | 3-5 días |
| 7 | **Actualizar Next.js** a ≥16.2.5 | H-012 | 2-4 horas |
| 8 | **Agregar lock file Python** con hashes | H-014 | 2-4 horas |
| 9 | **Separar dependencias dev/prod** del backend | H-026 | 1-2 horas |
| 10 | **Agregar fallback en memoria** para token blacklist y rate limiting | H-009, H-010 | 1-2 días |
| 11 | **Validar CORS_ORIGINS** contra lista blanca en producción | H-024 | 2-4 horas |
| 12 | **Corregir k6 test endpoint** y agregar más escenarios | H-021 | 4-6 horas |

### 15.3 Mediano Plazo (Meses 1-2)

| # | Recomendación | Hallazgos Relacionados | Esfuerzo |
|---|---------------|:----------------------:|:--------:|
| 13 | **Formalizar Lesson y Class** como entidades de dominio | H-027, H-028 | 2-3 días |
| 14 | **Agregar ORM/ODM** (SQLAlchemy Core + Alembic) | H-022 | 5-10 días |
| 15 | **Configurar réplicas de lectura PostgreSQL** | R-04 | 3-5 días |
| 16 | **Agregar cache de API** (Redis) para endpoints GET frecuentes | R-12 | 2-3 días |
| 17 | **Implementar wrapper para fire-and-forget** con logging y retry | H-007, H-034 | 1 día |
| 18 | **Agregar healthcheck detallado** (`/api/health/detailed`) | H-015, H-016, H-017 | 1-2 días |
| 19 | **Agregar tests de integración** con TestContainers | H-037 | 3-5 días |
| 20 | **Persistir scheduler APScheduler** en PostgreSQL | H-033 | 1 día |

### 15.4 Largo Plazo (Trimestre)

| # | Recomendación | Hallazgos Relacionados | Esfuerzo |
|---|---------------|:----------------------:|:--------:|
| 21 | **Migrar a microservicios** — extraer ml/ y analytics/ | — | 1-2 meses |
| 22 | **Agregar event bus** (Redis Streams / RabbitMQ) | H-007 | 1-2 semanas |
| 23 | **Implementar monitoreo y observabilidad** (Prometheus + Grafana + logs JSON) | H-039 | 1-2 semanas |
| 24 | **Migrar numpy a 2.x** | H-045 | 2-4 días |
| 25 | **Agregar feature flags** para deploy canary | H-048 | 3-5 días |
| 26 | **Documentar arquitectura y decisiones** (ADRs formales) | H-050 | 2-3 días |

---

## 16. Conclusiones

### 16.1 Lo que el Sistema Hace Bien

1. **Arquitectura hexagonal correctamente implementada**: dominio puro, puertos bien definidos, inversión de dependencias, adaptadores intercambiables.
2. **Stack tecnológico moderno y coherente**: FastAPI + Next.js + PostgreSQL + MongoDB + Redis con integraciones de IA bien pensadas.
3. **Sistema de IA robusto con 4 niveles de fallback**: Dialogflow → Ollama → OpenAI → IntelligentTutor. Resiliencia ante fallos de servicios externos.
4. **CI/CD completo**: linting multi-lenguaje, tests automatizados, build Docker y deploy SSH.
5. **Gestión de errores graceful en capas de infraestructura**: MongoDB, Redis y Ollama pueden fallar sin tirar la app — degradación en lugar de caída.
6. **Seguridad en capas**: bcrypt, JWT con cookie HTTP-only, security headers, redes Docker aisladas, sandbox Docker.
7. **Testing presente**: 28 tests backend, vitest frontend, k6 para carga, CI con service containers.
8. **Documentación de API**: Swagger/OpenAI automático en `/docs`.

### 16.2 Lo que el Sistema Necesita Mejorar

1. **🔴 11 hallazgos críticos de seguridad**: el más urgente es la vulnerabilidad CVE-2024-33663 en python-jose que compromete toda la autenticación.
2. **🔴 main.py de 4000+ líneas**: el mayor problema de mantenibilidad. Mezcla routing, lógica, SQL y manejo de errores.
3. **🟡 Modelo de dominio incompleto**: Lesson y Class (entidades fundamentales) no tienen representación formal.
4. **🟡 Sin lock file Python**: riesgo de supply chain e inconsistencia entre entornos.
5. **🟡 SQL crudo esparcido**: sin ORM, las consultas están duplicadas en main.py y repositorios.
6. **🟡 Degradación silenciosa**: múltiples servicios fallan sin notificar adecuadamente al operador.
7. **🟢 Sin observabilidad**: logs en texto plano, sin métricas, sin tracing.
8. **🟢 Sin tests de integración**: los tests unitarios no cubren el flujo completo.

### 16.3 Calificación Final

| Atributo | Nota |
|----------|:----:|
| **Arquitectura** | 4/5 — Hexagonal bien implementada con deuda puntual |
| **Seguridad** | 2/5 — Vulnerabilidad crítica + múltiples debilidades |
| **Calidad de Código** | 3/5 — Buena estructura pero main.py y SQL esparcido |
| **Testing** | 3.5/5 — Presente pero insuficiente en integración |
| **DevOps** | 4/5 — CI/CD completo, Docker, healthchecks |
| **Documentación** | 3/5 — Swagger bien, falta documentación técnica |
| **Promedio Ponderado** | **3.3/5** — Proyecto sólido con vulnerabilidades críticas que abordar |

### 16.4 Veredicto

RoboLearn muestra un **nivel avanzado de ingeniería de software**: arquitectura limpia, stack moderno, integración sofisticada de inteligencia artificial y automatización DevOps completa. La estructura hexagonal y el diseño modular demuestran madurez técnica.

**Sin embargo, las vulnerabilidades de seguridad son críticas y deben ser abordadas inmediatamente antes de cualquier despliegue a producción.** La vulnerabilidad CVE-2024-33663 (python-jose, CVSS 9.3) permite la falsificación total de tokens JWT, comprometiendo toda la autenticación del sistema. El sandbox de código con `exec()` y blacklist bypasseable representa un riesgo de RCE.

**Con las mitigaciones adecuadas de seguridad (prioritariamente: actualizar python-jose, reemplazar exec() por Docker, separar JWT_SECRET y agregar TLS), el proyecto está listo para producción y tiene potencial para escalar exitosamente.**

---

*Fin del Reporte de Ingeniería Inversa.*

*Documento generado el 2026-06-19. Basado en análisis de código fuente, dependencias, configuración, logs y reconstrucción arquitectónica del proyecto RoboLearn.*
