# Reconstrucción Arquitectónica — RoboLearn

**Rol:** Arquitecto Empresarial  
**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Propósito:** Reconstrucción completa de la arquitectura real del sistema a partir del código fuente, dependencias, configuración, logs y diagramas.

---

## Tabla de Contenidos

1. [Arquitectura General](#1-arquitectura-general)
2. [Vistas Arquitectónicas](#2-vistas-arquitectónicas)
   - 2.1 Vista de Contexto (C4 Nivel 1)
   - 2.2 Vista de Contenedores (C4 Nivel 2)
   - 2.3 Vista de Componentes (C4 Nivel 3)
   - 2.4 Vista de Capas (Layered Architecture)
   - 2.5 Vista de Despliegue
   - 2.6 Vista de Datos
3. [Catálogo de Componentes](#3-catálogo-de-componentes)
4. [Relaciones entre Componentes](#4-relaciones-entre-componentes)
5. [Dependencias Internas y Externas](#5-dependencias-internas-y-externas)
6. [Integraciones](#6-integraciones)
7. [Flujo de Datos](#7-flujo-de-datos)
8. [Arquitectura de Seguridad](#8-arquitectura-de-seguridad)
9. [Atributos de Calidad](#9-atributos-de-calidad)
10. [Decisiones Arquitectónicas (ADRs)](#10-decisiones-arquitectónicas-adrs)
11. [Deuda Técnica y Riesgos](#11-deuda-técnica-y-riesgos)
12. [Recomendaciones](#12-recomendaciones)

---

## 1. Arquitectura General

RoboLearn es una **plataforma educativa de programación asistida por IA** con una arquitectura **híbrida hexagonal-monolítica**: un backend monolítico con diseño hexagonal (Puertos y Adaptadores), un frontend SPA/SSR con Next.js, tres bases de datos especializadas, servicios de IA local y externa, y un pipeline ML independiente.

### Patrón Arquitectónico Predominante

| Patrón | Estado | Confianza |
|--------|--------|-----------|
| **Arquitectura Hexagonal (Puertos y Adaptadores)** | ✅ Implementado | 95% |
| Modular Monolith | ✅ Implementado | 80% |
| Clean Architecture | ⚠️ Parcial | 60% |
| Arquitectura por Capas | ✅ Presente (subordinada) | 75% |

### Diagrama de Arquitectura General (C4 Nivel 1 — Contexto)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROBOLEARN — SISTEMA DE EDUCACIÓN                      │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       USUARIOS DEL SISTEMA                             │   │
│  │  ┌──────────┐  ┌───────────┐  ┌───────────┐                          │   │
│  │  │ Student  │  │  Teacher  │  │   Admin   │                          │   │
│  │  │(aprende) │  │(enseña)   │  │(gobierna) │                          │   │
│  │  └─────┬────┘  └─────┬─────┘  └─────┬─────┘                          │   │
│  └────────┼──────────────┼──────────────┼────────────────────────────────┘   │
│           │              │              │                                    │
│           ▼              ▼              ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     FRONTEND WEB (Next.js 16)                         │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  App Router  │  Componentes shadcn/ui  │  Middleware JWT  │  │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │ HTTP (JWT cookie)                         │
│  ┌──────────────────────────────┼───────────────────────────────────────┐   │
│  │              BACKEND API (FastAPI + Hexagonal)                        │   │
│  │                                                                       │   │
│  │  ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │   │
│  │  │Auth    │  │Modules   │  │Exercises │  │Challenges│  │Classes  │  │   │
│  │  └────┬───┘  └─────┬────┘  └────┬─────┘  └─────┬────┘  └────┬────┘  │   │
│  │       │             │           │              │            │       │   │
│  │  ┌────┴─────────────┴───────────┴──────────────┴────────────┴────┐  │   │
│  │  │            CASOS DE USO + SERVICIOS DE APLICACIÓN              │  │   │
│  │  └────────────────────────────────┬───────────────────────────────┘  │   │
│  │                                   │                                  │   │
│  │  ┌────────────────────────────────┴───────────────────────────────┐  │   │
│  │  │       PUERTOS (domain/ports/) — Interfaces de Dominio           │  │   │
│  │  └────────────────────────────────┬───────────────────────────────┘  │   │
│  │                                   │                                  │   │
│  │  ┌────────────────────────────────┴───────────────────────────────┐  │   │
│  │  │    ADAPTADORES (infrastructure/) — Implementaciones             │  │   │
│  │  └────┬──────────┬──────────┬──────────┬──────────┬──────────────┘  │   │
│  └───────┼──────────┼──────────┼──────────┼──────────┼─────────────────┘   │
│          │          │          │          │          │                      │
│          ▼          ▼          ▼          ▼          ▼                      │
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌───────────┐               │
│    │Postgres│ │ MongoDB│ │ Redis  │ │ Ollama │ │ Docker    │               │
│    │:5432   │ │:27017  │ │:6379   │ │:11434  │ │(sandbox)  │               │
│    └────────┘ └────────┘ └────────┘ └────────┘ └───────────┘               │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │               SERVICIOS EXTERNOS (Opcionales)                         │   │
│  │  ┌─────────────┐  ┌──────────┐  ┌──────────────┐                    │   │
│  │  │ Dialogflow  │  │  OpenAI  │  │  Docker Hub  │                    │   │
│  │  │ (Google)    │  │ (fallback)│  │  (registry)  │                    │   │
│  │  └─────────────┘  └──────────┘  └──────────────┘                    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │           ML PIPELINE (Independiente — scripts Python)                │   │
│  │  ┌──────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐    │   │
│  │  │Generación│→│Entrenamiento│→│Evaluación  │→│NoS.  │    │   │
│  │  │Dataset   │  │(4 modelos) │  │(métricas)  │  │(KMeans,IF)  │    │   │
│  │  └──────────┘  └────────────┘  └────────────┘  └──────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Vistas Arquitectónicas

### 2.1 Vista de Contexto (C4 Nivel 1)

```
┌──────────────────────────────┐
│       ESTUDIANTE             │
│  (Aprende programación,      │
│   resuelve ejercicios,       │
│   consulta al tutor IA)      │
└──────────────┬───────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│                 ROBOLEARN                            │
│  Plataforma educativa de programación asistida por  │
│  IA. Permite aprender, enseñar, gestionar aulas     │
│  virtuales y predecir rendimiento estudiantil.      │
└──────┬──────────────────────┬──────────────────┬────┘
       │                      │                  │
       ▼                      ▼                  ▼
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│  Google Cloud │    │   OpenAI API    │    │  Docker Hub  │
│  Dialogflow   │    │   (opcional)    │    │  (registro)  │
└──────────────┘    └─────────────────┘    └──────────────┘
```

### 2.2 Vista de Contenedores (C4 Nivel 2)

```
┌───────────────────────────────────────────────────────────────────────┐
│                        SISTEMA ROBOLEARN                               │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  Contenedor: Frontend Web                                       │  │
│  │  Tecnología: Next.js 16 + React 19 + TypeScript + Tailwind 4    │  │
│  │  Puerto: 3000                                                   │  │
│  │  Responsabilidad: UI, Server Actions, Middleware JWT, proxy     │  │
│  │  Dependencias: 42 prod + 9 dev                                  │  │
│  └────────────────────────────┬────────────────────────────────────┘  │
│                               │ HTTP/HTTPS                             │
│                               │ JWT (cookie auth-token)                 │
│                               ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  Contenedor: Backend API                                        │  │
│  │  Tecnología: FastAPI 0.109 + Python 3.11 + Uvicorn              │  │
│  │  Puerto: 8000                                                   │  │
│  │  Responsabilidad: REST API, lógica de negocio, integraciones    │  │
│  │  Dependencias: 19 Python, 5 puertos, 5 casos de uso             │  │
│  └──┬──────────┬──────────┬──────────┬──────────┬──────────────────┘  │
│     │          │          │          │          │                     │
│     ▼          ▼          ▼          ▼          ▼                     │
│  ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐          │
│  │Postgr│ │MongoDB │ │ Redis  │ │ Ollama │ │  Docker    │          │
│  │:5432 │ │:27017  │ │:6379   │ │:11434  │ │  (sandbox) │          │
│  └──────┘ └────────┘ └────────┘ └────────┘ └────────────┘          │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  Contenedor: ML Pipeline (Independiente)                        │  │
│  │  Tecnología: Python + scikit-learn 1.8                          │  │
│  │  Responsabilidad: Entrenamiento y evaluación de modelos ML      │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
```

### 2.3 Vista de Componentes (C4 Nivel 3)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      BACKEND — COMPONENTES INTERNOS                      │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  CAPA DE PRESENTACIÓN (app/)                                       │ │
│  │                                                                   │ │
│  │  ┌─────────────────────────────────────────────────────────┐      │ │
│  │  │  main.py (Routers y Middleware)                          │      │ │
│  │  │  ├── Endpoints REST (~144 endpoints)                    │      │ │
│  │  │  ├── Middleware HTTP (CORS, Audit, Security Headers)    │      │ │
│  │  │  ├── Lifespan (init DB, pool, Google credentials)      │      │ │
│  │  │  └── Error handlers globales                           │      │ │
│  │  └─────────────────────────────────────────────────────────┘      │ │
│  │  ┌─────────────────────────────────────────────────────────┐      │ │
│  │  │  schemas/ (9 archivos Pydantic v2)                      │      │ │
│  │  │  ├── auth.py, ai.py, classes.py                         │      │ │
│  │  │  ├── exercises.py, challenges.py                        │      │ │
│  │  │  ├── modules.py, common.py                              │      │ │
│  │  │  └── schemas/__init__.py                               │      │ │
│  │  └─────────────────────────────────────────────────────────┘      │ │
│  │  ┌─────────────────────────────────────────────────────────┐      │ │
│  │  │  dependencies.py (Wiring DI centralizado)                │      │ │
│  │  └─────────────────────────────────────────────────────────┘      │ │
│  │  ┌─────────────────────────────────────────────────────────┐      │ │
│  │  │  exceptions.py, logging_config.py                        │      │ │
│  │  └─────────────────────────────────────────────────────────┘      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  CAPA DE APLICACIÓN (application/)                                 │ │
│  │                                                                   │ │
│  │  ┌────────────────────────────────┐ ┌────────────────────────┐    │ │
│  │  │  useCases/ (5 formales)        │ │  services/ (9 servicios) │    │ │
│  │  │  ├── RegisterUserUseCase       │ │  ├── ai_service_impl.py │    │ │
│  │  │  ├── EnrollStudentUseCase      │ │  ├── intelligent_tutor  │    │ │
│  │  │  ├── GetRecommendationsUseCase  │ │  ├── llm_service.py    │    │ │
│  │  │  ├── TeacherDashboardUseCase   │ │  ├── embedding_service  │    │ │
│  │  │  └── GenerateAIAlertsUseCase   │ │  ├── rag_service.py     │    │ │
│  │  └────────────────────────────────┘ │  ├── ai_tutor_service   │    │ │
│  │                                     │  ├── sandbox_service    │    │ │
│  │  ┌────────────────────────────────┐ │  └── exercise_gen...    │    │ │
│  │  │  services/ml/ (12 archivos)    │ └────────────────────────┘    │ │
│  │  │  ├── orchestrator.py          │                                │ │
│  │  │  ├── recommender.py           │ ┌────────────────────────┐    │ │
│  │  │  ├── engagement_predictor     │ │  services/analytics/   │    │ │
│  │  │  ├── performance_predictor    │ │  ├── analytics_router  │    │ │
│  │  │  ├── dropout_predictor        │ │  ├── metrics_service   │    │ │
│  │  │  ├── frustration_predictor    │ │  └── scheduler_service │    │ │
│  │  │  ├── clustering.py            │ └────────────────────────┘    │ │
│  │  │  ├── anomaly_detector.py      │                                │ │
│  │  │  ├── feature_extractor.py     │                                │ │
│  │  │  ├── base_predictor.py        │                                │ │
│  │  │  └── synthetic_dataset.py     │                                │ │
│  │  └────────────────────────────────┘                                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  CAPA DE DOMINIO (domain/)                                         │ │
│  │                                                                   │ │
│  │  ┌──────────────────────┐ ┌────────────────┐ ┌──────────────┐    │ │
│  │  │  entities/ (7)       │ │  ports/ (5)    │ │ valueObjects/ │    │ │
│  │  │  ├── user.py         │ │ ├── user_repo  │ │ ├── progress  │    │ │
│  │  │  ├── module.py       │ │ ├── module_repo│ │ └── ...       │    │ │
│  │  │  ├── exercise.py     │ │ ├── enroll_repo│ └──────────────┘    │ │
│  │  │  ├── challenge.py    │ │ ├── teacher_repo│                     │ │
│  │  │  ├── enrollment.py   │ │ └── ai_service │                     │ │
│  │  │  ├── achievement.py  │ └────────────────┘                     │ │
│  │  │  └── alert.py        │                                        │ │
│  │  └──────────────────────┘                                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  CAPA DE INFRAESTRUCTURA (infrastructure/)                         │ │
│  │                                                                   │ │
│  │  ┌─────────────────────────────────────────────────────────┐      │ │
│  │  │  adapters/output/                                       │      │ │
│  │  │  ├── postgres/ (4 repos + connection)                   │      │ │
│  │  │  │   ├── user_repository_impl.py                       │      │ │
│  │  │  │   ├── module_repository_impl.py                     │      │ │
│  │  │  │   ├── enrollment_repository_impl.py                 │      │ │
│  │  │  │   └── teacher_repository_impl.py                    │      │ │
│  │  │  ├── mongo/ (2 repos)                                   │      │ │
│  │  │  │   ├── event_repository_impl.py                      │      │ │
│  │  │  │   └── behavioral_repository.py                      │      │ │
│  │  │  ├── redis/ (2 servicios)                               │      │ │
│  │  │  │   ├── cache.py (AICache)                             │      │ │
│  │  │  │   └── rate_limiter.py (RateLimiter)                 │      │ │
│  │  │  └── docker/ (1 servicio)                               │      │ │
│  │  │      └── code_executor.py (CodeExecutor)               │      │ │
│  │  └─────────────────────────────────────────────────────────┘      │ │
│  │  ┌─────────────────────────────────────────────────────────┐      │ │
│  │  │  adapters/input/                                         │      │ │
│  │  │  └── analytics_router.py                                │      │ │
│  │  └─────────────────────────────────────────────────────────┘      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Vista de Capas (Layered Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│ CAPA             │ RESPONSABILIDAD               │ TECNOLOGÍA       │
├─────────────────────────────────────────────────────────────────────┤
│ Presentación     │ Routers REST, middleware,      │ FastAPI, Pydantic│
│ (app/)           │ schemas, DI wiring            │ Uvicorn          │
├─────────────────────────────────────────────────────────────────────┤
│ Aplicación       │ Casos de uso, orquestación,   │ Python puro      │
│ (application/)   │ servicios de IA, ML, tutor    │ scikit-learn     │
├─────────────────────────────────────────────────────────────────────┤
│ Dominio          │ Entidades, puertos, value     │ Python puro      │
│ (domain/)        │ objects — núcleo del negocio  │ (sin imports)    │
├─────────────────────────────────────────────────────────────────────┤
│ Infraestructura  │ Implementaciones concretas     │ psycopg2, PyMongo│
│ (infrastructure/)| de puertos (DBs, Redis,       │ redis, Docker SDK│
│                  │ Docker, cache, rate limit)     │ httpx            │
├─────────────────────────────────────────────────────────────────────┤
│ Config           │ Settings desde .env,          │ Pydantic Settings│
│ (config/)        │ init de base de datos         │                 │
└─────────────────────────────────────────────────────────────────────┘
           │
           │ Inversión de dependencias:
           │ app/ → application/ → domain/ ← infrastructure/
           │
           └── domain/ (sin dependencias externas)
               application/ → interfaces en domain/
               infrastructure/ → implementa interfaces de domain/
               app/ → orquesta todo
```

### 2.5 Vista de Despliegue

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      SERVIDOR LINUX (VPS / Local)                           │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        DOCKER ENGINE                                   │   │
│  │                                                                       │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────┐ ┌──────────────────┐  │   │
│  │  │  postgres    │ │   mongo     │ │   redis   │ │    ollama        │  │   │
│  │  │  pgvector    │ │   mongo:7   │ │ redis:7   │ │  ollama/ollama  │  │   │
│  │  │  pg16        │ │             │ │  alpine   │ │  qwen2.5-coder  │  │   │
│  │  └──────┬───────┘ └──────┬──────┘ └─────┬─────┘ └────────┬─────────┘  │   │
│  │         │                │              │                │             │   │
│  │         └────────────────┴──────────────┴────────────────┘             │   │
│  │                              │ internal_net                             │   │
│  │                      ┌───────┴──────────┐                              │   │
│  │                      │    backend        │                              │   │
│  │                      │    FastAPI        │                              │   │
│  │                      │    :8000          │                              │   │
│  │                      └───────┬──────────┘                              │   │
│  │                              │ frontend_net                             │   │
│  │                      ┌───────┴──────────┐                              │   │
│  │                      │    frontend       │                              │   │
│  │                      │    Next.js        │                              │   │
│  │                      │    :3000          │                              │   │
│  │                      └──────────────────┘                              │   │
│  │                                                                         │   │
│  │  Volúmenes: postgres_data, mongo_data, redis_data, ollama_data         │   │
│  │  Redes: frontend_net (bridge, público), internal_net (bridge, interno), │   │
│  │         ai_net (bridge, semi-público)                                   │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │  CI/CD (GitHub Actions)                                                  │   │
│  │  ┌────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────────────┐   │   │
│  │  │ Push   │──▶│   CI     │──▶│   Build  │──▶│   Deploy (SSH VPS)  │   │   │
│  │  │ main/  │   │ lint+test│   │ Docker   │   │ docker compose pull │   │   │
│  │  │ develop│   │ +coverage│   │ images   │   │ + docker compose up │   │   │
│  │  └────────┘   └──────────┘   └──────────┘   └─────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### 2.6 Vista de Datos

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      MAPA DE DATOS — FLUJO ENTRE SISTEMAS                     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                     POSTGRESQL 16 + pgvector                        │     │
│  │                                                                     │     │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │     │
│  │  │ Datos        │ │ Contenido    │ │ Relacionales │               │     │
│  │  │ de Usuario   │ │ Educativo    │ │              │               │     │
│  │  ├──────────────┤ ├──────────────┤ ├──────────────┤               │     │
│  │  │ users        │ │ modules      │ │ enrollments  │               │     │
│  │  │ user_achieve │ │ lessons      │ │ class_enroll │               │     │
│  │  │ ments        │ │ exercises    │ │ class_modules│               │     │
│  │  │              │ │ challenges   │ │ class_exerci │               │     │
│  │  │              │ │ classes      │ │ ses          │               │     │
│  │  │              │ │ knowledge_   │ │ exercise_    │               │     │
│  │  │              │ │ chunks       │ │ attempts     │               │     │
│  │  │              │ │ (pgvector)   │ │ progress     │               │     │
│  │  └──────────────┘ └──────────────┘ └──────────────┘               │     │
│  │  Almacena: ~22 tablas, 8 stored procedures, 1 vista               │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                │                                            │
│                                ▼                                            │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                     MONGODB 7 (robolearn_metrics)                   │     │
│  │                                                                     │     │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │     │
│  │  │ Eventos      │ │ Conductual   │ │ ML/Analítica │               │     │
│  │  ├──────────────┤ ├──────────────┤ ├──────────────┤               │     │
│  │  │ events       │ │ behavioral_  │ │ predictions  │               │     │
│  │  │ chat_interac │ │ events       │ │ engagement_  │               │     │
│  │  │ tions        │ │ frustration_ │ │ scores       │               │     │
│  │  │ tutor_inter  │ │ signals      │ │ admin_stats  │               │     │
│  │  │ actions      │ │ code_analysis│ │ session_     │               │     │
│  │  │ exercise_at  │ │ sessions     │ │ metrics      │               │     │
│  │  │ tempts       │ │ progress_sna │ │              │               │     │
│  │  │              │ │ pshots       │ │              │               │     │
│  │  └──────────────┘ └──────────────┘ └──────────────┘               │     │
│  │  Almacena: ~13 colecciones, datos de sesión, analítica             │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                │                                            │
│                                ▼                                            │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                     REDIS 7 (Caché + Rate Limit)                    │     │
│  │                                                                     │     │
│  │  ┌──────────────────────┐ ┌──────────────────┐ ┌──────────────┐   │     │
│  │  │ Cache de respuestas  │ │ Rate Limiting    │ │ Token Black- │   │     │
│  │  │ de IA (Ollama)       │ │ (requests/min)   │ │ list (JWT)  │   │     │
│  │  │ Cache de embeddings  │ │                  │ │              │   │     │
│  │  └──────────────────────┘ └──────────────────┘ └──────────────┘   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Catálogo de Componentes

### 3.1 Backend — Por Capa Hexagonal

| Componente | Tipo | Responsabilidad | Archivos |
|------------|------|----------------|----------|
| **main.py** | Entry Point | Punto de entrada FastAPI, 144 endpoints, middleware, lifespan | 1 archivo (4082 líneas) |
| **dependencies.py** | DI Container | Wiring de todas las dependencias: repos, servicios, lazy AI/ML | 1 archivo (305 líneas) |
| **schemas/** | DTOs | 9 archivos Pydantic v2 para request/response | 9 archivos |
| **exceptions.py** | Error Handling | Manejador global de excepciones | 1 archivo |
| **logging_config.py** | Logging | Configuración de logger (stdout, INFO) | 1 archivo |
| **domain/entities/** | Entidades | 7 entidades de dominio puras (User, Module, Exercise, etc.) | 7 archivos |
| **domain/ports/** | Puertos | 5 interfaces abstractas para repositorios y servicios | 5 archivos |
| **domain/valueObjects/** | VOs | 1 value object formal (Progress) + enums implícitos | 1 archivo |
| **application/useCases/** | Casos de Uso | 5 casos de uso formales que orquestan lógica | 5 archivos |
| **application/services/** | Servicios | 9 servicios de aplicación (IA, Tutor, RAG, Sandbox, etc.) | 9 archivos |
| **application/services/ml/** | ML Service | 12 archivos: 6 predictores + orquestador + extractor + dataset | 12 archivos |
| **application/services/analytics/** | Analytics | 3 archivos: router + metrics + scheduler | 3 archivos |
| **infrastructure/postgres/** | Adapter | 4 repositorios PostgreSQL + pool de conexiones | 5 archivos |
| **infrastructure/mongo/** | Adapter | 2 repositorios MongoDB (eventos + conductual) | 2 archivos |
| **infrastructure/redis/** | Adapter | 2 servicios Redis (caché IA + rate limiter) | 2 archivos |
| **infrastructure/docker/** | Adapter | 1 servicio Docker (code executor sandbox) | 1 archivo |
| **config/settings.py** | Config | Pydantic Settings mapeado desde .env | 1 archivo |
| **config/database_init.py** | Config | Inicialización automática de BD al arrancar | 1 archivo |
| **scripts/** | SQL/JS | 5 scripts SQL + 2 scripts JS de inicialización | 7 archivos |

### 3.2 Frontend

| Componente | Tipo | Responsabilidad | Archivos/Directorios |
|------------|------|----------------|---------------------|
| **app/** | Páginas | App Router de Next.js con layout, landing, login, register, dashboard, logout | 8 subdirectorios |
| **app/dashboard/** | Dashboard UI | Panel principal con subrutas para módulos, ejercicios, clases, challenges, analítica, logros, settings | 15+ subdirectorios |
| **components/** | Componentes UI | Componentes reutilizables: chat-widget, code-editor, dashboard widgets, error-boundary, theme-provider | 7 subdirectorios |
| **components/ui/** | UI Primitives | shadcn/ui componentes (button, card, dialog, etc.) — ~30 archivos | 30+ archivos |
| **components/dashboard/** | Dashboard Widgets | Sidebars, gráficos, tablas del dashboard por rol | 10+ archivos |
| **components/chat/** | Chat Widget | Widget de chat con el tutor IA | 2+ archivos |
| **lib/utils.ts** | Utilidades | clsx + tailwind-merge para clases CSS | 1 archivo |
| **proxy.ts** | Middleware | Next.js Middleware para verificación JWT en rutas protegidas | 1 archivo |
| **hooks/** | Custom Hooks | Hooks de React (use-auth, etc.) | 2+ archivos |
| **public/** | Assets | Archivos estáticos, imágenes, favicon | — |

### 3.3 ML Pipeline (Independiente)

| Componente | Responsabilidad | Archivos |
|------------|----------------|----------|
| **01_generate_dataset.py** | Genera dataset sintético (10K estudiantes × 16 semanas) | 1 archivo |
| **02_train_models.py** | Entrena 4 modelos supervisados (RandomForest) | 1 archivo |
| **03_evaluate_models.py** | Evalúa modelos en test set, genera reportes | 1 archivo |
| **04_train_unsupervised.py** | Entrena KMeans (clustering) + IsolationForest (anomalías) | 1 archivo |
| **run_all.py** | Orquestador: ejecuta pipeline completo o parcial | 1 archivo |
| **src/dataset.py** | Generación de datos sintéticos | 1 archivo |
| **src/features.py** | Ingeniería de características (sliding windows, 12 ventanas) | 1 archivo |
| **src/models.py** | Definición de 6 modelos (RandomForest, KMeans, IsolationForest) | 1 archivo |
| **src/windows.py** | Construcción de ventanas temporales para features | 1 archivo |
| **src/metrics.py** | Cálculo de métricas de evaluación (R², MSE, F1, ROC-AUC) | 1 archivo |

### 3.4 Infraestructura de Soporte (Docker Compose)

| Servicio | Imagen | Rol | Puertos |
|----------|--------|-----|---------|
| **postgres** | pgvector/pgvector:pg16 | Base de datos transaccional + RAG vectorial | 5432 |
| **mongo** | mongo:7 | Base de datos analítica y de eventos | 27017 |
| **redis** | redis:7-alpine | Caché de IA, rate limiting, blacklist de tokens | 6379 |
| **ollama** | ollama/ollama:latest | LLM local (Qwen2.5-Coder 1.5B) | 11434 |
| **backend** | Build local (Dockerfile) | API FastAPI | 8000 |
| **frontend** | Build local (Dockerfile) | UI Next.js | 3000 |

---

## 4. Relaciones entre Componentes

### 4.1 Mapa de Conexiones

```
Frontend (Next.js)
  │
  ├── HTTP ── backend:8000 ── (frontend_net)
  │     │
  │     ├── postgres:5432 ── (internal_net)
  │     │     └── pgvector (RAG)
  │     │
  │     ├── mongo:27017 ──── (internal_net)
  │     │
  │     ├── redis:6379 ───── (internal_net)
  │     │
  │     ├── ollama:11434 ─── (ai_net)
  │     │
  │     └── /var/run/docker.sock ── (Docker sandbox)
  │
  └── JWT (auth-token cookie)
        └── SECRET_KEY compartido (⚠️ riesgo)

APIs Externas:
  ├── Dialogflow (Google Cloud) ── backend ── via httpx / google-cloud SDK
  ├── OpenAI API ── backend ── via httpx
  └── Docker Hub ── GitHub Actions (CI/CD)
```

### 4.2 Matriz de Comunicación entre Componentes

| Origen \ Destino | PostgreSQL | MongoDB | Redis | Ollama | Docker | Dialogflow | OpenAI | Frontend |
|------------------|-----------|---------|-------|--------|--------|------------|--------|----------|
| **Backend API** | ✅ SQL | ✅ Eventos | ✅ Cache | ✅ LLM | ✅ Code | ✅ Chatbot | ✅ Fallback | ✅ HTTP |
| **Frontend** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — |
| **ML Pipeline** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **GitHub CI/CD** | ❌ | ❌ | ❌ | ❌ | ✅ Build | ❌ | ❌ | ✅ Build |

### 4.3 Dependencias entre Capas (Backend)

```
app/main.py
  │
  ├──→ app/dependencies.py
  │       │
  │       ├──→ infrastructure/adapters/output/postgres/*  (implementan ports)
  │       ├──→ infrastructure/adapters/output/mongo/*
  │       ├──→ infrastructure/adapters/output/redis/*
  │       ├──→ application/services/*                     (servicios de aplicación)
  │       ├──→ application/useCases/*                     (casos de uso)
  │       └──→ domain/entities/*                          (entidades)
  │
  ├──→ app/schemas/*        (DTOs — dependen de domain/entities)
  ├──→ config/settings.py   (config — sin dependencias del proyecto)
  └──→ app/exceptions.py    (error handling)

application/useCases/*
  └──→ domain/ports/*       (depende de interfaces, no implementaciones)
  └──→ domain/entities/*    (usa entidades)

infrastructure/adapters/output/*
  └──→ domain/ports/*       (implementa interfaces de dominio)
  └──→ config/settings.py   (usa configuración)

domain/*
  └── (sin dependencias del proyecto — Python puro)
```

---

## 5. Dependencias Internas y Externas

### 5.1 Dependencias Internas

| Dependencia | Tipo | Versión | Rol en la Arquitectura |
|-------------|------|---------|------------------------|
| FastAPI | Framework | 0.109.0 | Base del backend REST |
| Uvicorn | Servidor | 0.27.0 | ASGI server |
| Pydantic | Validación | 2.5.0 | Schemas, DTOs, settings |
| python-jose | JWT | 3.3.0 | 🔴 Vulnerabilidad CRÍTICA (CVE-2024-33663) |
| bcrypt | Hashing | 3.2.0 | Hash de contraseñas |
| psycopg2-binary | Driver PG | 2.9.9 | Conexión PostgreSQL |
| pymongo | Driver Mongo | 4.6.0 | Conexión MongoDB |
| redis[hiredis] | Driver Redis | 5.1.0 | Caché + rate limiting |
| scikit-learn | ML | 1.8.0 | Modelos predictivos |
| httpx | HTTP Client | 0.27.0 | Llamadas a Ollama, OpenAI |
| docker | Docker SDK | 7.1.0 | Sandbox de código |
| APScheduler | Scheduling | 3.10.4 | Snapshot semanal |
| Next.js | Framework | 16.2.4 | 🟡 Vulnerabilidad ALTA (CVE-2026-44581) |
| React | UI | 19.2.4 | Base UI frontend |
| Radix UI | Primitivas | 13 paquetes | Componentes accesibles |
| CodeMirror | Editor | 4.25.9 | Editor de código embebido |
| recharts | Charts | 2.15.0 | Gráficos de analítica |

### 5.2 Dependencias Externas

| Dependencia | Tipo | Propósito | Modo de Falla |
|-------------|------|-----------|---------------|
| **PostgreSQL 16 + pgvector** | Base de Datos | Datos principales del sistema | CRÍTICO — app no inicia |
| **MongoDB 7** | Base de Datos | Eventos y analítica conductual | DEGRADACIÓN — datos no persisten |
| **Redis 7** | Caché | Caché IA, rate limiting, token blacklist | DEGRADACIÓN — sin caché ni rate limit |
| **Ollama + Qwen2.5-Coder** | LLM Local | Tutor IA, RAG, generación de ejercicios | DEGRADACIÓN — fallback a reglas |
| **Dialogflow CX** | Chatbot | Chatbot conversacional primario | DEGRADACIÓN — fallback a Ollama |
| **OpenAI API** | LLM Cloud | Fallback de IA terciario | DEGRADACIÓN — fallback a tutor reglas |
| **Docker Engine** | Sandbox | Ejecución segura de código | LIMITADO — sandbox code no disponible |
| **Docker Hub** | Registry | Almacenamiento de imágenes | CI/CD — bloquea deploy |

### 5.3 Dependencias de Despliegue

| Herramienta | Propósito | Alternativa |
|-------------|-----------|-------------|
| Docker Engine 24+ | Ejecución de contenedores | Podman |
| Docker Compose v2+ | Orquestación multi-servicio | Podman-compose |
| GitHub Actions | CI/CD | GitLab CI, Jenkins |
| Codecov | Cobertura de tests | SonarQube |

---

## 6. Integraciones

### 6.1 Integraciones Internas

| Integración | Protocolo | Frecuencia | Patrón |
|-------------|-----------|------------|--------|
| Backend ↔ PostgreSQL | SQL/TCP | Por request | Síncrono (pool ThreadedConnectionPool) |
| Backend ↔ MongoDB | MongoDB Wire/TCP | Por request | Síncrono (fire-and-forget logs) |
| Backend ↔ Redis | Redis Serial/TCP | Por request | Asíncrono (redis.asyncio) |
| Backend ↔ Ollama | HTTP REST | Por request de IA | Síncrono (httpx) |
| Backend ↔ Docker | Docker Socket | Por ejecución de código | Síncrono (docker SDK) |
| Frontend ↔ Backend | HTTP REST | Por request | Síncrono (fetch) |

### 6.2 Integraciones Externas

| Integración | Protocolo | Autenticación | Propósito | Modo Falla |
|-------------|-----------|---------------|-----------|------------|
| Backend ↔ Dialogflow | gRPC/HTTPS | Google Cloud Auth (JSON key) | Chatbot primario | Fallback → Ollama |
| Backend ↔ OpenAI | HTTPS | API Key | Fallback IA | Fallback → IntelligentTutor |
| GitHub ↔ Docker Hub | HTTPS | Docker Hub credentials | CI/CD push | Deploy bloqueado |
| GitHub → VPS | SSH | SSH key | Deploy remoto | Deploy bloqueado |

### 6.3 Integración de ML Pipeline

La pipeline ML no está integrada en tiempo real con el backend. Es un proceso **independiente** que:

1. Genera dataset sintético → `data/robolearn_dataset.parquet`
2. Entrena modelos → exporta a `models/*.pkl`
3. Evalúa → exporta reportes a `reports/`

El backend carga los modelos `.pkl` en tiempo de ejecución (si existen). Si no existen, el sistema **no falla** sino que opera en modo degradado (sin predicciones ML).

---

## 7. Flujo de Datos

### 7.1 Flujo End-to-End: Estudiante Resuelve un Ejercicio

```
1. Browser                          → Frontend (Next.js)
   GET /dashboard/exercises              │
                                         │ (Middleware JWT check en proxy.ts)
                                         │ Cookie: auth-token
                                         ▼
2. Frontend                         → Backend (FastAPI)
   GET /api/exercises                    │
                                         │ verify_token (JWT decode + blacklist check)
                                         │ user_repository.get_by_id()
                                         ▼
3. Backend ← PostgreSQL                │
   SELECT * FROM exercises WHERE ...    │
                                         │
4. Response                         → Frontend
   JSON {exercises: [...]}              │
                                         │ Render: lista de ejercicios
                                         ▼
5. Estudiante hace clic en ejercicio  │
                                         ▼
6. Frontend                         → Backend (editor CodeMirror)
   POST /api/exercises/submit           │
   {code: "print('Hello')"}             │
                                         │
7. SandboxService                       │
   ├── validate_code()  ← AST parse + blacklist check
   ├── executor = CodeExecutor          │
   │     ├── docker run (python:3.11-slim, 64MB, 0.5 CPU, --read-only, --network=none)
   │     ├── container.wait(timeout=10) │
   │     └── container.logs()           │
   └── execute_and_compare()            │
                                         │
8. Backend ← PostgreSQL                │
   INSERT INTO exercise_attempts        │
   (ON CONFLICT DO NOTHING con retry)   │
                                         │
9. if passed:                           │
   ├── UPDATE progress                  │
   ├── UPDATE users (points +=)         │
   ├── check_and_award_achievements()   │
   └── event_repository.log_event()     │
                                         │
10. Response                         → Frontend
    {passed: true/false, score, ...}    │
                                         │
11. Frontend ← MongoDB                │
    (logging de interacción via         │
     asyncio.create_task)               ▼
```

### 7.2 Flujo de Chatbot Omnicanal (Sistema Híbrido de IA)

```
POST /api/chatbot (usuario envía mensaje)
  │
  ├─ 1. Intentar Dialogflow (Google Cloud)
  │     └─ ¿Respuesta válida? → Retornar {source: "dialogflow", response}
  │
  ├─ 2. Intentar Ollama (LLM local)
  │     └─ ¿Respuesta válida? → Retornar {source: "ollama", response}
  │                               └─ Cachear en Redis
  │
  ├─ 3. Intentar OpenAI (fallback opcional)
  │     └─ ¿Respuesta válida? → Retornar {source: "openai", response}
  │
  └─ 4. IntelligentTutor (basado en reglas)
        └─ Retornar {source: "tutor", response}
           (detecta intención: saludo/pista/ejemplo/error/recomendación)
  │
  └─ (Background) Log interacción en MongoDB
```

### 7.3 Flujo de Datos del Pipeline ML

```
ml_pipeline/run_all.py
  │
  ├─ 01_generate_dataset.py
  │     └─ Genera 10,000 estudiantes × 16 semanas de actividad sintética
  │           └─ data/robolearn_dataset.parquet
  │
  ├─ 02_train_models.py
  │     ├─ Construye sliding windows (12 ventanas)
  │     ├─ Entrena RandomForestRegressor (engagement, performance)
  │     ├─ Entrena RandomForestClassifier (dropout, frustration, balanceado)
  │     └─ Exporta modelos → models/*.pkl
  │
  ├─ 03_evaluate_models.py
  │     ├─ Evalúa en test set
  │     ├─ Métricas: R², MSE, MAE, RMSE, Accuracy, F1, Precision, Recall, ROC-AUC
  │     └─ Exporta reportes → reports/metrics.json + reports/report.md
  │
  └─ 04_train_unsupervised.py
        ├─ KMeans (4 clusters) + PCA para visualización
        ├─ IsolationForest (contamination=0.1)
        └─ Exporta modelos → models/*.pkl

  Los modelos .pkl son cargados por el backend en:
    application/services/ml/orchestrator.py
    → MLOrchestrator.reload_models()
```

### 7.4 Flujo de Inicialización del Sistema

```
docker compose up
  │
  ├─ postgres:
  │     └─ docker-entrypoint-initdb.d/
  │           ├─ 01-init.sql (22 tablas, 8 stored procedures)
  │           ├─ 02-seed.sql (datos semilla)
  │           ├─ 03-massive.sql (datos masivos de prueba)
  │           └─ 05-pgvector.sql (extensión vector + knowledge_chunks)
  │
  ├─ mongo:
  │     └─ init-db.js (13 colecciones)
  │
  ├─ redis:
  │     └─ redis-server --appendonly yes
  │
  ├─ ollama:
  │     └─ ollama serve + pull qwen2.5-coder:1.5b
  │
  └─ backend (lifespan):
        ├─ Cargar Google Credentials (si existe robolearn-key.json)
        ├─ initialize_database() → (crear DB si no existe, ejecutar scripts SQL/JS)
        ├─ PostgresConnection.init_pool() → pool de 5-50 conexiones
        ├─ Import lazy: analytics_router (numpy se carga aquí, no en import)
        └─ app.include_router(analytics_router)
```

---

## 8. Arquitectura de Seguridad

### 8.1 Estrategia de Autenticación

| Componente | Tecnología | Detalle |
|------------|------------|---------|
| Token | JWT | HS256 (default), RS256 (opcional) |
| Transporte | Cookie HTTP-only | `auth-token`, SameSite=Lax, Secure solo en prod |
| Claims | user_id, email, role, exp, iat, jti | Incluye JWT ID para blacklist |
| Expiración | 10080 minutos (7 días) | Configurable |
| Hash | bcrypt | Coste por defecto, truncado a 72 caracteres |
| Blacklist | Redis | Tokens revocados via `jti`, fallback a False si Redis caído |
| Middleware | Next.js proxy.ts | Verifica JWT en frontend antes de llegar al backend |

### 8.2 Estrategia de Autorización

| Rol | Permisos | Verificación |
|-----|----------|-------------|
| **STUDENT** | Acceder a módulos, resolver ejercicios, chat, ver propio progreso | `verify_token` |
| **TEACHER** | Todo lo de student + crear contenido, gestionar clases, ver analytics | `verify_teacher` |
| **ADMIN** | Todo lo de teacher + gestionar usuarios, aprobar contenido, auditoría | `verify_admin` |

### 8.3 Seguridad en el Transporte

| Capa | Medida |
|------|--------|
| HTTP → HTTPS | ❌ No configurado — depende del proxy reverso (no implementado) |
| CORS | `CORS_ORIGINS` configurable, multi-origen |
| CSP | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| HSTS | Solo en producción: `max-age=31536000; includeSubDomains` |
| X-Frame-Options | `DENY` |
| X-Content-Type-Options | `nosniff` |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| Redes Docker | `internal_net` aislada (bridge interno), tráfico plano entre servicios |

### 8.4 Seguridad de Datos

| Aspecto | Estado |
|---------|--------|
| Contraseñas | bcrypt hashing (truncado a 72 caracteres) |
| Token JWT | Firmado HMAC-SHA256 o RSA-SHA256 |
| Conexiones BD | Sin TLS — PostgreSQL, MongoDB y Redis en red interna aislada |
| SQL Injection | ⚠️ Riesgo en `database_init.py` (f-string), endpoints usan parámetros |
| JWT Algorithm | ⚠️ `_decode_token_fallback` prueba RS256 luego HS256 — por diseño pero riesgoso |
| Secretos compartidos | ⚠️ `JWT_SECRET` compartido frontend/backend |

### 8.5 Seguridad del Sandbox de Código

| Capa | Medida | Efectividad |
|------|--------|-------------|
| AST Validation | `ast.parse(code)` antes de ejecución | Alta — código mal formado es rechazado |
| Blacklist de patrones | Lista negra de strings: `os`, `subprocess`, `eval`, `exec`, `open`, `socket`, etc. | ⚠️ BAJA — bypasseable con concatenación |
| Docker Container | `python:3.11-slim`, `--read-only`, `--network=none`, `--memory=64m`, `--cpus=0.5`, sin privilegios | Alta — incluso si bypassean blacklist, el contenedor limita daños |
| Timeout | 10 segundos | Media — previene bucles infinitos |

### 8.6 Seguridad de Red (Docker)

```
frontend_net (bridge, público)
  │
  │ Solo frontend y backend tienen acceso
  │ frontend → backend (HTTP)
  │
  ├─── internal_net (bridge, INTERNO)
  │     │
  │     │ backend → postgres (SQL)
  │     │ backend → mongo (MongoDB Wire)
  │     │ backend → redis (Redis Protocol)
  │     │
  │     └── Aislado del exterior — solo contenedores en esta red
  │
  └─── ai_net (bridge, semi-público)
        │
        │ backend → ollama (HTTP)
        │
        └── Acceso externo posible pero limitado
```

---

## 9. Atributos de Calidad

### 9.1 Escalabilidad

| Aspecto | Evaluación |
|---------|-----------|
| **Horizontal (backend)** | Limitada — monolito FastAPI, escalable con múltiples instancias detrás de un balanceador |
| **Vertical (backend)** | Posible — aumentar recursos del contenedor |
| **Bases de datos** | PostgreSQL: escalable verticalmente, réplicas de lectura. MongoDB: sharding posible |
| **Frontend** | Stateless — escalable horizontalmente con CDN/balanceador |
| **Cuello de botella** | PostgreSQL (22 tablas, pool 5-50 conexiones) y ejecución de código Docker sincrónica |

### 9.2 Disponibilidad

| Componente | Estrategia de Alta Disponibilidad |
|------------|----------------------------------|
| PostgreSQL | Healthcheck + restart always. Sin réplicas configuradas |
| MongoDB | Healthcheck + restart always. Sin replica set |
| Redis | Healthcheck + restart always. AOF persistence |
| Backend | Healthcheck + restart always. Sin multi-instancia |
| Frontend | Depende de backend. Sin healthcheck en Docker |

### 9.3 Resiliencia

| Escenario | Comportamiento |
|-----------|---------------|
| **PostgreSQL caído** | App no inicia (`depends_on: condition: service_healthy`) |
| **MongoDB caído** | Degradación graceful (logs no persisten, dashboard sin datos) |
| **Redis caído** | Degradación graceful (sin caché IA, sin rate limiting, sin token blacklist) |
| **Ollama caído** | Degradación graceful (fallback a OpenAI → IntelligentTutor) |
| **Dialogflow caído** | Degradación graceful (fallback a Ollama) |
| **OpenAI caído o no configurado** | Degradación graceful (fallback a IntelligentTutor) |
| **Docker daemon caído** | Sandbox de código no disponible |
| **Timeout agregaciones** | Dashboard parcial con warm en background |

### 9.4 Rendimiento

| Componente | Límite / Configuración |
|------------|----------------------|
| **Pool PostgreSQL** | Mínimo 5, máximo 50 conexiones |
| **Timeout agregaciones MongoDB** | 3 segundos |
| **Timeout predicciones** | 5 segundos |
| **Timeout sandbox código** | 10 segundos |
| **Memoria Ollama** | Límite 4GB |
| **Memoria sandbox** | 64MB por contenedor |
| **CPU sandbox** | 0.5 CPU por contenedor |
| **Lazy imports** | numpy/scikit-learn cargados solo cuando se usan (en handlers de analytics) |
| **Cache de IA** | Redis, TTL configurable |

### 9.5 Mantenibilidad

| Aspecto | Evaluación |
|---------|-----------|
| **Estructura de carpetas** | Excelente — capas hexagonales claras |
| **Separación de responsabilidades** | Buena en capas, pero `main.py` tiene 4000+ líneas mezclando routing y lógica |
| **Testing** | 28 tests backend (pytest + cov), vitest frontend, k6 load tests |
| **CI/CD** | Linting (flake8, mypy, isort, ESLint), testing, build, deploy automatizado |
| **Documentación de API** | Swagger/OpenAPI automático en `/docs` |
| **Versionado** | No hay lock file para backend (requirements.txt sin hashes) |

---

## 10. Decisiones Arquitectónicas (ADRs)

### ADR-001: Arquitectura Hexagonal (Puertos y Adaptadores)

**Contexto:** Se necesita un backend que permita intercambiar implementaciones de infraestructura sin afectar la lógica de negocio.  
**Decisión:** Implementar Puertos y Adaptadores con capas `domain/`, `application/`, `infrastructure/`.  
**Consecuencias:** + Mantenibilidad, + Testeabilidad, − Complejidad inicial, + Flexibilidad para cambiar DBs.

### ADR-002: Monolito Modular (no Microservicios)

**Contexto:** El proyecto es una plataforma educativa con módulos internos bien definidos.  
**Decisión:** Mantener un solo proceso FastAPI con módulos internos (`ml/`, `analytics/`, `services/`).  
**Consecuencias:** + Simplicidad de deploy, + Consistencia transaccional, − Escalabilidad limitada, pero los módulos están preparados para ser extraídos (facilidad futura de migración a microservicios).

### ADR-003: Bases de Datos Políglota

**Contexto:** Diferentes tipos de datos requieren diferentes modelos de almacenamiento.  
**Decisión:** PostgreSQL para datos transaccionales + pgvector para embeddings, MongoDB para eventos/analítica, Redis para caché.  
**Consecuencias:** + Cada DB optimizada para su carga de trabajo, − Complejidad operativa, + pgvector permite RAG sin infraestructura adicional.

### ADR-004: IA Híbrida (Local + Cloud)

**Contexto:** Se necesita IA para tutor, chatbot, RAG y generación de ejercicios, con restricciones de costo y disponibilidad.  
**Decisión:** Ollama (local, primario) → OpenAI (cloud, fallback) → IntelligentTutor (reglas, último recurso).  
**Consecuencias:** + Resiliencia (4 niveles de fallback), − Mantenimiento de múltiples proveedores, + Privacidad (datos no salen del servidor si Ollama funciona).

### ADR-005: No ORM — SQL Crudo

**Contexto:** El equipo quiere control total sobre las consultas SQL.  
**Decisión:** Usar psycopg2 con SQL directo en lugar de SQLAlchemy u otro ORM.  
**Consecuencias:** + Rendimiento óptimo, + Control total, − Mayor riesgo de SQL injection, − Más código boilerplate, − Sin migraciones automáticas.

### ADR-006: Lazy Imports para ML

**Contexto:** scikit-learn, numpy y pandas son pesados (lentos de importar).  
**Decisión:** Usar proxies lazy (`_LazyAI`, `_LazyMLOrchestrator`) en `dependencies.py` y cargar analytics_router dentro del lifespan.  
**Consecuencias:** + Arranque rápido, − Complejidad de código, − Mensajes de error diferidos si faltan dependencias.

### ADR-007: JWT con Fallback de Algoritmo

**Contexto:** Soporte para HS256 y RS256.  
**Decisión:** `_decode_token_fallback` prueba RS256 luego HS256 secuencialmente hasta que uno funciona.  
**Consecuencias:** + Flexibilidad, ⚠️ Riesgo de algorithm confusion (parcialmente mitigado por orden de pruebas, pero la falla podría permitir ataques si la clave pública se conoce).

### ADR-008: Sandbox con Contenedores Docker

**Contexto:** Ejecución segura de código de estudiantes.  
**Decisión:** Contenedores Docker efímeros con restricciones estrictas (sin red, solo lectura, 64MB RAM, 0.5 CPU).  
**Consecuencias:** + Aislamiento real (no confiar solo en blacklist AST), − Dependencia de Docker daemon, − Latencia de creación de contenedores.

---

## 11. Deuda Técnica y Riesgos

### 11.1 Deuda Técnica Identificada

| ID | Deuda | Impacto | Esfuerzo Estimado |
|----|-------|---------|-------------------|
| TD1 | **main.py con 4000+ líneas** — mezcla routing, lógica de negocio, consultas SQL inline | Mantenibilidad baja, testing difícil | 3-5 días (refactor a routers separados) |
| TD2 | **Sin ORM/ODM** — SQL crudo y PyMongo directo en toda la app | Mayor riesgo de errores, sin migraciones | 5-10 días (migrar a SQLAlchemy + Beanie) |
| TD3 | **Lesson sin entidad formal** — se maneja como dict en SQL | Rompe el modelo de dominio DDD | 0.5 días (crear entidad Lesson) |
| TD4 | **Class sin entidad formal** — se maneja completamente en SQL y main.py | Rompe el modelo de dominio DDD | 1 día (crear entidad Class) |
| TD5 | **Sin lock file Python** — requirements.txt sin hashes | Vulnerabilidad de supply chain | 0.5 días (pip freeze + hashes) |
| TD6 | **Sin separación dev/prod deps** — backend no tiene requirements-dev.txt | Paquetes de test en producción | 0.5 días |
| TD7 | **Sin TLS/HTTPS configurado** — no hay proxy reverso en docker-compose | Riesgo de seguridad | 2 días (Caddy/nginx) |
| TD8 | **JWT_SECRET compartido** — frontend y backend usan la misma clave | Riesgo de seguridad si frontend es comprometido | 1 día (RS256 o claves separadas) |
| TD9 | **exec() con blacklist de strings** en sandbox_service.py | RCE potencial si se bypassea la blacklist | 2 días (usar CodeExecutor Docker siempre) |
| TD10 | **Fire-and-forget sin manejo de errores** — `asyncio.create_task` sin try/except | Excepciones silenciosas, datos perdidos | 1 día (wrappers con logging) |
| TD11 | **Numpy lazy import frágil** — si numpy falla, analytics_router no se registra y no hay feedback | Degradación silenciosa | 0.5 días (try/except visible) |
| TD12 | **test_debug.txt residual** en backend/app/ | Artefacto de desarrollo en producción | 0.1 días |

### 11.2 Riesgos Arquitectónicos

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|----|--------|------------|---------|------------|
| R1 | **CVE-2024-33663** python-jose 3.3.0 | Alta | Crítico | Actualizar a ≥3.4.0 |
| R2 | **CVE-2026-44581** Next.js 16.2.4 | Alta | Alto | Actualizar a ≥16.2.5 |
| R3 | **exec() sandbox bypasseable** | Media | Crítico | Usar siempre contenedor Docker |
| R4 | **PostgreSQL single point of failure** | Baja | Crítico | Configurar réplicas |
| R5 | **Dependencia de Docker daemon** | Media | Alto | Validar al iniciar, fallback graceful |
| R6 | **Modelos ML no entrenados** | Alta | Medio | Incluir modelos por defecto en repo |
| R7 | **Sin healthcheck en frontend** | Baja | Medio | Agregar healthcheck en Dockerfile |
| R8 | **CORS misconfigurado en producción** | Media | Medio | Validar orígenes en settings |

---

## 12. Recomendaciones

### Prioritarias (Seguridad)

1. **Actualizar python-jose** de 3.3.0 a ≥3.4.0 (corrige CVE-2024-33663, CVSS 9.3)
2. **Actualizar Next.js** de 16.2.4 a ≥16.2.5 (corrige CVE-2026-44581)
3. **Reemplazar exec() por CodeExecutor Docker** — eliminar la blacklist de strings, usar siempre sandbox Docker
4. **Separar JWT_SECRET** entre frontend y backend — idealmente migrar a RS256
5. **Agregar TLS/HTTPS** — nginx o Caddy como proxy reverso con Let's Encrypt

### Arquitectónicas

6. **Refactorizar main.py** — dividir en routers separados por dominio (auth, users, modules, exercises, classes, challenges, analytics)
7. **Formalizar entidades faltantes** — crear `Lesson` y `Class` como entidades de dominio con sus puertos
8. **Agregar event bus ligero** — Redis Streams o RabbitMQ para notificaciones y actualización de métricas en lugar de `asyncio.create_task`
9. **Centralizar manejo de errores** — evitar `raise HTTPException` esparcido en main.py, usar casos de uso con tipos Result
10. **Agregar healthcheck al frontend** en docker-compose

### Operacionales

11. **Generar lock file** para backend (`pip freeze > requirements-lock.txt` con hashes)
12. **Separar dependencias dev/prod** del backend
13. **Agregar modelos ML por defecto** al repositorio (o generarlos en el build de Docker)
14. **Configurar monitoreo** — logs estructurados (JSON), métricas de aplicación (Prometheus), dashboards (Grafana)
15. **Agregar migraciones de BD** — Alembic o similar para control de versiones de esquema

### A Largo Plazo

16. **Evaluar extracción de módulos** — `ml/` y `analytics/` son candidatos naturales a microservicios
17. **Migrar de python-jose a PyJWT** — python-jose no recibe mantenimiento activo
18. **Evaluar GraphQL** para el frontend — muchos endpoints podrían consolidarse
19. **Agregar feature flags** para despliegues canary y pruebas A/B
20. **Evaluar迁移 a Kubernetes** si la escala lo requiere (actualmente Docker Compose es adecuado)

---

## Resumen de Métricas Arquitectónicas

| Métrica | Valor |
|---------|-------|
| **Líneas de código backend** | ~10,000+ (estimado, excluyendo scripts SQL/JS) |
| **Líneas de código frontend** | ~8,000+ (estimado, incluyendo componentes) |
| **Archivos de código fuente** | ~90+ backend, ~60+ frontend, ~15 ML pipeline |
| **Endpoints REST** | 144 |
| **Puertos (interfaces)** | 5 |
| **Adaptadores** | 9 (4 Postgres + 2 Mongo + 2 Redis + 1 Docker) |
| **Casos de uso formales** | 5 |
| **Servicios de aplicación** | 9 |
| **Modelos ML** | 6 (4 supervisados + 2 no supervisados) |
| **Bases de datos** | 3 (PostgreSQL + MongoDB + Redis) |
| **Servicios Docker** | 6 |
| **Contenedores en producción** | 6 |
| **Redes Docker** | 3 |
| **Volúmenes persistentes** | 4 |
| **APIs externas** | 3 (Dialogflow, OpenAI, Docker Hub) |
| **% Cobertura de tests backend** | ~70-80% (estimado, 28 tests con cov) |
| **Vulnerabilidades críticas** | 1 (python-jose) |
| **Vulnerabilidades altas** | 1-2 (Next.js) |

---

*Fin del reporte de Reconstrucción Arquitectónica.*
