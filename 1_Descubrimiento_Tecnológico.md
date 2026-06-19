# Auditoría de Software — Descubrimiento Tecnológico

**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Auditor:** Asistente de IA (análisis automatizado)  
**Propósito:** Identificar todas las tecnologías utilizadas en el proyecto sin asumir previamente ningún lenguaje o framework.

---

## Metodología

Se realizó un recorrido completo de la estructura del proyecto, analizando:

- Archivos de configuración (`package.json`, `requirements.txt`, `tsconfig.json`, `docker-compose.yml`, `next.config.mjs`, `Dockerfile`)
- Código fuente del backend (FastAPI, arquitectura hexagonal)
- Código fuente del frontend (Next.js, React, componentes)
- Pipeline de ML (`ml_pipeline/`)
- Scripts de inicialización de bases de datos
- Archivos de CI/CD (GitHub Actions)
- Pruebas de carga (k6)
- Variables de entorno (`.env.example`)

---

## Resultados

### 1. Lenguajes de Programación

| Lenguaje | Ubicación | Versión | Evidencia |
|----------|-----------|---------|-----------|
| Python | `backend/`, `ml_pipeline/` | 3.11 | `backend/Dockerfile` → `FROM python:3.11-slim` |
| TypeScript | `frontend/` | 5.7.3 | `frontend/package.json` → `"typescript": "5.7.3"` |
| JavaScript | `frontend/` | ES6+ | `frontend/tsconfig.json` → `"target": "ES6"` |
| SQL (PL/pgSQL) | `backend/scripts/*.sql` | PostgreSQL 16 | `backend/scripts/001-init.sql` → funciones y procedimientos almacenados |
| Shell | `.github/workflows/`, Dockerfiles | bash/sh | Scripts en CI/CD y entrypoints |

### 2. Frameworks

| Framework | Tipo | Versión | Evidencia |
|-----------|------|---------|-----------|
| FastAPI | Backend web | 0.109.0 | `backend/requirements.txt` → `fastapi==0.109.0` |
| Next.js | Frontend (React SSR) | 16.2.4 | `frontend/package.json` → `"next": "^16.2.4"` |
| React | UI (Frontend) | 19.2.4 | `frontend/package.json` → `"react": "19.2.4"` |
| Uvicorn | ASGI Server | 0.27.0 | `backend/requirements.txt` → `uvicorn[standard]==0.27.0` |

### 3. Tecnologías Backend

| Tecnología | Propósito | Evidencia |
|------------|-----------|-----------|
| FastAPI 0.109 | Framework REST API | `backend/requirements.txt`, `backend/app/main.py` línea 76 |
| Pydantic 2.5 | Validación de datos/schemas | `backend/requirements.txt` → `pydantic==2.5.0` |
| Pydantic-Settings 2.1 | Configuración por variables de entorno | `backend/config/settings.py` línea 1 |
| PyMongo 4.6 | Driver MongoDB | `backend/requirements.txt` → `pymongo==4.6.0` |
| psycopg2-binary 2.9 | Driver PostgreSQL | `backend/requirements.txt` → `psycopg2-binary==2.9.9` |
| Redis + hiredis 5.1 | Caché y rate limiting | `backend/requirements.txt` → `redis[hiredis]==5.1.0` |
| python-jose 3.3 | JWT | `backend/requirements.txt` → `python-jose[cryptography]==3.3.0` |
| bcrypt 3.2 | Hashing de contraseñas | `backend/requirements.txt` → `bcrypt==3.2.0` |
| APScheduler 3.10 | Tareas programadas | `backend/requirements.txt` → `apscheduler==3.10.4` |
| httpx 0.27 | Cliente HTTP asíncrono | `backend/requirements.txt` → `httpx==0.27.0` |
| Docker SDK 7.1 | Interacción con Docker desde Python | `backend/requirements.txt` → `docker==7.1.0` |
| OpenAPI (auto) | Documentación Swagger | `docker-compose.yml` línea 83 → `/docs` |

### 4. Tecnologías Frontend

| Tecnología | Propósito | Evidencia |
|------------|-----------|-----------|
| Next.js 16.2.4 | Framework React SSR + App Router | `frontend/package.json` |
| React 19.2.4 | Librería UI | `frontend/package.json` |
| TypeScript 5.7 | Tipado estático | `frontend/tsconfig.json` |
| Tailwind CSS 4.2 | Framework CSS utility-first | `frontend/postcss.config.mjs` |
| shadcn/ui | Componentes UI reutilizables | `frontend/components.json` → `"style": "new-york"` |
| Radix UI | Primitivas UI accesibles (13 paquetes) | `frontend/package.json` → `@radix-ui/*` |
| lucide-react | Iconos SVG | `frontend/package.json` |
| recharts 2.15 | Gráficos y visualizaciones | `frontend/package.json` |
| react-hook-form 7.54 | Manejo de formularios | `frontend/package.json` |
| zod 3.24 | Validación de esquemas | `frontend/package.json` |
| sonner 1.7 | Notificaciones toast | `frontend/package.json` |
| date-fns 4.1 | Manipulación de fechas | `frontend/package.json` |
| clsx + tailwind-merge | Gestión de clases CSS | `frontend/lib/utils.ts` |
| class-variance-authority | Variantes de componentes | `frontend/package.json` |
| next-themes 0.4 | Modo oscuro/claro | `frontend/package.json` |
| CodeMirror | Editor de código | `frontend/package.json` → `@uiw/react-codemirror` |
| react-markdown + remark-gfm | Renderizado Markdown | `frontend/package.json` |
| react-syntax-highlighter | Resaltado de sintaxis | `frontend/package.json` |
| tw-animate-css | Animaciones CSS | `frontend/package.json` (dev) |
| @vercel/analytics 1.6 | Analytics de Vercel | `frontend/package.json`, `app/layout.tsx` línea 48 |

### 5. Bases de Datos

| Base de Datos | Versión | Propósito | Evidencia |
|---------------|---------|-----------|-----------|
| PostgreSQL | 16 (pgvector) | Datos principales (usuarios, módulos, ejercicios, progreso) | `docker-compose.yml` línea 6 → `pgvector/pgvector:pg16` |
| MongoDB | 7 | Eventos, logs, analítica conductual, interacciones tutor | `docker-compose.yml` línea 33 → `mongo:7` |
| Redis | 7 Alpine | Caché de IA, rate limiting, sesiones | `docker-compose.yml` línea 58 → `redis:7-alpine` |
| pgvector | Extensión PostgreSQL | Embeddings vectoriales para RAG | `backend/scripts/005-enable-pgvector.sql` |

### 6. Herramientas DevOps

| Herramienta | Propósito | Evidencia |
|-------------|-----------|-----------|
| Docker Compose | Orquestación multi-contenedor (8 servicios) | `docker-compose.yml` |
| Docker | Contenedores para cada servicio | `backend/Dockerfile`, `frontend/Dockerfile` |
| GitHub Actions | CI/CD automatizado | `.github/workflows/ci.yml`, `.github/workflows/deploy.yml` |
| Docker Buildx | Build multi-plataforma | `.github/workflows/ci.yml` línea 192 |
| flake8 | Linter Python | `.github/workflows/ci.yml` línea 33 |
| mypy | Type checker Python | `.github/workflows/ci.yml` línea 37 |
| isort | Ordenamiento de imports Python | `.github/workflows/ci.yml` línea 42 |
| pytest + pytest-cov | Testing Python + cobertura | `.github/workflows/ci.yml` línea 119 |
| ESLint (Next) | Linter TypeScript/JS | `.github/workflows/ci.yml` línea 153 → `npm run lint` |
| vitest | Testing frontend | `frontend/package.json` → `"test": "vitest run"` |
| k6 | Pruebas de carga | `tests/load/k6-load-test.js` |
| Cypress | Pruebas E2E (referenciado) | Directorio `cypress/` en raíz |
| docker/login-action | Login a Docker Hub | `.github/workflows/deploy.yml` línea 19 |
| appleboy/ssh-action | SSH a VPS para deploy | `.github/workflows/deploy.yml` línea 40 |

### 7. Servicios Externos

| Servicio | Propósito | Evidencia |
|----------|-----------|-----------|
| Dialogflow (Google Cloud) | Chatbot conversacional | `backend/.env.example` → `DIALOGFLOW_PROJECT_ID`, `backend/app/main.py` línea 932 |
| OpenAI | Fallback de IA cuando Ollama no responde | `backend/.env.example` → `OPENAI_API_KEY`, `backend/app/main.py` línea 1040 |
| Ollama + Qwen2.5-Coder 1.5B | LLM local para tutor, RAG, generación | `docker-compose.yml` línea 91 |
| Docker Hub | Registro de imágenes | `.github/workflows/deploy.yml` línea 19 |
| codecov/codecov-action | Reporte de cobertura | `.github/workflows/ci.yml` línea 129 |
| Vercel Analytics | Analytics del frontend | `frontend/package.json` línea 35 |

### 8. Sistema de Autenticación

| Componente | Tecnología | Evidencia |
|------------|------------|-----------|
| Algoritmo JWT | HS256 (por defecto), RS256 (opcional) | `docker-compose.yml` línea 109 → `ALGORITHM: HS256` |
| Librería JWT (backend) | python-jose[cryptography] 3.3 | `backend/requirements.txt` |
| Librería JWT (frontend) | jose 6.2 | `frontend/package.json` línea 39 |
| Hashing | bcrypt 3.2 | `backend/requirements.txt`, `backend/app/main.py` línea 205 |
| Transporte de token | HTTP-only cookie (`auth-token`) | `backend/app/main.py` línea 178, `frontend/proxy.ts` |
| Middleware frontend | Next.js Middleware (proxy.ts) | `frontend/proxy.ts` → verifica JWT en cada ruta protegida |
| Roles | student, teacher, admin | `backend/scripts/001-init.sql` línea 24 |
| Expiración | 7 días (configurable) | `docker-compose.yml` línea 110 → `ACCESS_TOKEN_EXPIRE_MINUTES: 10080` |

### 9. Sistema de Despliegue

| Componente | Tecnología | Evidencia |
|------------|------------|-----------|
| Contenedores | Docker Compose (6 servicios + 3 volúmenes + 3 redes) | `docker-compose.yml` |
| Registro de imágenes | Docker Hub | `.github/workflows/deploy.yml` línea 19-23 |
| Orquestación | docker-compose up -d --force-recreate | `.github/workflows/deploy.yml` línea 49 |
| Destino | VPS (Servidor Linux) vía SSH | `.github/workflows/deploy.yml` línea 40-49 |
| Estrategia | Blue-green (pull + force-recreate) | `.github/workflows/deploy.yml` línea 49 |
| CI automático | Push a `main` o `develop` | `.github/workflows/ci.yml` línea 4-5 |
| CD automático | Push a `main` | `.github/workflows/deploy.yml` línea 4-5 |
| Redes Docker | frontend_net, internal_net (interna), ai_net | `docker-compose.yml` líneas 182-191 |

### 10. Inteligencia Artificial / Machine Learning

| Componente | Tecnología | Evidencia |
|------------|------------|-----------|
| LLM Local | Ollama + qwen2.5-coder:1.5b | `docker-compose.yml` línea 91 |
| Chatbot | Dialogflow CX (Google) | `backend/app/main.py` línea 932 |
| RAG (Retrieval Augmented Generation) | pgvector + embeddings | `backend/scripts/005-enable-pgvector.sql`, `backend/application/services/rag_service.py` |
| Embeddings | OpenAI / Ollama | `backend/application/services/embedding_service.py` |
| Tutor Inteligente | Sistema híbrido (reglas + LLM) | `backend/application/services/intelligent_tutor.py` |
| Predicción de Engagement | RandomForestRegressor + scikit-learn | `ml_pipeline/src/models.py` líneas 38-47 |
| Predicción de Rendimiento | RandomForestRegressor | `ml_pipeline/src/models.py` líneas 50-59 |
| Predicción de Abandono | RandomForestClassifier (balanceado) | `ml_pipeline/src/models.py` líneas 62-72 |
| Predicción de Frustración | RandomForestClassifier (balanceado) | `ml_pipeline/src/models.py` líneas 75-85 |
| Clustering de Estudiantes | KMeans (4 clusters) + PCA | `ml_pipeline/04_train_unsupervised.py` líneas 70-78 |
| Detección de Anomalías | IsolationForest | `ml_pipeline/04_train_unsupervised.py` líneas 90-104 |
| Recomendador | ML + reglas de negocio | `backend/application/services/ml/recommender.py` |
| Generación de Ejercicios | IA + plantillas | `backend/application/services/exercise_generator_service.py` |
| Sandbox de Código | exec() seguro con AST validation | `backend/app/main.py` líneas 1110-1198 |

### 11. Arquitectura

| Aspecto | Detalle | Evidencia |
|---------|---------|-----------|
| Patrón arquitectónico | Hexagonal (Puertos y Adaptadores) | `backend/domain/ports/`, `backend/infrastructure/adapters/` |
| Separación en capas | domain, application, infrastructure, config | Estructura de `backend/` |
| DTOs/Schemas | Pydantic v2 | `backend/app/schemas/` (9 archivos) |
| Casos de uso | Use Cases separados | `backend/application/useCases/` (5 archivos) |

---

## Conclusión Técnica

**RoboLearn** es una plataforma educativa full-stack para la enseñanza de programación y robótica, construida sobre un stack moderno y bien estructurado.

### Stack Principal
- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind 4 + shadcn/ui, con editor de código embebido (CodeMirror), gráficos (recharts), y soporte de temas claro/oscuro.
- **Backend**: FastAPI con arquitectura hexagonal (Puertos y Adaptadores), validación con Pydantic v2, autenticación JWT (HS256/RS256) con bcrypt y cookies HTTP-only.
- **Bases de datos**: Políglota — PostgreSQL 16 con pgvector (datos transaccionales + embeddings), MongoDB 7 (eventos/analítica), Redis 7 (caché).

### Inteligencia Artificial (Diferenciador clave)
El proyecto integra un ecosistema de IA notablemente completo:
- **Chatbot híbrido** con Dialogflow como primera opción y Ollama (Qwen2.5-Coder 1.5B local) + OpenAI como fallbacks.
- **Tutor inteligente** que adapta explicaciones según el nivel del estudiante.
- **RAG** (Retrieval Augmented Generation) con pgvector para consultas contextuales.
- **ML Pipeline** completo con 4 modelos supervisados (RandomForest para engagement, rendimiento, abandono y frustración) y 2 no supervisados (KMeans para segmentación, IsolationForest para detección de anomalías).
- **Analítica predictiva** para docentes con dashboard de riesgo de abandono, factores de frustración y compromiso.

### DevOps y Despliegue
- CI/CD completo con GitHub Actions: linting (flake8, mypy, ESLint), tests (pytest + vitest), build de imágenes Docker, y deploy automatizado a VPS vía SSH.
- Docker Compose con 6 contenedores, redes separadas (interna para DBs, AI, frontend) y healthchecks.

### Seguridad
- JWT con soporte HS256 y RS256.
- Middleware de seguridad con headers (CSP, HSTS, XSS, CORS).
- Sandbox de ejecución de código con AST validation y listas negras de módulos peligrosos.
- Auditoría de endpoints sensibles.
- Cookies HTTP-only y SameSite Lax.

### Puntos de Atención (Hallazgos Iniciales)
1. **JWT_SECRET compartido** entre backend y frontend (`docker-compose.yml` línea 167) — riesgo de seguridad.
2. **exec() para sandbox** de código (`backend/app/main.py` línea 1177) — la seguridad es frágil, lista negra de patrones es evitable.
3. **Fire-and-forget asyncio.create_task** en varios puntos — sin manejo de errores ni reintentos.
4. **No se observan pruebas de carga para la IA** — el k6 test solo cubre endpoints REST básicos.
5. **La pipeline de ML usa datos sintéticos** — válido para desarrollo, pero requiere datos reales para producción.
6. **No se observa TLS/HTTPS configurado** en docker-compose o los middlewares.

### Madurez del Proyecto
El proyecto muestra un nivel avanzado de ingeniería de software: arquitectura limpia, separación de responsabilidades, testing extenso (28 archivos de test en backend), CI/CD automatizado, y una integración sofisticada de IA. Es un proyecto listo para escalar a producción con las mitigaciones de seguridad adecuadas.

---

*Fin del reporte de Descubrimiento Tecnológico.*
