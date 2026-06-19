# Auditoría de Software — Entorno Reconstruido

**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Auditor:** Asistente de IA (análisis automatizado)  
**Propósito:** Reconstruir el entorno de desarrollo y producción necesario para ejecutar el proyecto.

---

## 1. Software Requerido

### Obligatorio (base del proyecto)

| Software | Versión Mínima | Versión Recomendada | Propósito |
|----------|---------------|---------------------|-----------|
| Docker Engine | 24.0+ | 27.x+ | Contenedores de todos los servicios |
| Docker Compose | v2.20+ | v2.30+ | Orquestación multi-servicio |
| Git | 2.30+ | 2.45+ | Control de versiones |
| GNU Make (opcional) | — | 4.3+ | Automatización de comandos |

### Alternativa — Desarrollo local (sin Docker)

| Software | Versión Mínima | Versión Recomendada | Propósito |
|----------|---------------|---------------------|-----------|
| Python | 3.11.0 | 3.11.11 | Backend + ML Pipeline |
| Node.js | 20.0.0 | 20.18.x | Frontend |
| npm | 10.0+ | 10.8+ | Gestor de paquetes frontend |
| PostgreSQL | 16.0 | 16.4+ | Base de datos principal |
| pgvector | 0.7+ | 0.8+ | Extension de vectores (RAG) |
| MongoDB | 7.0 | 7.0+ | Base de datos de eventos |
| Redis | 7.0 | 7.4+ | Caché y rate limiting |
| Ollama | 0.3+ | 0.5+ | LLM local |
| pip | 24.0+ | 24.3+ | Gestor de paquetes Python |

### CI/CD (GitHub Actions)

| Software | Versión | Propósito |
|----------|---------|-----------|
| GitHub Actions | — | CI/CD pipeline |
| Docker Buildx | plugin | Build multi-plataforma |
| Codecov | — | Reporte de cobertura |
| k6 | 0.50+ | Pruebas de carga |
| Cypress | 13+ | Pruebas E2E |

---

## 2. Versiones Recomendadas (del proyecto)

Extraídas de los archivos de dependencias (`backend/requirements.txt`, `frontend/package.json`, `docker-compose.yml`):

### Backend Python

| Paquete | Versión en proyecto | Versión recomendada actualizada | Nota |
|---------|--------------------|--------------------------------|------|
| fastapi | 0.109.0 | 0.109.0+ | Mantener |
| uvicorn[standard] | 0.27.0 | 0.27.0+ | Mantener |
| python-jose[cryptography] | 3.3.0 | **3.4.0+** | 🔴 CVE-2024-33663 |
| bcrypt | 3.2.0 | 4.2.0+ | Mejoras de rendimiento |
| python-multipart | 0.0.6 | 0.0.9+ | Mantenimiento |
| pymongo | 4.6.0 | 4.10+ | Mantenimiento |
| psycopg2-binary | 2.9.9 | 2.9.9+ | Mantener |
| python-dotenv | 1.0.0 | 1.0.0+ | Mantener |
| pydantic | 2.5.0 | 2.13+ | Mejoras y parches |
| pydantic-settings | 2.1.0 | 2.8+ | Mantenimiento |
| scikit-learn | 1.8.0 | 1.9+ | Mantenimiento |
| joblib | 1.5.3 | 1.5.3+ | Mantener |
| numpy | 1.26.3 | 1.26.3+ | 2.x requiere migración |
| pandas | 2.1.4 | 2.2+ | Mantenimiento |
| scipy | 1.11.4 | 1.14+ | Mantenimiento |
| apscheduler | 3.10.4 | 3.11+ | Mantenimiento |
| docker | 7.1.0 | 7.1.0+ | Mantener |
| redis[hiredis] | 5.1.0 | 5.2+ | Mantenimiento |
| httpx | 0.27.0 | 0.27.0+ | Mantener |

### ML Pipeline Python

| Paquete | Versión en proyecto | Versión recomendada |
|---------|--------------------|---------------------|
| pandas | >=1.5.0 | 2.2+ |
| numpy | >=1.24.0 | 1.26.3+ |
| scikit-learn | >=1.3.0 | 1.8+ |
| joblib | >=1.2.0 | 1.5.3+ |
| matplotlib | >=3.7.0 | 3.9+ |
| seaborn | >=0.12.0 | 0.13+ |
| pyarrow | >=12.0.0 | 18+ |

### Frontend Node.js

| Paquete | Versión en proyecto | Nota |
|---------|--------------------|------|
| next | 16.2.4 | 🟡 Actualizar a 16.2.5+ (CVE-2026-44581) |
| react | 19.2.4 | Mantener |
| react-dom | 19.2.4 | Mantener |
| typescript | 5.7.3 | Mantener |
| tailwindcss | 4.2.0 | Mantener |
| jose | 6.2.2 | Mantener |
| zod | 3.24.1 | Mantener |

---

## 3. Servicios Externos Requeridos

### Obligatorios

| Servicio | Imagen Docker | Propósito | Puerto por defecto |
|----------|--------------|-----------|--------------------|
| PostgreSQL 16 + pgvector | `pgvector/pgvector:pg16` | Datos principales | 5432 |
| MongoDB 7 | `mongo:7` | Eventos + analítica conductual | 27017 |
| Redis 7 | `redis:7-alpine` | Caché + rate limiting | 6379 |
| Ollama + Qwen2.5-Coder 1.5B | `ollama/ollama:latest` | LLM local (tutor, RAG) | 11434 |

### Opcionales (fallback / feature)

| Servicio | Propósito | Configuración necesaria |
|----------|-----------|------------------------|
| Dialogflow CX (Google Cloud) | Chatbot conversacional | `DIALOGFLOW_PROJECT_ID` + `DIALOGFLOW_AGENT_ID` + credenciales JSON |
| OpenAI API | Fallback de IA cuando Ollama no responde | `OPENAI_API_KEY` |
| Vercel Analytics | Analytics del frontend | Automático con `@vercel/analytics` (solo producción) |
| Docker Hub | Registro de imágenes para deploy | Cuenta Docker Hub + `DOCKER_USERNAME`/`DOCKER_PASSWORD` |
| Codecov | Reporte de cobertura de tests | `CODECOV_TOKEN` |

---

## 4. Bases de Datos Requeridas

### PostgreSQL 16 (principal)

| Propiedad | Valor |
|-----------|-------|
| Imagen Docker | `pgvector/pgvector:pg16` |
| Puerto | 5432 |
| Base de datos | `robolearn` |
| Usuario | `postgres` (configurable) |
| Contraseña | Configurable via `.env` |
| Extensión requerida | `vector` (pgvector) |
| Scripts de inicialización | `backend/scripts/001-init.sql` (schema + stored procedures) |
| Seed data | `backend/scripts/002-seed-data.sql`, `003-seed-massive.sql` |

**Tablas creadas (22):**
`users`, `modules`, `lessons`, `exercises`, `enrollments`, `progress`, `exercise_attempts`, `lesson_completions`, `chatbot_sessions`, `challenges`, `challenge_attempts`, `achievements`, `user_achievements`, `classes`, `class_modules`, `class_exercises`, `class_enrollments`, `class_exercise_attempts`, `exercise_suggestions`, `alert_log`, `knowledge_chunks` (pgvector)

**Vistas (1):** `user_statistics`  
**Stored Procedures (8):** `sp_upsert_progress`, `sp_record_exercise_attempt`, `fn_get_student_progress_summary`, `fn_get_teacher_dashboard`, `fn_get_admin_stats`, `fn_get_admin_modules`, `fn_get_student_alerts`, `sp_award_points`, `sp_enroll_student`, `sp_check_and_award_achievements`, `fn_get_weekly_activity`, `fn_get_student_performance_distribution`, `fn_get_module_detail_for_admin`, `fn_search_users`

### MongoDB 7 (eventos + analítica)

| Propiedad | Valor |
|-----------|-------|
| Imagen Docker | `mongo:7` |
| Puerto | 27017 |
| Base de datos | `robolearn_metrics` |
| Usuario | `admin` (configurable) |
| Script de inicialización | `backend/scripts/004-mongodb-init.js` |

**Colecciones creadas (13):**
`events`, `exercise_attempts`, `progress_snapshots`, `chat_interactions`, `sessions`, `session_metrics`, `behavioral_events`, `frustration_signals`, `code_analysis`, `engagement_scores`, `predictions`, `tutor_interactions`, `admin_stats`

### Redis 7 (caché)

| Propiedad | Valor |
|-----------|-------|
| Imagen Docker | `redis:7-alpine` |
| Puerto | 6379 |
| Contraseña | Configurable (vacía por defecto en dev) |
| Persistencia | Append-only file (AOF) |
| Propósito | Caché de respuestas de IA, rate limiting |

---

## 5. Variables de Entorno

Basado en `backend/.env.example`, `frontend/.env.example` (implícito) y `docker-compose.yml`.

### Backend

```bash
# ============================================
# APP
# ============================================
APP_NAME=Robolearn API
APP_ENV=development           # development | production
DEBUG=True

# ============================================
# SEGURIDAD — JWT
# ============================================
SECRET_KEY=changeme-para-produccion-robolearn
ALGORITHM=HS256               # HS256 | RS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Opcional — para RS256:
# JWT_PRIVATE_KEY=<contenido de private.pem>
# JWT_PUBLIC_KEY=<contenido de public.pem>

# ============================================
# POSTGRESQL
# ============================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=robolearn_dev
POSTGRES_HOST=localhost       # postgres si usa Docker
POSTGRES_PORT=5432
POSTGRES_DB=robolearn
DB_POOL_MIN=5
DB_POOL_MAX=50

# ============================================
# MONGODB
# ============================================
MONGODB_URL=mongodb://localhost:27017   # mongo si usa Docker
MONGODB_DB=robolearn_metrics

# ============================================
# REDIS
# ============================================
REDIS_URL=redis://localhost:6379/0      # redis si usa Docker
REDIS_PASSWORD=

# ============================================
# OLLAMA (IA LOCAL)
# ============================================
OLLAMA_URL=http://localhost:11434       # ollama si usa Docker
OLLAMA_MODEL=qwen2.5-coder:1.5b

# ============================================
# OPENAI (FALLBACK OPCIONAL)
# ============================================
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# ============================================
# DIALOGFLOW (CHATBOT OPCIONAL)
# ============================================
DIALOGFLOW_PROJECT_ID=
DIALOGFLOW_AGENT_ID=
GOOGLE_CREDENTIALS_PATH=backend/robolearn-key.json

# ============================================
# ML MODELS
# ============================================
ML_MODEL_DIR=models

# ============================================
# CORS
# ============================================
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### Frontend

```bash
# ============================================
# FRONTEND
# ============================================
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_JWT_EXPIRATION_DAYS=7

# Debe coincidir con SECRET_KEY del backend
JWT_SECRET=changeme-para-produccion-robolearn
```

---

## 6. Configuración Necesaria

### Docker Compose (`docker-compose.yml`)

El proyecto incluye un `docker-compose.yml` completo con 6 servicios:

```
Servicios:
├── postgres  (pgvector/pgvector:pg16)   → puerto 5432
├── mongo     (mongo:7)                  → puerto 27017
├── redis     (redis:7-alpine)           → puerto 6379
├── ollama    (ollama/ollama:latest)     → puerto 11434
├── backend   (Dockerfile local)         → puerto 8000
└── frontend  (Dockerfile local)         → puerto 3000

Volúmenes:
├── postgres_data
├── mongo_data
├── redis_data
└── ollama_data

Redes:
├── frontend_net  → bridge (acceso externo)
├── internal_net  → bridge (interna, aislada)
└── ai_net        → bridge (acceso externo)
```

### Healthchecks
- PostgreSQL: `pg_isready`
- MongoDB: `mongosh --eval 'db.runCommand({ ping: 1 })'`
- Redis: `redis-cli ping`

### Redes Docker
- `frontend_net`: frontend ↔ backend (comunicación HTTP)
- `internal_net`: backend ↔ postgres ↔ mongo ↔ redis (aislada del exterior)
- `ai_net`: backend ↔ ollama (acceso a GPU si está disponible)

---

## 7. Procedimiento Completo de Instalación

### A. Requisitos previos (Ubuntu Linux)

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Docker Engine
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 3. Verificar instalación
sudo docker --version
sudo docker compose version

# 4. (Opcional) Ejecutar Docker sin sudo
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar, o ejecutar: newgrp docker

# 5. Instalar Git
sudo apt install -y git

# 6. (Opcional) Instalar herramientas de desarrollo
sudo apt install -y make curl wget
```

### B. Clonar el Repositorio

```bash
# 1. Clonar
git clone https://github.com/proyecto1235/Tallerproyecto.git
cd Tallerproyecto

# 2. Ver rama (se recomienda main o develop)
git branch -a
```

### C. Configurar Variables de Entorno

```bash
# 1. Crear archivo .env desde la plantilla
cp backend/.env.example .env

# 2. Editar con valores seguros (producción)
# nano .env
# Como mínimo, cambiar:
#   SECRET_KEY=<generar clave aleatoria>
#   POSTGRES_PASSWORD=<contraseña segura>
#   MONGO_INITDB_ROOT_PASSWORD=<contraseña mongo>

# Generar SECRET_KEY segura:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### D. Despliegue con Docker (Método Oficial — Recomendado)

```bash
# 1. Levantar todos los servicios
docker compose up -d

# 2. Verificar que todos los contenedores estén corriendo
docker compose ps

# 3. Ver logs del backend (opcional)
docker compose logs -f backend
```

**Salida esperada:**
```
NAME                    STATUS              PORTS
robolearn_postgres     Up (healthy)         0.0.0.0:5432->5432/tcp
robolearn_mongo        Up (healthy)         0.0.0.0:27017->27017/tcp
robolearn_redis        Up (healthy)         0.0.0.0:6379->6379/tcp
robolearn_ollama       Up (healthy)         0.0.0.0:11434->11434/tcp
robolearn_backend      Up                   0.0.0.0:8000->8000/tcp
robolearn_frontend     Up                   0.0.0.0:3000->3000/tcp
```

### E. Verificar el Despliegue

```bash
# Backend API
curl http://localhost:8000/health
# → {"status": "healthy"}

# API Docs (Swagger)
# Abrir en navegador: http://localhost:8000/docs

# Frontend
# Abrir en navegador: http://localhost:3000

# Verificar PostgreSQL
docker exec robolearn_postgres psql -U postgres -d robolearn -c "\dt"

# Verificar MongoDB
docker exec robolearn_mongo mongosh robolearn_metrics --eval "db.getCollectionNames()"

# Verificar Redis
docker exec robolearn_redis redis-cli ping
# → PONG

# Verificar Ollama
docker exec robolearn_ollama ollama list
# → debería mostrar qwen2.5-coder:1.5b
# (la primera vez se descarga automáticamente, puede tomar varios minutos)
```

### F. Despliegue Local (sin Docker)

#### 1. Backend

```bash
# Requisitos: Python 3.11, PostgreSQL 16+pgvector, MongoDB 7, Redis 7
# Los servicios de base de datos deben estar instalados y corriendo.

# 1. Crear y activar entorno virtual
cd backend
python3.11 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configurar variables de entorno
# Asegurarse de que POSTGRES_HOST=localhost (no "postgres")
# Asegurarse de que MONGODB_URL apunta a localhost
# Asegurarse de que REDIS_URL apunta a localhost

# 4. Configurar base de datos PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE robolearn;"
sudo -u postgres psql -d robolearn -f scripts/001-init.sql
sudo -u postgres psql -d robolearn -f scripts/002-seed-data.sql
# (opcional) sudo -u postgres psql -d robolearn -f scripts/003-seed-massive.sql

# 5. Configurar extensión pgvector
sudo -u postgres psql -d robolearn -f scripts/005-enable-pgvector.sql

# 6. Inicializar MongoDB
mongosh robolearn_metrics scripts/004-mongodb-init.js

# 7. Iniciar servidor backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend

```bash
# Requisitos: Node.js 20+

# 1. Instalar dependencias
cd frontend
npm install

# 2. Configurar variables de entorno
# Crear frontend/.env.local con:
#   NEXT_PUBLIC_API_URL=http://localhost:8000/api
#   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
#   JWT_SECRET=<mismo SECRET_KEY del backend>

# 3. Iniciar servidor de desarrollo
npm run dev
```

#### 3. ML Pipeline (independiente)

```bash
# Requisitos: Python 3.11 (puede usar el mismo venv del backend)

# 1. Activar entorno
cd backend
source .venv/bin/activate

# 2. Instalar dependencias adicionales
cd ../ml_pipeline
pip install -r requirements.txt

# 3. Ejecutar pipeline completo
python run_all.py

# Opciones:
# python run_all.py --skip 03        # saltar evaluación
# python run_all.py --only 02        # solo entrenamiento
```

### G. Pruebas

```bash
# Backend — pruebas unitarias
cd backend
source .venv/bin/activate
pip install pytest pytest-cov pytest-asyncio httpx
pytest tests/ -v --cov=application --cov=app --cov=config

# Frontend — lint y type check
cd frontend
npm run lint
npx tsc --noEmit

# Frontend — pruebas (si existen)
npm test

# Pruebas de carga (k6)
k6 run tests/load/k6-load-test.js
```

### H. Comandos Útiles (Docker)

```bash
# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f frontend

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (CUIDADO: borra datos de BD)
docker compose down -v

# Reconstruir imágenes después de cambios
docker compose up -d --build

# Acceder a un contenedor
docker exec -it robolearn_backend bash
docker exec -it robolearn_frontend sh

# Ver uso de recursos
docker stats

# Ver logs de inicialización de BD
docker compose logs postgres
docker compose logs mongo
```

### I. CI/CD Pipeline

El proyecto incluye GitHub Actions preconfigurados:

#### CI (`.github/workflows/ci.yml`)
Se ejecuta en push a `main`/`develop` y PR a `main`:
```
Jobs:
├── backend-lint    → flake8 + mypy + isort
├── backend-tests   → pytest con PostgreSQL + MongoDB + Redis service containers
│   └── coverage    → upload a Codecov
├── frontend-lint   → next lint + tsc --noEmit
├── frontend-tests  → vitest (si hay tests)
└── build           → Docker Buildx (backend + frontend)
```

#### Deploy (`.github/workflows/deploy.yml`)
Se ejecuta en push a `main` (o manual):
```
Jobs:
└── deploy
    ├── Login a Docker Hub
    ├── Build + Push de imágenes (backend + frontend)
    └── SSH a VPS → git pull + docker compose pull + up -d
```

**Secretos requeridos en GitHub:**
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`

---

## Diagrama de Arquitectura del Entorno

```
┌─────────────────────────────────────────────────────────────────┐
│                        UBUNTU LINUX HOST                         │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                     DOCKER ENGINE                           │   │
│  │                                                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌─────────────┐   │   │
│  │  │ postgres │  │  mongo   │  │ redis │  │   ollama    │   │   │
│  │  │ :5432    │  │ :27017   │  │ :6379 │  │  :11434     │   │   │
│  │  └────┬─────┘  └────┬─────┘  └───┬───┘  └──────┬──────┘   │   │
│  │       │              │            │              │          │   │
│  │       └──────────────┴────────────┴──────────────┘          │   │
│  │                            │ internal_net                    │   │
│  │                    ┌───────┴────────┐                        │   │
│  │                    │   backend      │                        │   │
│  │                    │   FastAPI      │                        │   │
│  │                    │   :8000        │                        │   │
│  │                    └───────┬────────┘                        │   │
│  │                            │                                 │   │
│  │                    ┌───────┴────────┐                        │   │
│  │                    │   frontend     │                        │   │
│  │                    │   Next.js      │                        │   │
│  │                    │   :3000        │                        │   │
│  │                    └────────────────┘                        │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Servicios externos (opcionales):                                 │
│  ├── Dialogflow CX (Google Cloud)  → chatbot                     │
│  └── OpenAI API                    → fallback IA                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Checklist de Verificación

Antes de considerar el entorno listo, confirmar:

- [ ] Docker + Docker Compose instalados y funcionando
- [ ] Repositorio clonado
- [ ] Archivo `.env` creado con valores seguros
- [ ] `docker compose up -d` ejecutado sin errores
- [ ] `docker compose ps` muestra 6 servicios "Up"
- [ ] `curl http://localhost:8000/health` responde `{"status": "healthy"}`
- [ ] `curl http://localhost:8000/docs` responde con Swagger UI
- [ ] Navegador abre `http://localhost:3000` sin errores
- [ ] Registro de usuario funciona (`POST /api/auth/register`)
- [ ] Login de usuario funciona (`POST /api/auth/login`)
- [ ] PostgreSQL tiene tablas creadas (`\dt`)
- [ ] MongoDB tiene colecciones creadas
- [ ] Ollama responde con el modelo qwen2.5-coder:1.5b

---

## Troubleshooting Común

| Problema | Causa posible | Solución |
|----------|--------------|----------|
| Puerto 5432 en uso | PostgreSQL local corriendo | `sudo systemctl stop postgresql` |
| Backend no conecta a BD | `POSTGRES_HOST` incorrecto | En Docker usar `postgres`, en local usar `localhost` |
| Ollama no responde | Primera descarga del modelo | Esperar 2-3 minutos, verificar con `docker compose logs ollama` |
| Frontend no conecta | `NEXT_PUBLIC_API_URL` incorrecto | Verificar que apunte a `http://localhost:8000/api` |
| JWT inválido | `SECRET_KEY` no coincide entre backend y frontend | Usar la misma clave en ambos `.env` |
| pgvector no disponible | PostgreSQL sin la extensión | Usar imagen `pgvector/pgvector:pg16` en vez de `postgres:16` |
| MongoDB auth failed | Credenciales incorrectas | Verificar `MONGO_INITDB_ROOT_USERNAME` y `MONGO_INITDB_ROOT_PASSWORD` |
| `docker compose` no encontrado | Docker Compose v1 instalado | Usar `docker-compose` (guión) o instalar plugin v2 |

---

*Fin del reporte de Entorno Reconstruido.*
