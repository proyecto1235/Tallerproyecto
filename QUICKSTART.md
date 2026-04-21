# Quick Start - Robolearn 🚀

El inicio más rápido para ejecutar Robolearn localmente con Docker.

## 5 Minutos para Empezar

### 1️⃣ Clonar

```bash
git clone <URL_REPO>
cd Tallerproyecto
```

### 2️⃣ Configurar (Opcional)

```bash
# Solo si quieres cambiar contraseñas
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edita los archivos si lo deseas
```

### 3️⃣ Ejecutar

```bash
docker-compose up --build
```

### 4️⃣ Acceder

| URL | Descripción |
|-----|-------------|
| http://localhost:3000 | 🎨 Frontend (Next.js) |
| http://localhost:8000 | ⚡ Backend API |
| http://localhost:8000/docs | 📚 API Documentation |

### 5️⃣ Login

Usar cualquier usuario de prueba:

```
Email: admin@robolearn.com
Contraseña: admin123

O:

Email: teacher@robolearn.com
Contraseña: teacher123

O:

Email: student1@robolearn.com
Contraseña: student123
```

---

## ¿Qué se levanta automáticamente?

```
✅ PostgreSQL (5432) - Base de datos principal
✅ MongoDB (27017) - Base de datos de eventos
✅ FastAPI Backend (8000) - API REST
✅ Next.js Frontend (3000) - Aplicación web
```

## Problemas Comunes

### "Puerto en uso"

```bash
# Ubuntu/Mac - Encontrar qué está usando el puerto
lsof -i :3000

# Windows - PowerShell
Get-Process | Where-Object {$_.Port -eq 3000}

# Solución: Usar puerto diferente
# Edita docker-compose.yml:
# "3001:3000"  # Frontend
# "8001:8000"  # Backend
```

### "Contenedores no responden"

```bash
# Revisar logs
docker-compose logs

# Reiniciar
docker-compose down
docker-compose up --build
```

### "MongoDB no inicia"

```bash
# Limpiar datos viejos
docker volume rm tallerproyecto_mongo_data

# Reiniciar
docker-compose down -v
docker-compose up --build
```

## Detener

```bash
# Ctrl+C en la terminal

# O en otra terminal:
docker-compose down
```

## Datos de la BD

Se crean automáticamente 4 usuarios + módulos + ejercicios de ejemplo.

Revisar: `scripts/002-seed-data.sql`

## APIs Principales

```bash
# Registrar
POST /api/auth/register

# Login
POST /api/auth/login

# Mi perfil
GET /api/users/profile

# Listar módulos
GET /api/modules

# Recomendaciones (IA/ML)
GET /api/recommendations

# Chatbot
POST /api/chatbot

# Ver documentación completa
curl http://localhost:8000/docs
```

## Stack Utilizado

- **Backend**: FastAPI + PostgreSQL + MongoDB
- **Frontend**: Next.js + TypeScript + TailwindCSS
- **IA/ML**: Scikit-learn + Google Dialogflow
- **Auth**: JWT (7 días de expiración)
- **Arquitectura**: Hexagonal

## Documentación Completa

- [README.md](README.md) - Descripción general
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía detallada
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura hexagonal

## Desarrollo Local (sin Docker)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
pnpm install
pnpm dev
```

## En Producción

1. Cambiar `SECRET_KEY` en backend/.env
2. Cambiar contraseñas de BD
3. Usar HTTPS
4. Restricción CORS
5. Usar variables de entorno seguras

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para más detalles.

---

**¿Preguntas?** Revisar documentación o crear un issue.

**Versión**: 1.0.0  
**Última actualización**: 2026-04-21
