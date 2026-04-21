# Robolearn - Plataforma de Aprendizaje Inteligente

Plataforma web para el aprendizaje de programación y robótica para niños y adolescentes, potenciada con inteligencia artificial y aprendizaje automático.

> [!Note]
> **Integrantes del Proyecto**
> - Perez Ravelo Angel Simon
> - Rojas Quispe Angela Deniss
> - Velasquez Palomino Kevyn L
> - Tucto Ubaldo Ricardo David

## Características Principales

✨ **Arquitectura Hexagonal** - Separación clara de responsabilidades
🤖 **Chatbot IA** - Integración con Google Dialogflow
📊 **Recomendaciones ML** - Scikit-learn para análisis inteligente
🔐 **Autenticación JWT** - Tokens seguros que expiran en 7 días
📱 **Responsive Design** - Next.js + TailwindCSS
💾 **Datos Escalables** - PostgreSQL + MongoDB

## Arquitectura

### Backend (FastAPI + Arquitectura Hexagonal)

```
backend/
├── app/
│   └── main.py              # Rutas y configuración FastAPI
├── config/
│   └── settings.py          # Configuración centralizada
├── domain/                  # Capa de dominio (lógica de negocio)
│   ├── entities/            # Entidades (User, Module, Exercise)
│   ├── ports/               # Interfaces (UserRepository, AIService)
│   └── valueObjects/        # Objetos de valor (Progress)
├── application/             # Capa de aplicación
│   ├── services/            # Servicios (RecommendationService, AIServiceImpl)
│   └── useCases/            # Casos de uso (RegisterUser, GetRecommendations)
├── infrastructure/          # Capa de infraestructura
│   └── adapters/
│       ├── output/
│       │   ├── postgres/    # Repositorios PostgreSQL
│       │   └── mongo/       # Repositorios MongoDB
│       └── input/           # Controladores (routes)
└── tests/
```

### Frontend (Next.js + TypeScript)

```
frontend/
├── app/
│   ├── api/auth/            # Rutas API que redirigen al backend
│   ├── page.tsx             # Home
│   ├── layout.tsx           # Layout general
│   └── dashboard/           # Dashboard por rol
├── components/
│   ├── ui/                  # Componentes Radix UI
│   └── dashboard/           # Componentes específicos
├── hooks/
│   └── use-auth.ts          # Hook para autenticación
└── lib/
    ├── auth.ts              # Funciones de auth
    └── utils.ts             # Utilidades
```

## Integración con IA/ML

### 1. Dialogflow (Chatbot)
- **Endpoint**: `POST /api/chatbot`
- **Función**: Asistente virtual para consultas de estudiantes
- **Almacenamiento**: Historial en MongoDB

### 2. Scikit-learn (Recomendaciones)
- **Predicción de módulos**: Basada en historial del usuario
- **Análisis de patrones**: Deteccion de estilos de aprendizaje
- **Predicción de desempeño**: Score 0-1 para cada módulo

## Autenticación y Seguridad

- **Método**: JWT (JSON Web Tokens)
- **Expiración**: 7 días (modificable en settings)
- **Algoritmo**: HS256
- **Almacenamiento**: HTTP-only cookies (más seguro)
- **Hashing**: Bcrypt para contraseñas

## Bases de Datos

### PostgreSQL (Datos principales)
- Usuarios con roles (student, teacher, admin)
- Módulos y ejercicios
- Inscripciones de estudiantes
- Historial de progreso

### MongoDB (Eventos y métricas)
- Eventos de usuario
- Intentos de ejercicios
- Interacciones con chatbot
- Snapshots de progreso

## Docker Compose

Levanta automáticamente 4 servicios:

```bash
docker-compose up --build
```

| Servicio  | Puerto | Rol |
|-----------|--------|-----|
| PostgreSQL | 5432  | Base de datos relacional |
| MongoDB   | 27017 | Base de datos de eventos |
| Backend   | 8000  | API FastAPI |
| Frontend  | 3000  | App Next.js |

## Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# Clonar proyecto
git clone <REPO_URL>
cd Tallerproyecto

# Copiar archivos de configuración
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Ejecutar
docker-compose up --build

# Acceder a:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Opción 2: Desarrollo Local

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
pnpm install
cp .env.example .env
pnpm dev
```

## Variables de Entorno

### Backend (`backend/.env`)
```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=robolearn_password
POSTGRES_HOST=postgres
POSTGRES_DB=robolearn

# MongoDB
MONGODB_URL=mongodb://mongo:27017
MONGODB_DB=robolearn_metrics

# Seguridad
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Dialogflow (opcional)
DIALOGFLOW_PROJECT_ID=your_project_id
GOOGLE_CREDENTIALS_PATH=/app/credentials.json
```

### Frontend (`frontend/.env`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_JWT_EXPIRATION_DAYS=7
NODE_ENV=development
```

## API Principal

### Autenticación
```
POST   /api/auth/register      # Registrar usuario
POST   /api/auth/login         # Iniciar sesión
POST   /api/auth/logout        # Cerrar sesión
```

### Usuarios
```
GET    /api/users/profile      # Mi perfil (requiere token)
GET    /api/users/{id}         # Usuario público
```

### Módulos
```
GET    /api/modules            # Listar módulos publicados
GET    /api/modules/{id}       # Detalle de módulo
POST   /api/modules/{id}/enroll # Inscribirse
```

### IA/ML
```
GET    /api/recommendations    # Módulos recomendados (requiere token)
GET    /api/learning-path      # Ruta de aprendizaje óptima
GET    /api/performance-prediction/{module_id} # Predicción de desempeño
```

### Chatbot
```
POST   /api/chatbot            # Chat con Dialogflow
```

### Métricas
```
POST   /api/events             # Registrar evento
GET    /api/user-history       # Historial del usuario
```

Ver documentación completa en: `http://localhost:8000/docs`

## Stack Tecnológico

### Backend
- **FastAPI** 0.109.0
- **Python** 3.11+
- **PostgreSQL** 16
- **MongoDB** 7.0
- **Scikit-learn** 1.3.2
- **Google Dialogflow CX** 1.29.0

### Frontend
- **Next.js** 15
- **TypeScript** 5
- **TailwindCSS** 3
- **Radix UI** - Componentes accesibles

## Flujos Principales

### 1. Registro de Usuario
```
Usuario → Formulario → API Register → BD PostgreSQL → JWT Token → Cookie HTTP-only
```

### 2. Obtener Recomendaciones
```
Usuario → GET /api/recommendations → Historial (MongoDB) → Scikit-learn → Módulos similares
```

### 3. Chat con Dialogflow
```
Mensaje → POST /api/chatbot → Dialogflow → Respuesta IA → Guardar en MongoDB
```

## Estructura de Datos (Ejemplos)

### User (PostgreSQL)
```json
{
  "id": 1,
  "email": "estudiante@robolearn.com",
  "full_name": "Juan Pérez",
  "role": "student",
  "is_active": true,
  "created_at": "2026-04-21T10:30:00Z",
  "updated_at": "2026-04-21T10:30:00Z"
}
```

### Module (PostgreSQL)
```json
{
  "id": 1,
  "title": "Introducción a Python",
  "description": "Aprende los fundamentos de programación",
  "teacher_id": 2,
  "status": "approved",
  "is_published": true,
  "created_at": "2026-04-20T15:00:00Z"
}
```

### Event (MongoDB)
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "event_type": "exercise_attempt",
  "user_id": 1,
  "exercise_id": 5,
  "passed": true,
  "score": 0.95,
  "timestamp": "2026-04-21T11:45:00Z"
}
```

## Seguridad

✅ Contraseñas hasheadas con bcrypt
✅ JWT con expiración automática
✅ HTTP-only cookies (protección contra XSS)
✅ CORS configurado
✅ Validación de entrada en backend (Pydantic)
✅ SQL injection protegido (parameterized queries)
✅ Bases de datos en contenedores aislados

## Performance

- ⚡ FastAPI (async/await)
- 🗂️ Connection pooling PostgreSQL
- 💾 Índices en BD para consultas frecuentes
- 📦 Next.js con SSR/SSG
- 🔄 Caché de recomendaciones en Redis (futuro)

## Logs y Monitoreo

Todos los eventos se registran en MongoDB:
- Logins/logouts
- Intentos de ejercicios
- Cambios de progreso
- Interacciones con chatbot

## Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Troubleshooting

### Puerto 5432 en uso
```bash
# Cambiar puerto en docker-compose.yml
"5433:5432"
```

### MongoDB no inicia
```bash
docker volume prune  # Limpiar volúmenes
docker-compose up --build
```

### Token expirado
Automáticamente expira en 7 días. El usuario debe login de nuevo.

## Roadmap

- [ ] Dashboard de analytics para teachers
- [ ] Sistema de badges y logros
- [ ] Integración con pagos (Stripe)
- [ ] Notificaciones en tiempo real (WebSocket)
- [ ] Versión mobile (React Native)
- [ ] Exportar progreso (PDF)
- [ ] Tests automatizados
- [ ] CI/CD con GitHub Actions

## Licencia

[Especificar licencia del proyecto]

## Contacto

Para soporte, crear un issue en el repositorio.

---

**Versión**: 1.0.0  
**Última actualización**: 2026-04-21  
**Estado**: 🚀 En desarrollo