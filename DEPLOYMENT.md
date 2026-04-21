# Guía de Configuración y Despliegue - Robolearn

Esta guía te ayudará a ejecutar el proyecto Robolearn de forma local o con Docker.

## Requisitos Previos

### Para Docker (Recomendado)
- Docker Desktop instalado (versión 20.10+)
- Docker Compose instalado (versión 2.0+)
- 4GB de RAM mínimo disponible

### Para Desarrollo Local
- Python 3.11+
- Node.js 20+
- pnpm (gerenciador de paquetes)
- PostgreSQL 16+ instalado localmente
- MongoDB 7.0+ instalado localmente

## Opción 1: Ejecución con Docker (Más Fácil)

### Paso 1: Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Tallerproyecto
```

### Paso 2: Variables de Entorno

```bash
# Las variables ya están configuradas en docker-compose.yml
# Pero puedes personalizarlas si lo deseas

cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Editar si es necesario:
# backend/.env - Cambiar contraseñas si quieres
# frontend/.env - Cambiar URLs de API si es necesario
```

### Paso 3: Levantar los Servicios

```bash
# Desde la raíz del proyecto
docker-compose up --build

# Esto levantará:
# 1. PostgreSQL en puerto 5432
# 2. MongoDB en puerto 27017
# 3. Backend FastAPI en puerto 8000
# 4. Frontend Next.js en puerto 3000
```

### Paso 4: Acceder a la Aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

### Paso 5: Datos de Prueba

Al iniciar, se crean automáticamente:

**Admin:**
- Email: admin@robolearn.com
- Contraseña: admin123

**Teacher:**
- Email: teacher@robolearn.com
- Contraseña: teacher123

**Students:**
- Email: student1@robolearn.com
- Contraseña: student123
- Email: student2@robolearn.com
- Contraseña: student123
- Email: student3@robolearn.com
- Contraseña: student123

### Detener los Servicios

```bash
# Presionar Ctrl+C en la terminal

# O en otra terminal:
docker-compose down

# Para eliminar también volúmenes (perderá datos):
docker-compose down -v
```

---

## Opción 2: Ejecución Local (Desarrollo)

### Backend Setup

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Editar .env con tus credenciales locales:
# POSTGRES_HOST=localhost
# POSTGRES_PASSWORD=tu_contraseña
# MONGODB_URL=mongodb://localhost:27017

# Ejecutar servidor
uvicorn app.main:app --reload --port 8000

# El backend estará en http://localhost:8000
```

### Frontend Setup (en otra terminal)

```bash
cd frontend

# Instalar dependencias
pnpm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario

# Ejecutar servidor
pnpm dev

# El frontend estará en http://localhost:3000
```

### Bases de Datos Locales

**PostgreSQL:**
```bash
# Si tienes PostgreSQL instalado
createdb robolearn
psql -U postgres -d robolearn -f ../scripts/001-create-tables.sql
psql -U postgres -d robolearn -f ../scripts/002-seed-data.sql
```

**MongoDB:**
```bash
# Si tienes MongoDB instalado
mongosh < ../scripts/003-mongodb-init.js
```

---

## Solución de Problemas

### Puerto 5432 en Uso (PostgreSQL)

```bash
# Opción 1: Usar otro puerto en docker-compose.yml
"5433:5432"

# Opción 2: Matar el proceso
# En Linux/Mac:
lsof -ti:5432 | xargs kill -9

# En Windows:
Get-Process | Where-Object {$_.Port -eq 5432} | Stop-Process
```

### Puerto 3000 en Uso (Frontend)

```bash
# Ejecutar en otro puerto
cd frontend
pnpm dev -- --port 3001
```

### Puerto 8000 en Uso (Backend)

```bash
# Ejecutar en otro puerto
cd backend
uvicorn app.main:app --port 8001
```

### MongoDB No Inicia

```bash
# Limpiar volúmenes
docker volume prune

# Reiniciar
docker-compose down -v
docker-compose up --build
```

### Token Expirado

Los tokens expiran automáticamente después de 7 días. El usuario debe iniciar sesión nuevamente.

Para cambiar esta duración, editar en `backend/config/settings.py`:
```python
access_token_expire_minutes: int = 10080  # 7 días
# Cambiar a:
access_token_expire_minutes: int = 1440   # 1 día
```

### Dialogflow No Funciona

Es opcional. Si no tienes credenciales de Google Cloud:
1. Comentar las variables en `.env`
2. El endpoint `/api/chatbot` retornará un error informativo
3. El resto de la aplicación funciona normalmente

Para habilitarlo:
1. Crear proyecto en Google Cloud
2. Configurar Dialogflow CX
3. Obtener `project-id` y `agent-id`
4. Descargar archivo de credenciales JSON
5. Actualizar en `.env`

---

## Estructura de Directorios

```
Tallerproyecto/
├── backend/                    # API FastAPI
│   ├── app/
│   │   └── main.py            # Todas las rutas
│   ├── config/
│   │   └── settings.py        # Configuración
│   ├── domain/                # Lógica de negocio
│   ├── application/           # Casos de uso
│   ├── infrastructure/        # BD y adaptadores
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env
│   └── .env.example
├── frontend/                  # App Next.js
│   ├── app/
│   │   ├── api/              # Rutas que redirigen al backend
│   │   ├── dashboard/
│   │   └── page.tsx
│   ├── components/
│   ├── lib/
│   ├── package.json
│   ├── Dockerfile
│   ├── .env
│   └── .env.example
├── scripts/
│   ├── 001-create-tables.sql     # Schema PostgreSQL
│   ├── 002-seed-data.sql         # Datos de prueba
│   └── 003-mongodb-init.js       # Índices MongoDB
├── docker-compose.yml        # Configuración de servicios
├── README.md                 # Este archivo
└── DEPLOYMENT.md            # Esta guía
```

---

## Comandos Útiles

### Docker

```bash
# Ver logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
docker-compose logs mongo

# Acceder a contenedor
docker-compose exec postgres psql -U postgres -d robolearn
docker-compose exec mongo mongosh

# Detener sin eliminar
docker-compose stop

# Reanudar
docker-compose start

# Limpiar todo
docker-compose down -v
```

### Backend

```bash
# Tests
cd backend
pytest

# Linting
flake8 .

# Type checking
mypy .
```

### Frontend

```bash
# Tests
cd frontend
pnpm test

# Build
pnpm build

# Linting
pnpm lint
```

---

## Notas de Seguridad

⚠️ **IMPORTANTE PARA PRODUCCIÓN:**

1. **Cambiar SECRET_KEY** en `backend/.env`
   ```env
   SECRET_KEY=genera-una-clave-aleatoria-segura
   ```

2. **Cambiar Contraseñas** de base de datos
   ```env
   POSTGRES_PASSWORD=contraseña_fuerte_aqui
   ```

3. **HTTPS** - Usar certificados SSL/TLS

4. **CORS** - Restringir orígenes permitidos

5. **Variables sensibles** - No commitear `.env` (incluir en `.gitignore`)

6. **Dependencias** - Mantener actualizadas
   ```bash
   pip list --outdated
   pnpm outdated
   ```

---

## Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Estadísticas de Contenedores

```bash
docker stats
```

### Volúmenes

```bash
docker volume ls
docker volume inspect robolearn_postgres_data
docker volume inspect robolearn_mongo_data
```

---

## Integración Continua (CI/CD)

Se puede configurar con GitHub Actions:
- Tests automáticos al hacer push
- Deploy automático a servidor
- Notificaciones de fallos

(Ver `.github/workflows/` cuando se configure)

---

## Contacto y Soporte

Para reportar problemas:
1. Verificar este documento
2. Revisar logs: `docker-compose logs`
3. Crear issue en el repositorio
4. Contactar con los integrantes

---

**Última actualización**: 2026-04-21  
**Versión**: 1.0.0
