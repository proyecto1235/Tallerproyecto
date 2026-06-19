# Auditoría de Software — Variables de Entorno y Configuración

**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Auditor:** Asistente de IA (análisis automatizado)  
**Propósito:** Inventario completo de variables de entorno, secretos, tokens y configuraciones.

---

## Archivos de Configuración Encontrados

| Archivo | Ubicación | Tipo | Propósito |
|---------|-----------|------|-----------|
| `.env.example` | `./` | Variables de entorno | Plantilla para desarrollo (84 líneas) |
| `settings.py` | `backend/config/` | Pydantic Settings | Validación + defaults de todas las variables |
| `database_init.py` | `backend/config/` | Inicialización | Creación automática de BD y tablas |
| `docker-compose.yml` | `./` | Docker Compose | Orquestación de 6 servicios (191 líneas) |
| `next.config.mjs` | `frontend/` | Next.js | Configuración del framework frontend |
| `tsconfig.json` | `frontend/` | TypeScript | Compilación y paths |
| `postcss.config.mjs` | `frontend/` | PostCSS | Procesamiento CSS (Tailwind) |
| `components.json` | `frontend/` | shadcn/ui | Configuración de componentes UI |
| `logging_config.py` | `backend/app/` | Logging | Formato y handlers de logs |
| `Dockerfile` | `backend/` | Docker | Build de imagen backend |
| `Dockerfile` | `frontend/` | Docker | Build de imagen frontend |
| `ci.yml` | `.github/workflows/` | GitHub Actions | Pipeline CI (206 líneas) |
| `deploy.yml` | `.github/workflows/` | GitHub Actions | Pipeline CD (50 líneas) |
| `.gitignore` | `./` | Git | Exclusiones del repositorio (119 líneas) |

---

## Inventario Completo de Variables de Entorno

### A. Backend — App / Generales

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `APP_NAME` | No | string | Nombre de la aplicación | `Robolearn API` | `.env.example` l.10, `settings.py` l.14 |
| `APP_ENV` | No | string | Entorno de ejecución | `development` | `.env.example` l.11, `settings.py` l.17 |
| `DEBUG` | No | bool | Modo debug | `True` | `.env.example` l.12, `settings.py` l.16 |
| `APP_VERSION` | No | string | Versión de la API | `1.0.0` | `settings.py` l.15 (default) |
| `NODE_ENV` | No | string | Entorno Node (para middleware) | `development` | `settings.py` l.24 |

### B. Backend — Seguridad / JWT

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `SECRET_KEY` | **SÍ** | string | 🔴 Clave secreta para firmar JWT | `changeme-para-produccion-robolearn` | `.env.example` l.15, `settings.py` l.19 |
| `ALGORITHM` | No | string | Algoritmo JWT (HS256 o RS256) | `HS256` | `.env.example` l.16, `settings.py` l.20 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | int | Minutos de expiración del token | `10080` (7 días) | `.env.example` l.17, `settings.py` l.21 |
| `JWT_PRIVATE_KEY` | No | string | 🔴 Clave privada RSA (para RS256) | *(contenido PEM)* | `.env.example` l.22, `settings.py` l.23 |
| `JWT_PUBLIC_KEY` | No | string | 🔴 Clave pública RSA (para RS256) | *(contenido PEM)* | `.env.example` l.23, `settings.py` l.22 |

### C. Backend — PostgreSQL

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `POSTGRES_USER` | **SÍ** | string | Usuario de PostgreSQL | `postgres` | `.env.example` l.28, `settings.py` l.27 |
| `POSTGRES_PASSWORD` | **SÍ** | string | 🔴 Contraseña de PostgreSQL | `robolearn_dev` | `.env.example` l.29, `settings.py` l.28 |
| `POSTGRES_HOST` | **SÍ** | string | Host de PostgreSQL | `localhost` (local) / `postgres` (Docker) | `.env.example` l.30, `settings.py` l.29 |
| `POSTGRES_PORT` | **SÍ** | int | Puerto de PostgreSQL | `5432` | `.env.example` l.31, `settings.py` l.30 |
| `POSTGRES_DB` | **SÍ** | string | Nombre de la base de datos | `robolearn` | `.env.example` l.32, `settings.py` l.31 |
| `DB_POOL_MIN` | No | int | Pool mínimo de conexiones | `5` | `.env.example` l.33, `settings.py` l.32 |
| `DB_POOL_MAX` | No | int | Pool máximo de conexiones | `50` | `.env.example` l.34, `settings.py` l.33 |

### D. Backend — MongoDB

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `MONGODB_URL` | **SÍ** | string | URL de conexión MongoDB | `mongodb://localhost:27017` | `.env.example` l.39, `settings.py` l.36 |
| `MONGODB_DB` | **SÍ** | string | Nombre de la base MongoDB | `robolearn_metrics` | `.env.example` l.40, `settings.py` l.37 |

### E. Backend — Redis

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `REDIS_URL` | **SÍ** | string | URL de conexión Redis | `redis://localhost:6379/0` | `.env.example` l.45, `settings.py` l.44 |
| `REDIS_PASSWORD` | No | string | 🔴 Contraseña de Redis | *(vacío en desarrollo)* | `docker-compose.yml` l.64 |

### F. Backend — Ollama (IA Local)

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `OLLAMA_URL` | No | string | URL del servidor Ollama | `http://localhost:11434` | `.env.example` l.50, `settings.py` l.47 |
| `OLLAMA_MODEL` | No | string | Modelo de Ollama a usar | `qwen2.5-coder:1.5b` | `.env.example` l.51, `settings.py` l.48 |

### G. Backend — OpenAI (Fallback Opcional)

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `OPENAI_API_KEY` | No | string | 🔴 API Key de OpenAI (fallback) | *(vacío — opcional)* | `.env.example` l.56, `settings.py` l.51 |
| `OPENAI_MODEL` | No | string | Modelo OpenAI a usar | `gpt-3.5-turbo` | `.env.example` l.57, `settings.py` l.52 |

### H. Backend — Dialogflow (Chatbot Opcional)

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `DIALOGFLOW_PROJECT_ID` | No | string | 🔴 ID del proyecto Google Cloud | *(vacío — opcional)* | `.env.example` l.62, `settings.py` l.40 |
| `DIALOGFLOW_AGENT_ID` | No | string | 🔴 ID del agente Dialogflow | *(vacío — opcional)* | `.env.example` l.63 |
| `GOOGLE_CREDENTIALS_PATH` | No | string | 🔴 Ruta al JSON de credenciales GCP | `backend/robolearn-key.json` | `.env.example` l.64, `settings.py` l.41 |

### I. Backend — ML / CORS

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `ML_MODEL_DIR` | No | string | Directorio de modelos ML | `models` | `.env.example` l.69, `settings.py` l.54 |
| `CORS_ORIGINS` | No | list | Orígenes permitidos CORS | `["http://localhost:3000","http://localhost:8000"]` | `.env.example` l.74, `settings.py` l.56 |

### J. Docker Compose — Puertos Externos

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `POSTGRES_PORT_EXTERNAL` | No | string | Puerto PostgreSQL externo | `127.0.0.1:5432` | `docker-compose.yml` l.13 |
| `MONGO_PORT_EXTERNAL` | No | string | Puerto MongoDB externo | `127.0.0.1:27017` | `docker-compose.yml` l.40 |
| `REDIS_PORT_EXTERNAL` | No | string | Puerto Redis externo | `127.0.0.1:6379` | `docker-compose.yml` l.61 |
| `OLLAMA_PORT_EXTERNAL` | No | string | Puerto Ollama externo | `127.0.0.1:11434` | `docker-compose.yml` l.81 |
| `BACKEND_PORT_EXTERNAL` | No | string | Puerto Backend externo | `127.0.0.1:8000` | `docker-compose.yml` l.133 |
| `FRONTEND_PORT_EXTERNAL` | No | string | Puerto Frontend externo | `127.0.0.1:3000` | `docker-compose.yml` l.169 |

### K. Docker Compose — MongoDB / Redis

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `MONGO_USER` | No | string | Usuario root MongoDB | `admin` | `docker-compose.yml` l.36 |
| `MONGO_PASSWORD` | No | string | 🔴 Contraseña root MongoDB | `robolearn_dev` | `docker-compose.yml` l.37 |
| `MONGO_DB` | No | string | Base de datos MongoDB | `robolearn_metrics` | `docker-compose.yml` l.38 |

### L. Frontend — Next.js

| Variable | Obligatoria | Tipo | Descripción | Valor de Ejemplo | Fuente |
|----------|-------------|------|-------------|-------------------|--------|
| `NEXT_PUBLIC_API_URL` | **SÍ** | string | URL de la API backend (pública) | `http://localhost:8000/api` | `.env.example` l.79, `docker-compose.yml` l.164 |
| `NEXT_PUBLIC_BACKEND_URL` | **SÍ** | string | URL base del backend (pública) | `http://localhost:8000` | `.env.example` l.80, `docker-compose.yml` l.165 |
| `NEXT_PUBLIC_JWT_EXPIRATION_DAYS` | No | int | Días de expiración JWT (frontend) | `7` | `.env.example` l.81, `docker-compose.yml` l.166 |
| `JWT_SECRET` | **SÍ** | string | 🔴 Clave JWT (debe coincidir con backend SECRET_KEY) | `changeme-para-produccion-robolearn` | `.env.example` l.84, `docker-compose.yml` l.167 |

---

## Tabla Maestra de Variables

| # | Variable | Obligatoria | Secreto | Categoría | Valor por Defecto | Fuentes |
|---|----------|-------------|---------|-----------|-------------------|---------|
| 1 | `APP_NAME` | ❌ No | ❌ | App | `Robolearn API` | .env, settings.py, compose |
| 2 | `APP_ENV` | ❌ No | ❌ | App | `development` | .env, settings.py, compose |
| 3 | `DEBUG` | ❌ No | ❌ | App | `True` | .env, settings.py, compose |
| 4 | `APP_VERSION` | ❌ No | ❌ | App | `1.0.0` | settings.py |
| 5 | `NODE_ENV` | ❌ No | ❌ | App | `development` | settings.py |
| 6 | `SECRET_KEY` | ✅ Sí | 🔴 | Seguridad | *(sin default seguro)* | .env, settings.py, compose |
| 7 | `ALGORITHM` | ❌ No | ❌ | Seguridad | `HS256` | .env, settings.py, compose |
| 8 | `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ No | ❌ | Seguridad | `10080` (7 días) | .env, settings.py, compose |
| 9 | `JWT_PRIVATE_KEY` | ❌ No | 🔴 | Seguridad | *(vacío)* | .env, settings.py |
| 10 | `JWT_PUBLIC_KEY` | ❌ No | 🔴 | Seguridad | *(vacío)* | .env, settings.py |
| 11 | `POSTGRES_USER` | ✅ Sí | ❌ | BD | `postgres` | .env, settings.py, compose |
| 12 | `POSTGRES_PASSWORD` | ✅ Sí | 🔴 | BD | *(sin default)* | .env, settings.py, compose |
| 13 | `POSTGRES_HOST` | ✅ Sí | ❌ | BD | `localhost` | .env, settings.py, compose |
| 14 | `POSTGRES_PORT` | ✅ Sí | ❌ | BD | `5432` | .env, settings.py, compose |
| 15 | `POSTGRES_DB` | ✅ Sí | ❌ | BD | `robolearn` | .env, settings.py, compose |
| 16 | `DB_POOL_MIN` | ❌ No | ❌ | BD | `5` | .env, settings.py |
| 17 | `DB_POOL_MAX` | ❌ No | ❌ | BD | `50` | .env, settings.py |
| 18 | `POSTGRES_PORT_EXTERNAL` | ❌ No | ❌ | BD (Docker) | `127.0.0.1:5432` | compose |
| 19 | `MONGODB_URL` | ✅ Sí | ❌ | BD | `mongodb://localhost:27017` | .env, settings.py, compose |
| 20 | `MONGODB_DB` | ✅ Sí | ❌ | BD | `robolearn_metrics` | .env, settings.py, compose |
| 21 | `MONGO_USER` | ❌ No | ❌ | BD (Docker) | `admin` | compose |
| 22 | `MONGO_PASSWORD` | ❌ No | 🔴 | BD (Docker) | `robolearn_dev` | compose |
| 23 | `MONGO_DB` | ❌ No | ❌ | BD (Docker) | `robolearn_metrics` | compose |
| 24 | `MONGO_PORT_EXTERNAL` | ❌ No | ❌ | BD (Docker) | `127.0.0.1:27017` | compose |
| 25 | `REDIS_URL` | ✅ Sí | ❌ | Cache | `redis://localhost:6379/0` | .env, settings.py, compose |
| 26 | `REDIS_PASSWORD` | ❌ No | 🔴 | Cache | *(vacío)* | .env, compose |
| 27 | `REDIS_PORT_EXTERNAL` | ❌ No | ❌ | Cache (Docker) | `127.0.0.1:6379` | compose |
| 28 | `OLLAMA_URL` | ❌ No | ❌ | IA Local | `http://localhost:11434` | .env, settings.py, compose |
| 29 | `OLLAMA_MODEL` | ❌ No | ❌ | IA Local | `qwen2.5-coder:1.5b` | .env, settings.py, compose |
| 30 | `OLLAMA_PORT_EXTERNAL` | ❌ No | ❌ | IA (Docker) | `127.0.0.1:11434` | compose |
| 31 | `OPENAI_API_KEY` | ❌ No | 🔴 | IA Fallback | *(vacío)* | .env, settings.py |
| 32 | `OPENAI_MODEL` | ❌ No | ❌ | IA Fallback | `gpt-3.5-turbo` | .env, settings.py |
| 33 | `DIALOGFLOW_PROJECT_ID` | ❌ No | 🔴 | Chatbot | *(vacío)* | .env, settings.py, compose |
| 34 | `DIALOGFLOW_AGENT_ID` | ❌ No | 🔴 | Chatbot | *(vacío)* | .env, compose |
| 35 | `GOOGLE_CREDENTIALS_PATH` | ❌ No | 🔴 | Chatbot | *(vacío)* | .env, settings.py, compose |
| 36 | `ML_MODEL_DIR` | ❌ No | ❌ | ML | `models` | .env, settings.py |
| 37 | `CORS_ORIGINS` | ❌ No | ❌ | Seguridad | `["http://localhost:3000","http://localhost:8000"]` | .env, settings.py, compose |
| 38 | `BACKEND_PORT_EXTERNAL` | ❌ No | ❌ | Docker | `127.0.0.1:8000` | compose |
| 39 | `FRONTEND_PORT_EXTERNAL` | ❌ No | ❌ | Docker | `127.0.0.1:3000` | compose |
| 40 | `NEXT_PUBLIC_API_URL` | ✅ Sí | ❌ | Frontend | `http://localhost:8000/api` | .env, compose |
| 41 | `NEXT_PUBLIC_BACKEND_URL` | ✅ Sí | ❌ | Frontend | `http://localhost:8000` | .env, compose |
| 42 | `NEXT_PUBLIC_JWT_EXPIRATION_DAYS` | ❌ No | ❌ | Frontend | `7` | .env, compose |
| 43 | `JWT_SECRET` | ✅ Sí | 🔴 | Frontend | *(igual que SECRET_KEY)* | .env, compose |

**Totales:** 43 variables | **14 obligatorias** | **14 secretos** | 5 categorías

---

## Secretos Identificados

| # | Secreto | Variable(s) | Riesgo si se expone | Mitigación |
|---|---------|-------------|---------------------|------------|
| 🔴 | **SECRET_KEY / JWT_SECRET** | `SECRET_KEY`, `JWT_SECRET` | Falsificación de tokens JWT — acceso total a la plataforma | Rotar en producción, usar RS256, no compartir entre frontend y backend |
| 🔴 | **Contraseña PostgreSQL** | `POSTGRES_PASSWORD` | Acceso a todos los datos del sistema (usuarios, progreso, ejercicios) | Usar contraseña fuerte, red interna aislada (`internal_net`) |
| 🔴 | **Contraseña MongoDB** | `MONGO_PASSWORD` | Acceso a eventos, analítica conductual, interacciones | Usar contraseña fuerte, red interna aislada |
| 🔴 | **API Key OpenAI** | `OPENAI_API_KEY` | Uso no autorizado de API OpenAI — costos inesperados | Mantener vacío si no se usa, rotar periódicamente |
| 🔴 | **Dialogflow / GCP** | `DIALOGFLOW_PROJECT_ID`, `DIALOGFLOW_AGENT_ID`, `GOOGLE_CREDENTIALS_PATH` | Acceso a agente GCP, posible escalada | Archivo JSON de credenciales fuera del repo (`.gitignore`) |
| 🔴 | **JWT Private Key** | `JWT_PRIVATE_KEY` | Falsificación de tokens (modo RS256) | Generar por separado, nunca comitear |
| 🟡 | **Redis Password** | `REDIS_PASSWORD` | Acceso a caché, posible manipulación de datos en caché | En desarrollo puede estar vacío, producción requiere contraseña |
| 🟡 | **Claves SSH (VPS)** | Secrets de GitHub (`VPS_SSH_KEY`) | Acceso completo al servidor de producción | Almacenar solo en GitHub Secrets, nunca en archivos |

---

## Configuración de Bases de Datos

### PostgreSQL 16 + pgvector

| Propiedad | Valor | Fuente de configuración |
|-----------|-------|------------------------|
| Imagen Docker | `pgvector/pgvector:pg16` | `docker-compose.yml` l.6 |
| Puerto interno | 5432 | `docker-compose.yml` l.13 |
| Puerto externo (default) | `127.0.0.1:5432` | `docker-compose.yml` l.13 (variable `POSTGRES_PORT_EXTERNAL`) |
| Base de datos | `robolearn` | `POSTGRES_DB` |
| Usuario | `postgres` | `POSTGRES_USER` |
| Pool de conexiones | min 5, max 50 | `DB_POOL_MIN`, `DB_POOL_MAX` |
| Extensión | `vector` (pgvector) | `backend/scripts/005-enable-pgvector.sql` |
| Inicialización | Scripts SQL montados en `/docker-entrypoint-initdb.d/` | `docker-compose.yml` l.16-19 |
| Healthcheck | `pg_isready -U postgres` cada 10s | `docker-compose.yml` l.21-24 |
| Persistencia | Volumen `postgres_data` | `docker-compose.yml` l.15 |
| Red | `internal_net` (aislada) | `docker-compose.yml` l.27 |
| Hostname en Docker | `postgres` | `docker-compose.yml` l.7 |

**Scripts de inicialización ejecutados en orden:**

1. `01-init.sql` → Schema (22 tablas, 8 stored procedures, 1 vista)
2. `02-seed.sql` → Datos base
3. `03-massive.sql` → Datos masivos de prueba (solo desarrollo)
4. `05-pgvector.sql` → Extensión vector + tabla `knowledge_chunks`

### MongoDB 7

| Propiedad | Valor | Fuente de configuración |
|-----------|-------|------------------------|
| Imagen Docker | `mongo:7` | `docker-compose.yml` l.33 |
| Puerto interno | 27017 | `docker-compose.yml` l.40 |
| Puerto externo (default) | `127.0.0.1:27017` | `docker-compose.yml` l.40 (variable `MONGO_PORT_EXTERNAL`) |
| Base de datos | `robolearn_metrics` | `MONGO_DB` |
| Usuario root | `admin` | `MONGO_USER` |
| Inicialización | Script JS montado en `/docker-entrypoint-initdb.d/` | `docker-compose.yml` l.43 |
| Healthcheck | `mongosh --eval 'db.runCommand({ ping: 1 })'` | `docker-compose.yml` l.46-49 |
| Persistencia | Volumen `mongo_data` | `docker-compose.yml` l.42 |
| Red | `internal_net` (aislada) | `docker-compose.yml` l.52 |

**Colecciones creadas (13):** `events`, `exercise_attempts`, `progress_snapshots`, `chat_interactions`, `sessions`, `session_metrics`, `behavioral_events`, `frustration_signals`, `code_analysis`, `engagement_scores`, `predictions`, `tutor_interactions`, `admin_stats`

### Redis 7

| Propiedad | Valor | Fuente de configuración |
|-----------|-------|------------------------|
| Imagen Docker | `redis:7-alpine` | `docker-compose.yml` l.58 |
| Puerto interno | 6379 | `docker-compose.yml` l.61 |
| Puerto externo (default) | `127.0.0.1:6379` | `docker-compose.yml` l.61 (variable `REDIS_PORT_EXTERNAL`) |
| Contraseña | Configurable via `REDIS_PASSWORD` | `docker-compose.yml` l.64 |
| Persistencia | AOF (Append Only File) | `docker-compose.yml` l.64 (`--appendonly yes`) |
| Healthcheck | `redis-cli -a <password> ping` | `docker-compose.yml` l.66-69 |
| Red | `internal_net` (aislada) | `docker-compose.yml` l.72 |

---

## Configuración de APIs Externas

### Ollama (IA Local)

| Propiedad | Valor |
|-----------|-------|
| URL interna (Docker) | `http://ollama:11434` |
| URL externa (local) | `http://localhost:11434` |
| Modelo | `qwen2.5-coder:1.5b` (2.5 GB aprox.) |
| Límite de memoria | 4 GB (Docker deploy) |
| Red | `ai_net` |
| Pull automático | Sí, en entrypoint del contenedor (`ollama pull qwen2.5-coder:1.5b`) |
| Propósito | Tutor inteligente, RAG, generación de ejercicios, fallback de chatbot |

### Dialogflow CX (Google Cloud — Opcional)

| Propiedad | Valor |
|-----------|-------|
| Project ID | `DIALOGFLOW_PROJECT_ID` |
| Agent ID | `DIALOGFLOW_AGENT_ID` |
| Credenciales | Archivo JSON en `/app/robolearn-key.json` (montado como volumen) |
| Propósito | Chatbot conversacional de primer nivel |
| Comportamiento si no configurado | Fallback automático a Ollama → IntelligentTutor |

### OpenAI (Fallback — Opcional)

| Propiedad | Valor |
|-----------|-------|
| API Key | `OPENAI_API_KEY` |
| Modelo | `gpt-3.5-turbo` |
| Propósito | Fallback de último nivel cuando Ollama y Dialogflow no responden |
| Comportamiento si no configurado | Se salta, usa IntelligentTutor basado en reglas |

### Vercel Analytics (Frontend)

| Propiedad | Valor |
|-----------|-------|
| Paquete | `@vercel/analytics` 1.6.1 |
| Activación | Solo en producción (`NODE_ENV === 'production'`) |
| Configuración | Automática — no requiere variable de entorno explícita |

### Docker Hub (Deploy)

| Propiedad | Valor |
|-----------|-------|
| Usuario | `${{ secrets.DOCKER_USERNAME }}` |
| Contraseña / Token | `${{ secrets.DOCKER_PASSWORD }}` |
| Backend tag | `${{ secrets.DOCKER_USERNAME }}/robolearn-backend:latest` |
| Frontend tag | `${{ secrets.DOCKER_USERNAME }}/robolearn-frontend:latest` |

### Codecov (CI)

| Propiedad | Valor |
|-----------|-------|
| Token | `${{ secrets.CODECOV_TOKEN }}` (opcional, `fail_ci_if_error: false`) |

---

## Diagrama de Flujo de Variables de Entorno

```
.env (raíz del proyecto)
│
├── docker-compose.yml
│   ├── ${POSTGRES_USER}      → postgres container
│   ├── ${POSTGRES_PASSWORD}  → postgres container
│   ├── ${MONGO_USER}         → mongo container
│   ├── ${MONGO_PASSWORD}     → mongo container
│   ├── ${REDIS_PASSWORD}     → redis container
│   │
│   ├── backend service (env_file: .env)
│   │   ├── Lee .env automáticamente
│   │   └── Overrides específicos en environment:
│   │       ├── POSTGRES_HOST=postgres
│   │       ├── MONGODB_URL=mongodb://mongo:27017
│   │       └── REDIS_URL=redis://redis:6379/0
│   │
│   └── frontend service (env_file: .env)
│       └── Lee NEXT_PUBLIC_* y JWT_SECRET de .env
│
└── backend/config/settings.py
    └── Lee .env (backend/.env) automáticamente
        └── Valida 8 variables obligatorias al iniciar
```

---

## Configuraciones Adicionales Relevantes

### Next.js (`next.config.mjs`)

```js
const nextConfig = {
  typescript: { ignoreBuildErrors: false },   // TypeScript estricto
  images: { unoptimized: true },               // Sin optimización de imágenes (desarrollo)
  serverExternalPackages: [],                   // Sin paquetes externos en server
}
```

### TypeScript (`tsconfig.json`)

| Propiedad | Valor | Significado |
|-----------|-------|-------------|
| `target` | `ES6` | Compilación a ES6 |
| `module` | `esnext` | Módulos ES nativos |
| `moduleResolution` | `bundler` | Resolución moderna (Next.js) |
| `jsx` | `react-jsx` | JSX transform automático (React 19) |
| `strict` | `true` | Modo estricto |
| `paths` | `@/*` → `./*` | Alias de imports |

### Logging (`logging_config.py`)

| Propiedad | Valor |
|-----------|-------|
| Formato | `2024-01-01 12:00:00 [INFO] robolearn: mensaje` |
| Salida | stdout |
| Nivel | INFO |
| Handler | StreamHandler (consola) |
| Logger name | `robolearn` |

### Docker Compose — Redes

| Red | Driver | Acceso externo | Propósito |
|-----|--------|---------------|-----------|
| `frontend_net` | bridge | ✅ Sí (HTTP) | Comunicación frontend ↔ backend |
| `internal_net` | bridge | ❌ No (aislada) | Backend ↔ PostgreSQL ↔ MongoDB ↔ Redis |
| `ai_net` | bridge | ✅ Sí | Backend ↔ Ollama |

---

## Observaciones y Riesgos

1. **SECRET_KEY compartida** entre backend y frontend — `docker-compose.yml` l.167 asigna `JWT_SECRET: ${SECRET_KEY}`. Ambas aplicaciones usan la misma clave para firmar/verificar JWT. En producción, se recomienda claves separadas con RS256.

2. **Valores por defecto inseguros** — `docker-compose.yml` tiene defaults como `-robolearn_dev` para contraseñas. Si alguien ejecuta `docker compose up` sin `.env`, las contraseñas serán predecibles.

3. **GOOGLE_CREDENTIALS_PATH montado como volumen** — `docker-compose.yml` l.143 monta `./backend/robolearn-key.json`. Este archivo está en `.gitignore`, pero si alguien lo comitea por error, las credenciales GCP quedarán expuestas.

4. **No hay validación de `CORS_ORIGINS` en producción** — `settings.py` lo parsea pero no valida contra orígenes maliciosos.

5. **Red interna de Docker no es cifrada** — El tráfico entre servicios en `internal_net` viaja en texto plano.

6. **Variable `NODE_ENV` duplicada** — Existe `APP_ENV` (backend) y `NODE_ENV` (settings.py l.24). `NODE_ENV` parece no tener uso real y podría eliminarse.

---

*Fin del reporte de Variables de Entorno y Configuración.*
