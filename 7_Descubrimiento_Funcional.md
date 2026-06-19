# Descubrimiento Funcional — RoboLearn

**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Rol:** Ingeniero de Soporte Nivel 3  
**Propósito:** Inventario funcional completo del sistema: módulos, menús, formularios, procesos de negocio, APIs y flujos principales.

---

## 1. Módulos Funcionales

| # | Módulo | Cobertura | Archivos Clave | Descripción |
|---|--------|-----------|----------------|-------------|
| F1 | **Autenticación y Cuentas** | Backend + Frontend | `auth.py`, `use-auth.ts`, `login/page.tsx`, `register/page.tsx`, `logout/page.tsx`, `proxy.ts` | Registro, inicio de sesión, cierre de sesión, recuperación de sesión, validación JWT, blacklist de tokens |
| F2 | **Gestión de Usuarios y Perfiles** | Backend + Frontend | `user_repository_impl.py`, `settings/page.tsx`, `profile/[id]/page.tsx` | CRUD de perfiles, búsqueda, roles (student/teacher/admin), puntos, racha de días |
| F3 | **Módulos de Aprendizaje** | Backend + Frontend | `module_repository_impl.py`, `modules/page.tsx`, `modules/[id]/page.tsx` | Exploración, inscripción, progreso, lecciones, ejercicios por módulo |
| F4 | **Ejercicios Interactivos** | Backend + Frontend | `exercises/page.tsx`, `InteractiveExercise.tsx`, `InlineExercise.tsx`, `sandbox_service.py`, `code_executor.py` | Editor de código, ejecución sandbox (Docker), comparación de output, historial de intentos, análisis de dificultad |
| F5 | **Tutor Inteligente (IA)** | Backend + Frontend | `intelligent_tutor.py`, `ai_tutor_service.py`, `chat-widget.tsx`, `tutor ask/hint/explain/feedback endpoints` | Chat conversacional, detección de intención, pistas contextuales, explicaciones de concepto, adaptación por nivel y frustración |
| F6 | **Chatbot Omnicanal** | Backend + Frontend | `ai_service_impl.py`, `llm_service.py`, `chatbot endpoints`, `chat-widget.tsx` | Integración Dialogflow CX, fallback Ollama, fallback OpenAI, fallback IntelligentTutor, modo público sin auth |
| F7 | **Sistema de Logros** | Backend + Frontend | `dependencies.py`, `achievements/page.tsx`, `achievement-badge.tsx` | Logros automáticos por hitos (ejercicios, módulos, rachas, challenges, first-try), puntos, insignias |
| F8 | **Clases (Aulas Virtuales)** | Backend + Frontend | `classes/` pages, `ClassCreate/Update/Exercises endpoints` | Creación de clases por teachers, solicitudes de inscripción, módulos personalizados por clase, ejercicios de clase |
| F9 | **Challenges (Competencias)** | Backend + Frontend | `challenges/` pages, `ChallengeCreate/Submit endpoints` | Desafíos de programación con fecha límite, intentos limitados, solución y test code |
| F10 | **Analítica Predictiva (Teachers)** | Backend + Frontend | `analytics/page.tsx`, `analytics_router.py`, `MLOrchestrator`, `metrics_service.py` | Dashboard de métricas por estudiante, factores de riesgo, predicciones de rendimiento, calor de predicciones, clustering, detección de anomalías |
| F11 | **Analítica de Estudiante** | Backend + Frontend | `mis-metricas/page.tsx`, `student_metrics_repository.py` | Progreso personal, actividad semanal, rendimiento por módulo, racha de estudio |
| F12 | **Panel del Docente** | Backend + Frontend | `teacher-dashboard.tsx`, `TeacherDashboardUseCase`, `teacher endpoints` | Resumen de clases, estudiantes, alertas generadas por IA, análisis de dificultad de ejercicios |
| F13 | **Panel del Administrador** | Backend + Frontend | `admin-dashboard.tsx`, `admin/* endpoints` | Gestión de usuarios, aprobación de docentes, revisión de contenido, logs de auditoría, salud del sistema |
| F14 | **Sandbox de Código** | Backend | `sandbox_service.py`, `code_executor.py`, `main.py:1104-1198` | Ejecución segura de código Python en contenedores Docker con restricciones de recursos, sin red, solo lectura |
| F15 | **Motor de Recomendaciones IA** | Backend | `GetRecommendationsUseCase`, `AIServiceImpl`, `ai_service.py` | Recomendaciones personalizadas de módulos basadas en historial y ML |
| F16 | **RAG (Retrieval Augmented Generation)** | Backend | `rag_service.py`, `embedding_service.py`, `pgvector` | Indexación de contenido educativo, búsqueda semántica por similitud coseno, contexto aumentado para el tutor |
| F17 | **Pipeline ML Predictivo** | Backend (ML) | `MLOrchestrator`, `EngagementPredictor`, `PerformancePredictor`, `DropoutPredictor`, `FrustrationPredictor`, `clustering.py`, `anomaly_detector.py` | 6 modelos scikit-learn para predecir engagement, rendimiento, deserción, frustración, clustering de estudiantes y detección de anomalías |
| F18 | **Generación Automática de Ejercicios** | Backend | `ExerciseGeneratorService`, `exercise_generator_service.py` | Sugerencias de variantes de ejercicios generadas por LLM, flujo de aprobación/rechazo |
| F19 | **Notificaciones y Alertas** | Backend + Frontend | `GenerateAIAlertsUseCase`, `alerts/page.tsx`, `_try_warm_predictions` | Alertas dinámicas por IA para docentes (dificultad, estudiantes lentos/rápidos) |
| F20 | **Eventos y Métricas** | Backend | `EventRepository`, `BehavioralRepository`, `MetricsService`, `AnalyticsScheduler` | Tracking de eventos de usuario, sesiones, señales de frustración, snapshots semanales, programación de snapshots vía APScheduler |
| F21 | **Auditoría** | Backend + Frontend | `audit/page.tsx`, `audit_logging middleware`, `event_repository_impl.py` | Logs de auditoría para rutas sensibles (auth, admin, profile, execute-code, submit) |
| F22 | **Notificaciones de Seguridad (Headers HTTP)** | Backend | `main.py:110-122` | CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Permissions-Policy |

---

## 2. Menús (Navegación por Rol)

### 2.1 Estudiante (`StudentSidebar`)

| Ruta | Label | Descripción |
|------|-------|-------------|
| `/dashboard` | Inicio | Panel principal con clases, progreso, achievements recientes |
| `/dashboard/modules` | Módulos | Explorar módulos disponibles e inscribirse |
| `/dashboard/exercises` | Ejercicios | Lista global de ejercicios con filtros |
| `/dashboard/challenges` | Challenges | Ver challenges activos/completados |
| `/dashboard/classes` | Clases | Explorar clases y solicitar inscripción |
| `/dashboard/analytics/mis-metricas` | Mis Métricas | Panel personal de progreso y rendimiento |
| `/dashboard/achievements` | Logros | Galería de logros (todos/desbloqueados/bloqueados) |
| `/dashboard/settings` | Ajustes | Perfil, notificaciones, apariencia, zona de peligro |

### 2.2 Docente (Teacher) — Hereda de Estudiante + agrega:

| Ruta | Label | Descripción |
|------|-------|-------------|
| `/dashboard/my-classes` | Mis Clases | CRUD de clases, módulos por clase, solicitudes de estudiantes |
| `/dashboard/students` | Estudiantes | Lista de estudiantes con progreso |
| `/dashboard/metrics` | Métricas | Gráficos (barras, pastel, líneas) de rendimiento |
| `/dashboard/analytics` | Analítica IA | Dashboard predictivo: predicciones, riesgo, clusters, anomalías |
| `/dashboard/alerts` | Alertas IA | Lista de alertas generadas por IA con filtros |

### 2.3 Administrador — Hereda de Teacher + agrega:

| Ruta | Label | Descripción |
|------|-------|-------------|
| `/dashboard/teacher-requests` | Solicitudes Docentes | Aprobar/rechazar solicitudes de role teacher |
| `/dashboard/users` | Usuarios | CRUD de usuarios, cambiar roles, activar/desactivar |
| `/dashboard/content-review` | Revisión de Contenido | Aprobar/rechazar módulos creados por teachers |
| `/dashboard/audit` | Auditoría | Logs de auditoría y salud del sistema |

### 2.4 Público (Sin Autenticación)

| Ruta | Label | Descripción |
|------|-------|-------------|
| `/` | Landing | Hero, características, roles, CTA |
| `/login` | Iniciar Sesión | Formulario de login |
| `/register` | Registrarse | Formulario de registro |

---

## 3. Formularios

| # | Formulario | Ubicación | Campos | Validación | Método HTTP |
|---|-----------|-----------|--------|------------|-------------|
| FR1 | **Login** | `login/page.tsx` | email (email), password (password + show/hide toggle) | Campos requeridos | `POST /api/auth/login` |
| FR2 | **Registro** | `register/page.tsx` | fullName (text), email (email), password (password), confirmPassword (password), requestTeacher (checkbox) | Confirmación de password, campos requeridos | `POST /api/auth/register` |
| FR3 | **Actualizar Perfil** | `settings/page.tsx` (tab Profile) | fullName (text), email (email), password (password, opcional), avatarUrl (url, opcional), bio (textarea, opcional) | Campos requeridos | `PUT /api/users/profile` |
| FR4 | **Crear Challenge** | `challenges/create/page.tsx` | title (text), description (textarea), instructions (textarea), difficulty (select: 1-5), points (number), baseCode (code), solutionCode (code), solutionType (select: output/test), solutionOutput (textarea), testCode (code), deadline (datetime), isPublished (checkbox), maxAttempts (number) | Campos requeridos | `POST /api/challenges` |
| FR5 | **Crear Clase** | `my-classes/[id]/page.tsx` (modal) | title (text), description (textarea), category (text), difficulty (select: 1-5), isPublished (checkbox) | Campos requeridos | `POST /api/classes` |
| FR6 | **Actualizar Clase** | `my-classes/[id]/page.tsx` (modal) | title, description, category, difficulty, isPublished | Opcionales | `PUT /api/classes/{id}` |
| FR7 | **Crear Módulo** | `modules/[id]/edit/page.tsx` | title (text), description (textarea), theoryContent (markdown), difficulty (select), order (number) | Campos requeridos | `POST /api/modules` |
| FR8 | **Actualizar Módulo** | `modules/[id]/edit/page.tsx` | title, description, theoryContent, difficulty, order, isPublished | Opcionales | `PUT /api/modules/{id}` |
| FR9 | **Crear Lección** | `modules/[id]/edit/page.tsx` | title (text), theoryContent (markdown), order (number) | Campos requeridos | `POST /api/modules/{id}/lessons` |
| FR10 | **Crear Ejercicio** (en módulo) | `modules/[id]/edit/page.tsx` | title, description, instructions, difficulty, points, solutionOutput, solutionType, testCode, order, lessonId | Campos requeridos | `POST /api/modules/{moduleId}/exercises` |
| FR11 | **Crear Ejercicio de Clase** | `my-classes/[id]/module/[moduleId]/edit/page.tsx` | title, description, instructions, exerciseType, difficulty, points, order, solutionOutput, solutionType, testCode, metadata | Campos requeridos | `POST /api/classes/{classId}/modules/{moduleId}/exercises` |
| FR12 | **Enviar Ejercicio** | `InteractiveExercise.tsx`, `InlineExercise.tsx` | code (code editor via CodeMirror) | Código no vacío | `POST /api/exercises/submit` |
| FR13 | **Enviar Challenge** | `challenges/[id]/page.tsx` | code (code editor via CodeMirror) | Código no vacío | `POST /api/challenges/submit` |
| FR14 | **Ejecutar Código** | `exercises/page.tsx` | code (code editor) | Código no vacío | `POST /api/execute-code` |
| FR15 | **Chat / Tutor** | `chat-widget.tsx` | message (text + file upload) | Mensaje no vacío | `POST /api/chatbot`, `POST /api/tutor/ask` |
| FR16 | **Solicitar Pista** | `InteractiveExercise.tsx` | (botón, no formulario) | — | `POST /api/tutor/hint` |
| FR17 | **Solicitar Explicación** | `chat-widget.tsx` | concept (text) | Concepto no vacío | `POST /api/tutor/explain` |
| FR18 | **Feedback de Tutor** | `chat-widget.tsx` | helpful (boolean), message (text, opcional) | — | `POST /api/tutor/feedback` |
| FR19 | **Configuración - Notificaciones** | `settings/page.tsx` (tab Notifications) | emailNotifications (switch), pushNotifications (switch) | — | (solo UI, sin endpoint) |
| FR20 | **Configuración - Apariencia** | `settings/page.tsx` (tab Appearance) | theme (select: dark/light/system) | — | (solo UI, sin endpoint) |
| FR21 | **Configuración - Zona de Peligro** | `settings/page.tsx` (tab Danger Zone) | deleteAccount (botón con confirmación) | Confirmación | (solo UI) |

---

## 4. Procesos de Negocio

| ID | Proceso | Actor | Descripción | Pasos | Endpoints Involucrados |
|----|---------|-------|-------------|-------|----------------------|
| B1 | **Registro de Usuario** | Público | Crear cuenta como estudiante, opcionalmente solicitar rol teacher | 1. Llenar formulario → 2. Validar datos → 3. Hash password (bcrypt) → 4. Crear usuario → 5. Generar JWT → 6. Setear cookie → 7. Retornar usuario | `POST /api/auth/register` |
| B2 | **Inicio de Sesión** | Usuario | Autenticarse en la plataforma | 1. Enviar email+password → 2. Buscar usuario → 3. Verificar password (bcrypt) → 4. Verificar estado activo → 5. Generar JWT → 6. Setear cookie → 7. Log evento login | `POST /api/auth/login` |
| B3 | **Ciclo de Aprendizaje** | Estudiante | Inscribirse, estudiar, completar ejercicios y módulos | 1. Explorar módulos → 2. Inscribirse → 3. Ver lecciones → 4. Leer teoría → 5. Resolver ejercicios → 6. Enviar código → 7. Evaluación automática → 8. Recibir puntuación → 9. Completar lección → 10. Completar módulo → 11. Recibir logros | `GET /api/modules`, `POST /api/modules/{id}/enroll`, `GET /api/modules/{id}/lessons`, `POST /api/exercises/submit`, `POST /api/modules/complete`, `GET /api/achievements` |
| B4 | **Ejecución de Código Interactivo** | Estudiante | Ejecutar código Python en sandbox seguro | 1. Validar AST → 2. Verificar patrones peligrosos (string blacklist) → 3. Ejecutar en sandbox Docker (`CodeExecutor`) → 4. Capturar stdout/stderr → 5. Retornar resultado + acciones de robot | `POST /api/execute-code` |
| B5 | **Evaluación de Ejercicio** | Estudiante | Enviar solución y recibir calificación | 1. Buscar ejercicio (global o de clase) → 2. Obtener output esperado o test code → 3. Ejecutar en sandbox → 4. Comparar output (o ejecutar tests) → 5. Registrar intento (con retry ON CONFLICT) → 6. Si passed: otorgar puntos, actualizar progress, verificar logros, loguear evento → 7. Si no passed y 3+ intentos: ofrecer solución | `POST /api/exercises/submit` |
| B6 | **Solicitud de Docente** | Estudiante → Admin | Solicitar y aprobar/rechazar rol teacher | 1. Registro con request_teacher=true → 2. Admin revisa pending → 3. Admin aprueba/rechaza → 4. Role actualizado → 5. UI cambia para nuevo teacher | `POST /api/auth/register`, `GET /api/admin/teachers/pending`, `POST /api/admin/teachers/approve/{id}`, `POST /api/admin/teachers/reject/{id}` |
| B7 | **Creación y Publicación de Contenido** | Teacher → Admin | Teacher crea módulo, admin revisa y aprueba | 1. Teacher crea módulo (draft) → 2. Teacher agrega lecciones → 3. Teacher agrega ejercicios → 4. Teacher publica (PENDING_REVIEW) → 5. Admin revisa en content-review → 6. Admin aprueba (APPROVED) o rechaza (REJECTED) → 7. Módulo visible globalmente | `POST /api/modules`, `POST /api/modules/{id}/lessons`, `POST /api/modules/{id}/exercises`, `PUT /api/modules/{id}`, `GET /api/admin/content-review`, `POST /api/admin/modules/{id}/approve`, `POST /api/admin/modules/{id}/reject` |
| B8 | **Gestión de Aula Virtual** | Teacher | Crear clase, agregar módulos personalizados, gestionar estudiantes | 1. Crear clase → 2. Agregar módulos (con contenido propio) → 3. Publicar clase → 4. Recibir solicitudes de estudiantes → 5. Aprobar/rechazar inscripciones → 6. Ver progreso de estudiantes → 7. Desinscribir si necesario | `POST /api/classes`, `POST /api/classes/{id}/modules`, `GET /api/classes/{id}/requests`, `POST /api/classes/{id}/approve/{studentId}`, `DELETE /api/classes/{classId}/unenroll/{studentId}` |
| B9 | **Desafíos (Challenges)** | Teacher → Estudiante | Crear, publicar y resolver challenges de programación | 1. Teacher crea challenge (con base_code, solution, test, deadline) → 2. Estudiante explora challenges → 3. Estudiante envía solución → 4. Sistema evalúa → 5. Registra intento → 6. Si passed: puntos y logros | `POST /api/challenges`, `GET /api/challenges`, `POST /api/challenges/submit` |
| B10 | **Analítica Predictiva para Teachers** | Teacher | Visualizar dashboard de predicciones por estudiante | 1. Teacher accede a analytics → 2. Backend intenta obtener predicciones (timeout 5s) → 3. Si timeout: warm en background + respuesta parcial → 4. Consulta MongoDB para actividad y frustración → 5. Retorna dashboard completo o parcial | `GET /api/analytics/dashboard`, `GET /api/analytics/predictions/status`, `POST /api/analytics/predictions/prewarm` |
| B11 | **Pipeline ML** | Sistema (scheduled) | Entrenar y actualizar modelos predictivos semanalmente | 1. Generar dataset sintético (10K estudiantes x 16 semanas) → 2. Construir sliding windows (12 ventanas) → 3. Entrenar 4 modelos supervisados → 4. Entrenar 2 modelos no supervisados → 5. Evaluar en test set → 6. Persistir modelos en `models/` → 7. Generar reports JSON + MD | `ml_pipeline/run_all.py` (manual, `POST /api/analytics/train`) |
| B12 | **Chatbot Omnicanal** | Estudiante / Público | Recibir asistencia vía múltiples proveedores IA | 1. Enviar mensaje → 2. Intentar Dialogflow (si configurado) → 3. Si falla: intentar Ollama (IA local) → 4. Si falla: intentar OpenAI (opcional) → 5. Si todo falla: IntelligentTutor basado en reglas → 6. Log interacción en MongoDB | `POST /api/chatbot`, `POST /api/chatbot/public`, `GET /api/chatbot/status` |
| B13 | **Tutor Inteligente** | Estudiante | Obtener ayuda contextual durante ejercicios | 1. Detectar intención (saludo/pista/ejemplo/error/recomendación) → 2. Detectar nivel del estudiante (beginner/intermediate/advanced) → 3. Detectar frustración → 4. Generar prompt según intención+contexto → 5. Llamar a LLM (si disponible) → 6. Retornar respuesta + metadata | `POST /api/tutor/ask`, `POST /api/tutor/hint`, `POST /api/tutor/explain`, `GET /api/tutor/student-level` |
| B14 | **RAG (Búsqueda Semántica)** | Sistema (tutor) | Indexar y buscar contenido educativo | 1. Indexar: chunk texto → embed (Ollama) → almacenar en pgvector → 2. Buscar: embed query → cosine similarity → recuperar top-k chunks → construir contexto para LLM | `POST /api/ai/rag/index`, `POST /api/ai/rag/search` |
| B15 | **Sistema de Logros** | Estudiante | Desbloquear logros automáticamente | 1. Post-ejercicio o post-módulo → 2. Obtener todos los logros → 3. Para cada logro no obtenido: evaluar criterio (exercise_complete, module_complete, streak_days, etc.) → 4. Si cumple: insertar user_achievement, otorgar puntos → 5. Log evento | `check_and_award_achievements()` (llamado internamente) |
| B16 | **Snapshot Semanal** | Sistema (scheduled) | Persistir métricas semanales y generar predicciones | 1. APScheduler trigger → 2. Para cada estudiante activo: agregar métricas → 3. Persistir weekly_student_metrics → 4. Ejecutar ML predictions → 5. Persistir predictions en MongoDB | `AnalyticsScheduler.weekly_snapshot` (APScheduler) |
| B17 | **Aprobación de Eliminación de Módulo** | Teacher → Admin | Solicitar y aprobar eliminación de módulo | 1. Teacher solicita delete (status → PENDING_DELETION) → 2. Admin aprueba (eliminación real) o rechaza (status → APPROVED) | `DELETE /api/modules/{id}`, `POST /api/admin/modules/{id}/approve-deletion`, `POST /api/admin/modules/{id}/reject-deletion` |
| B18 | **Generación de Ejercicios por IA** | Teacher → Admin | Generar variantes de ejercicios con LLM y aprobar | 1. Teacher solicita sugerencia para un ejercicio → 2. LLM genera variante → 3. Sugerencia guardada como pendiente → 4. Admin revisa y aprueba/rechaza → 5. Si aprobada: ejercicio creado | `POST /api/ai/exercises/suggest`, `GET /api/ai/exercises/suggestions`, `POST /api/ai/exercises/suggestions/{id}/approve` |

---

## 5. APIs Consumidas (Externas)

| # | API Externa | Tecnología | Propósito | Endpoints/SDK Usados | Modo de Fallback | Archivo |
|---|-------------|-----------|-----------|---------------------|------------------|---------|
| E1 | **Google Dialogflow CX** | `google.cloud.dialogflow` SDK | Chatbot conversacional (primario) | `SessionsClient`, `session_path()`, `detect_intent()`, `TextInput(es)` | Ollama → IntelligentTutor | `ai_service_impl.py:52-72` |
| E2 | **Ollama (Local LLM)** | HTTP API (`httpx`) | Generación de texto, chat, embeddings (fallback primario) | `POST /api/generate`, `POST /api/chat`, `POST /api/embeddings`, `GET /api/tags` | IntelligentTutor | `llm_service.py:6-58` |
| E3 | **OpenAI** | `openai` SDK Python | Chat GPT (fallback terciario) | `openai.chat.completions.create()`, modelo `gpt-3.5-turbo` | IntelligentTutor | `main.py:1040-1060` |
| E4 | **Docker Engine** | `docker` SDK Python | Sandbox de ejecución de código | `docker.from_env()`, `containers.run()`, `container.wait()`, `container.logs()` | Sin fallback (error directo) | `code_executor.py:7-83` |
| E5 | **Redis** | `redis.asyncio` | Caché de respuestas IA, embeddings, rate limiting, blacklist de tokens | `from_url()`, `ping()`, `get()`, `setex()`, `incr()`, `expire()`, `scan()`, `delete()`, `exists()` | Degradación (sin caché, sin rate limit) | `cache.py`, `rate_limiter.py` |
| E6 | **PostgreSQL + pgvector** | `psycopg2` | Base de datos principal (usuarios, módulos, ejercicios, progreso, logros, RAG) | `ThreadedConnectionPool`, SQL crudo, stored procedures, pgvector para similitud coseno | Sin fallback (app no inicia) | `connection.py`, todos los repos Postgres |
| E7 | **MongoDB** | `pymongo` | Base de datos analítica (eventos, sesiones, métricas conductuales, predicciones ML) | `MongoClient`, insert_one, find, update_one, aggregate, count_documents, find_one_and_update | Degradación silenciosa (datos no persisten) | Todos los repos Mongo |

---

## 6. APIs Expuestas (144 Endpoints)

### 6.1 Health (2)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/` | ❌ | Root — mensaje de bienvenida + versión |
| GET | `/health` | ❌ | Healthcheck |

### 6.2 Autenticación (3)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | ❌ | Registro de usuario |
| POST | `/api/auth/login` | ❌ | Inicio de sesión |
| POST | `/api/auth/logout` | ✅ Token | Cierre de sesión |

### 6.3 Usuarios (5)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/users/profile` | ✅ Token | Obtener perfil del usuario actual |
| PUT | `/api/users/profile` | ✅ Token | Actualizar perfil |
| GET | `/api/users/by-public-id/{public_id}` | ❌ | Buscar por UUID público |
| GET | `/api/users/{user_id}` | ❌ | Obtener usuario por ID |
| GET | `/api/users/search` | ❌ | Buscar usuarios por nombre |
| GET | `/api/users/{user_id}/classes` | ❌ | Obtener clases de un usuario |

### 6.4 AI/ML Recomendaciones (3)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/recommendations` | ✅ Token | Recomendaciones personalizadas |
| GET | `/api/learning-path` | ✅ Token | Ruta de aprendizaje óptima |
| GET | `/api/performance-prediction/{module_id}` | ✅ Token | Predicción de rendimiento |

### 6.5 Analítica Predictiva (6)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/analytics/student/{student_id}/metrics` | ✅ Teacher | Métricas predictivas de un estudiante |
| GET | `/api/analytics/student/{student_id}/risk-factors` | ✅ Teacher | Factores de riesgo detallados |
| GET | `/api/analytics/dashboard` | ✅ Teacher | Dashboard analítico completo |
| GET | `/api/analytics/predictions/status` | ✅ Teacher | Estado de caché de predicciones |
| POST | `/api/analytics/predictions/prewarm` | ✅ Teacher | Pre-calcular predicciones |
| POST | `/api/analytics/train` | ✅ Admin | Retrain modelos (manual vía pipeline) |

### 6.6 Tutor Inteligente (5)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/tutor/ask` | ✅ Opcional | Preguntar al tutor |
| POST | `/api/tutor/hint` | ✅ Token | Solicitar pista |
| POST | `/api/tutor/explain` | ✅ Opcional | Explicar concepto |
| GET | `/api/tutor/student-level` | ✅ Token | Nivel detectado del estudiante |
| POST | `/api/tutor/feedback` | ✅ Token | Feedback sobre respuesta del tutor |

### 6.7 Chatbot (3)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/chatbot/status` | ❌ | Estado de servicios de IA |
| POST | `/api/chatbot/public` | ❌ | Chat público (sin auth) |
| POST | `/api/chatbot` | ✅ Token | Chat autenticado |

### 6.8 Ejecución de Código (1)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/execute-code` | ✅ Token | Ejecutar código Python en sandbox |

### 6.9 Ejercicios (4)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/exercises` | ✅ Token | Listar todos los ejercicios |
| POST | `/api/exercises/submit` | ✅ Token | Enviar solución de ejercicio |
| GET | `/api/exercises/{exercise_id}/attempts` | ✅ Token | Historial de intentos |
| GET | `/api/exercises/difficulty-analysis` | ✅ Teacher | Análisis de dificultad |

### 6.10 Módulos (18)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/modules` | ✅ Token | Listar módulos publicados |
| GET | `/api/modules/search` | ✅ Token | Buscar módulos |
| GET | `/api/modules/enrolled` | ✅ Token | Módulos en los que está inscrito |
| GET | `/api/modules/{id}` | ✅ Token | Detalle de módulo |
| POST | `/api/modules` | ✅ Teacher | Crear módulo |
| PUT | `/api/modules/{id}` | ✅ Teacher | Actualizar módulo |
| DELETE | `/api/modules/{id}` | ✅ Teacher | Solicitar eliminación |
| POST | `/api/modules/{id}/enroll` | ✅ Token | Inscribirse en módulo |
| POST | `/api/modules/complete` | ✅ Token | Marcar módulo como completado |
| GET | `/api/modules/{id}/progress` | ✅ Token | Progreso en módulo |
| GET | `/api/modules/{id}/lessons` | ✅ Token | Lecciones de un módulo |
| POST | `/api/modules/{id}/lessons` | ✅ Teacher | Crear lección |
| PUT | `/api/modules/{id}/lessons/{lesson_id}` | ✅ Teacher | Actualizar lección |
| DELETE | `/api/modules/{id}/lessons/{lesson_id}` | ✅ Teacher | Eliminar lección |
| POST | `/api/modules/{id}/exercises` | ✅ Teacher | Crear ejercicio en módulo |
| PUT | `/api/modules/{id}/exercises/{exercise_id}` | ✅ Teacher | Actualizar ejercicio |
| DELETE | `/api/modules/{id}/exercises/{exercise_id}` | ✅ Teacher | Eliminar ejercicio |
| GET | `/api/modules/{id}/exercises` | ✅ Token | Ejercicios de un módulo |

### 6.11 Lecciones (1)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/lessons/{lesson_id}/complete` | ✅ Token | Marcar lección completada |

### 6.12 Logros (2)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/achievements` | ✅ Token | Listar logros con estado |
| GET | `/api/achievements/recent` | ✅ Token | Logros recientes del usuario |

### 6.13 Eventos/Métricas (2)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/events` | ✅ Token | Loguear evento manual |
| GET | `/api/user-history` | ✅ Token | Historial de eventos del usuario |

### 6.14 Teacher Dashboard (7)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/teacher/dashboard` | ✅ Teacher | Dashboard del docente |
| GET | `/api/teacher/students` | ✅ Teacher | Estudiantes del docente |
| GET | `/api/teacher/students/{id}` | ✅ Teacher | Detalle de estudiante |
| GET | `/api/teacher/alerts` | ✅ Teacher | Alertas generadas por IA |
| GET | `/api/teacher/pending-enrollments` | ✅ Teacher | Inscripciones pendientes |
| POST | `/api/teacher/enrollments/approve` | ✅ Teacher | Aprobar inscripción |
| POST | `/api/teacher/enrollments/reject` | ✅ Teacher | Rechazar inscripción |

### 6.15 Admin (15)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/admin/users` | ✅ Admin | Listar todos los usuarios |
| PUT | `/api/admin/users/{id}/role` | ✅ Admin | Cambiar rol de usuario |
| GET | `/api/admin/teachers/pending` | ✅ Admin | Solicitudes de teacher pendientes |
| POST | `/api/admin/teachers/approve/{id}` | ✅ Admin | Aprobar teacher |
| POST | `/api/admin/teachers/reject/{id}` | ✅ Admin | Rechazar teacher |
| GET | `/api/admin/audit-logs` | ✅ Admin | Logs de auditoría |
| GET | `/api/admin/modules` | ✅ Admin | Todos los módulos (CRUD admin) |
| GET | `/api/admin/modules/{id}` | ✅ Admin | Detalle de módulo (admin) |
| POST | `/api/admin/modules/{id}/approve` | ✅ Admin | Aprobar módulo (content review) |
| POST | `/api/admin/modules/{id}/reject` | ✅ Admin | Rechazar módulo |
| PUT | `/api/admin/modules/{id}/content` | ✅ Admin | Editar contenido de módulo |
| GET | `/api/admin/content-review` | ✅ Admin | Contenido pendiente de revisión |
| POST | `/api/admin/modules/{id}/approve-deletion` | ✅ Admin | Aprobar eliminación de módulo |
| POST | `/api/admin/modules/{id}/reject-deletion` | ✅ Admin | Rechazar eliminación |
| POST | `/api/classes/{class_id}/unenroll/{student_id}` | ✅ Teacher | Desinscribir estudiante |

### 6.16 Dashboards (2)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/dashboard/student` | ✅ Token | Dashboard del estudiante |
| GET | `/api/dashboard/admin` | ✅ Admin | Dashboard del admin |

### 6.17 Challenges (7)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/challenges` | ✅ Token | Listar challenges |
| GET | `/api/challenges/{id}` | ✅ Token | Detalle de challenge |
| POST | `/api/challenges` | ✅ Teacher | Crear challenge |
| PUT | `/api/challenges/{id}` | ✅ Teacher | Actualizar challenge |
| DELETE | `/api/challenges/{id}` | ✅ Teacher | Eliminar challenge |
| POST | `/api/challenges/submit` | ✅ Token | Enviar solución de challenge |
| POST | `/api/challenges/{id}/submit` | (implícito) | (variante con ID en URL) |

### 6.18 Clases (25)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/classes` | ✅ Token | Listar clases disponibles |
| GET | `/api/classes/my-classes` | ✅ Teacher | Mis clases (teacher) |
| GET | `/api/classes/enrolled` | ✅ Token | Clases en las que estoy inscrito |
| GET | `/api/classes/{id}` | ✅ Token | Detalle de clase |
| POST | `/api/classes` | ✅ Teacher | Crear clase |
| PUT | `/api/classes/{id}` | ✅ Teacher | Actualizar clase |
| DELETE | `/api/classes/{id}` | ✅ Teacher | Eliminar clase |
| POST | `/api/classes/{id}/enroll` | ✅ Token | Solicitar inscripción |
| GET | `/api/classes/{id}/requests` | ✅ Teacher | Solicitudes de inscripción |
| POST | `/api/classes/{id}/approve/{student_id}` | ✅ Teacher | Aprobar estudiante |
| POST | `/api/classes/{id}/reject/{student_id}` | ✅ Teacher | Rechazar estudiante |
| GET | `/api/classes/{id}/modules` | ✅ Token | Módulos de una clase |
| GET | `/api/classes/{id}/modules/{module_id}` | ✅ Token | Detalle de módulo de clase |
| POST | `/api/classes/{id}/modules` | ✅ Teacher | Crear módulo en clase |
| PUT | `/api/classes/{id}/modules/{module_id}` | ✅ Teacher | Actualizar módulo de clase |
| DELETE | `/api/classes/{id}/modules/{module_id}` | ✅ Teacher | Eliminar módulo de clase |
| GET | `/api/classes/{id}/modules/{module_id}/exercises` | ✅ Token | Ejercicios de módulo de clase |
| POST | `/api/classes/{id}/modules/{module_id}/exercises` | ✅ Teacher | Crear ejercicio en clase |
| PUT | `/api/classes/{id}/modules/{module_id}/exercises/{ex_id}` | ✅ Teacher | Actualizar ejercicio de clase |
| DELETE | `/api/classes/{id}/modules/{module_id}/exercises/{ex_id}` | ✅ Teacher | Eliminar ejercicio de clase |
| POST | `/api/classes/{id}/modules/{module_id}/exercises/{ex_id}/submit` | ✅ Token | Enviar ejercicio de clase |

### 6.19 AI RAG / Tutor / Ejercicios (8)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/ai/rag/index` | ✅ Teacher | Indexar contenido en pgvector |
| POST | `/api/ai/rag/search` | ✅ Token | Búsqueda semántica RAG |
| POST | `/api/ai/tutor/ask-v2` | ✅ Token | Tutor v2 con RAG |
| POST | `/api/ai/tutor/hint` | ✅ Token | Pista v2 con RAG |
| POST | `/api/ai/exercises/suggest` | ✅ Teacher | Sugerir variante de ejercicio |
| GET | `/api/ai/exercises/suggestions` | ✅ Admin | Sugerencias pendientes |
| POST | `/api/ai/exercises/suggestions/{id}/approve` | ✅ Admin | Aprobar sugerencia |
| POST | `/api/ai/exercises/suggestions/{id}/reject` | ✅ Admin | Rechazar sugerencia |

### 6.20 Analytics (Router) (6)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/analytics/teacher-overview` | ✅ Teacher | Vista general del teacher |
| GET | `/api/analytics/admin-dashboard` | ✅ Admin | Dashboard admin |
| GET | `/api/analytics/student-evolution` | ✅ Teacher | Evolución de estudiantes |
| GET | `/api/analytics/module-performance/{module_id}` | ✅ Teacher | Rendimiento de módulo |
| GET | `/api/analytics/teacher/students` | ✅ Teacher | Lista estudiantes (analytics) |
| GET | `/api/analytics/student-progress/{student_id}` | ✅ Teacher | Progreso detallado |

### 6.21 Analytics Service Router (6)
| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| GET | `/api/analytics/student/{student_id}` | ✅ Teacher | Perfil analítico completo |
| GET | `/api/analytics/class/predictions` | ✅ Teacher | Predicciones por clase |
| GET | `/api/analytics/class/{class_id}` | ✅ Teacher | Analítica de clase |
| GET | `/api/analytics/risk-students` | ✅ Teacher | Estudiantes en riesgo |
| GET | `/api/analytics/clusters` | ✅ Teacher | Clusters de estudiantes |
| GET | `/api/analytics/anomalies` | ✅ Teacher | Detección de anomalías |

---

## 7. Flujos Principales

### 7.1 Flujo de Estudiante: Primer Uso
```
Landing (/) → Register → Login → Dashboard Student
                                          │
                                          ├─ Explorar Módulos → Inscribirse → Ver Lecciones
                                          │      → Leer Teoría → Resolver Ejercicios
                                          │      → Recibir Puntuación y Logros
                                          │
                                          ├─ Explorar Clases → Solicitar Inscripción
                                          │      → Esperar Aprobación Teacher
                                          │
                                          ├─ Challenges → Resolver → Subir Ranking
                                          │
                                          ├─ Chat/Tutor → Preguntar Dudas
                                          │
                                          └─ Mis Métricas → Revisar Progreso
```

### 7.2 Flujo de Docente: Gestión de Contenido
```
Login → Dashboard Teacher
          │
          ├─ Crear Clase → Agregar Módulos (contenido propio)
          │      → Publicar → Recibir Solicitudes
          │      → Aprobar Estudiantes
          │
          ├─ Crear Módulo (DRAFT) → Agregar Lecciones
          │      → Agregar Ejercicios → Publicar (PENDING_REVIEW)
          │      → Admin Revisa → APPROVED (visible globalmente)
          │
          ├─ Crear Challenge → Publicar (con deadline)
          │
          ├─ Analítica → Dashboard Predictivo
          │      → Ver Predicciones por Estudiante → Identificar Riesgos
          │      → Alertas IA → Tomar Acción
          │
          └─ Alertas → Revisar Notificaciones del Sistema
```

### 7.3 Flujo de Administrador: Gestión del Sistema
```
Login → Dashboard Admin
          │
          ├─ Solicitudes Docentes → Aprobar/Rechazar
          │
          ├─ Gestión de Usuarios → Buscar → Editar Roles
          │      → Activar/Desactivar
          │
          ├─ Revisión de Contenido → Aprobar/Rechazar Módulos
          │
          ├─ Auditoría → Revisar Logs → Ver Salud del Sistema
          │
          └─ Módulos → Editar directamente si es necesario
```

### 7.4 Flujo de Chatbot Omnicanal
```
Usuario envía mensaje
  │
  ├─ ¿Dialogflow configurado? → Sí → Intentar Dialogflow
  │                                   │
  │                                   ├─ Respuesta válida → Retornar (source: dialogflow)
  │                                   └─ Error/vacío → Continuar
  │
  ├─ Intentar Ollama (IA local)
  │     │
  │     ├─ Respuesta válida → Retornar (source: ollama)
  │     └─ No disponible → Continuar
  │
  ├─ ¿OpenAI configurado? → Sí → Intentar OpenAI
  │                           │
  │                           ├─ Respuesta válida → Retornar (source: openai)
  │                           └─ Error → Continuar
  │
  └─ IntelligentTutor (reglas) → Retornar (source: tutor)
```

### 7.5 Flujo de Evaluación de Ejercicio
```
Usuario envía código (POST /api/exercises/submit)
  │
  ├─ ¿Es ejercicio de clase?
  │     ├─ Sí → Buscar en class_exercises
  │     └─ No → Buscar en exercises globales
  │
  ├─ ¿Ya aprobado anteriormente?
  │     └─ Sí → Retornar "Ya habías resuelto este ejercicio"
  │
  ├─ SandboxService.execute_and_compare()
  │     ├─ Validar código (AST parse + blacklist)
  │     ├─ Ejecutar en Docker (timeout 10s, 64MB RAM, sin red)
  │     └─ Comparar stdout con solution_output
  │
  ├─ Registrar intento (ON CONFLICT DO NOTHING con retry)
  │
  ├─ ¿Passed?
  │     ├─ Sí → Otorgar puntos, actualizar progress
  │     │      → Verificar logros (check_and_award_achievements)
  │     │      → Log evento "exercise_passed"
  │     │
  │     └─ No → ¿3+ intentos? → Ofrecer solución
  │
  └─ Retornar resultado (passed, score, output, error, solution)
```

### 7.6 Flujo de Pipeline ML (Semanal)
```
APScheduler trigger (Domingo 23:59)
  │
  ├─ Para cada estudiante activo:
  │     ├─ Agregar métricas desde MongoDB (sesiones, ejercicios, eventos)
  │     └─ Persistir weekly_student_metrics
  │
  ├─ Ejecutar ML predictions:
  │     ├─ EngagementPredictor (RandomForestRegressor)
  │     ├─ PerformancePredictor (RandomForestRegressor)
  │     ├─ DropoutPredictor (RandomForestClassifier)
  │     ├─ FrustrationPredictor (RandomForestClassifier)
  │     ├─ LearningClustering (KMeans)
  │     └─ AnomalyDetector (IsolationForest)
  │
  └─ Persistir predictions en MongoDB
```

### 7.7 Flujo de Inicialización del Sistema
```
docker-compose up
  │
  ├─ postgres: init scripts (001-005.sql) → Schema + Seed Data
  ├─ mongo: init script → Colecciones iniciales
  ├─ redis: start → AOF persistence
  ├─ ollama: pull model → Download qwen2.5-coder:1.5b
  │
  └─ backend (lifespan):
        ├─ Cargar Google Credentials (si existen)
        ├─ initialize_database()
        │     ├─ Crear DB si no existe
        │     ├─ Ejecutar 001-init.sql (schema)
        │     ├─ Ejecutar 002-seed-data.sql (datos base)
        │     ├─ Ejecutar 003-seed-massive.sql (datos masivos, dev)
        │     └─ Ejecutar 005-enable-pgvector.sql
        ├─ Init PostgresConnection pool
        └─ Include analytics_router (lazy import numpy)
```

### 7.8 Flujo de Datos: Request → Response
```
Cliente (Browser) → Next.js (Middleware JWT check) → API Backend
  │
  ├─ Middleware HTTP:
  │     ├─ CORS (allow_origins configurable)
  │     ├─ Audit logging (rutas sensibles)
  │     └─ Security headers (CSP, HSTS, X-Frame-Options)
  │
  ├─ Dependencies:
  │     ├─ verify_token → Cookie "auth-token" → JWT decode → TokenData
  │     ├─ verify_teacher → Role check (teacher/admin)
  │     └─ verify_admin → Role check (admin)
  │
  ├─ Route Handler:
  │     ├─ Use Case → Service → Repository → Database
  │     │     └─ PostgreSQL (datos transaccionales)
  │     │     └─ MongoDB (datos analíticos)
  │     │     └─ Redis (caché, rate limit)
  │     │     └─ Docker (sandbox code)
  │     │     └─ Ollama (IA local)
  │     │     └─ Dialogflow (chatbot)
  │     │
  │     └─ Response (JSON) → Client
  │
  └─ Error Handling:
        ├─ AppException → JSON {success, error, code}
        ├─ HTTPException → JSON {success, error, code}
        └─ Unhandled Exception → 500 + log + JSON genérico
```

---

## Resumen

| Categoría | Cantidad |
|-----------|----------|
| **Módulos funcionales** | 22 |
| **Menús por rol** | 4 (público, estudiante, teacher, admin) |
| **Formularios** | 21 |
| **Procesos de negocio** | 18 |
| **APIs externas consumidas** | 7 |
| **Endpoints expuestos** | 144 |
| **Flujos principales** | 8 |

---

*Fin del reporte de Descubrimiento Funcional.*
