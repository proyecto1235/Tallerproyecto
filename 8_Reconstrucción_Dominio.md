# Reconstrucción del Dominio — RoboLearn (DDD)

**Proyecto:** RoboLearn  
**Rol:** Experto en Domain-Driven Design  
**Propósito:** Reconstruir el modelo de dominio, identificar entidades, value objects, servicios, agregados, repositorios, casos de uso y reglas de negocio. Incluye diagramas UML textuales.

---

## 1. Mapa del Dominio: Visión General

El sistema RoboLearn pertenece al dominio de **Educación Programática Asistida por IA**. Sus subdominios son:

| Subdominio | Tipo | Descripción |
|-----------|------|-------------|
| **Catálogo de Contenido** | Core | Módulos, lecciones, ejercicios, challenges — el activo educativo principal |
| **Gestión de Aprendizaje** | Core | Inscripciones, progreso, logros — seguimiento del estudiante |
| **Analítica Predictiva** | Core | Modelos ML que predicen engagement, rendimiento, deserción y frustración |
| **Tutoría Inteligente** | Core | Asistencia contextual vía IA (chatbot, pistas, explicaciones) |
| **Aulas Virtuales** | Soporte | Clases creadas por teachers con contenido personalizado |
| **Identidad y Acceso** | Soporte | Autenticación, roles (student/teacher/admin), autorización |
| **Eventos y Métricas** | Genérico | Tracking de comportamiento, sesiones, snapshots semanales |
| **Ejecución de Código** | Soporte | Sandbox para ejecutar código Python de forma segura |

### Diagrama de Contexto

```
┌─────────────────────────────────────────────────────────────┐
│                    ROBOLEARN (Sistema)                       │
│                                                             │
│  ┌──────────────────┐   ┌──────────────┐   ┌────────────┐  │
│  │  Catálogo de     │   │ Gestión de   │   │ Aulas      │  │
│  │  Contenido       │◄──│ Aprendizaje  │──►│ Virtuales  │  │
│  │  (Core)          │   │ (Core)       │   │ (Soporte)  │  │
│  └────────┬─────────┘   └──────┬───────┘   └────────────┘  │
│           │                    │                            │
│           ▼                    ▼                            │
│  ┌─────────────────────────────────────────────────┐       │
│  │           Tutoría Inteligente (Core)             │       │
│  │  (Dialogflow → Ollama → OpenAI → IntelligentTutor)│      │
│  └─────────────────────────────────────────────────┘       │
│           │                    │                            │
│           ▼                    ▼                            │
│  ┌──────────────────┐   ┌──────────────┐                   │
│  │  Analítica       │   │ Eventos y    │                   │
│  │  Predictiva      │──►│ Métricas     │                   │
│  │  (Core)          │   │ (Genérico)   │                   │
│  └──────────────────┘   └──────────────┘                   │
│                                                             │
│  ┌──────────────────┐   ┌──────────────┐                   │
│  │  Identidad y     │   │ Ejecución    │                   │
│  │  Acceso          │   │ de Código    │                   │
│  │  (Soporte)       │   │ (Soporte)    │                   │
│  └──────────────────┘   └──────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Entidades

### 2.1 User

```
┌─────────────────────────────────────────────────────┐
│                     User                             │
├─────────────────────────────────────────────────────┤
│ - id: Optional[int]                    (IDENTITY)    │
│ - public_id: str                       (UUID único)  │
│ - email: str                                         │
│ - password_hash: str                                 │
│ - full_name: str                                     │
│ - role: UserRole {STUDENT, TEACHER, ADMIN}           │
│ - is_active: bool                     (default True) │
│ - teacher_request_status: Optional<TeacherRequestStatus> │
│   {PENDING, APPROVED, REJECTED}                      │
│ - avatar_url: Optional[str]                          │
│ - bio: Optional[str]                                 │
│ - points: int                         (default 0)    │
│ - streak_days: int                    (default 0)    │
│ - created_at: datetime                               │
│ - updated_at: datetime                               │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

**Identidad:** `id` (autoincremental) o `public_id` (UUID).  
**Ciclo de vida:** Creado durante registro, actualizado vía perfil, desactivado por admin.  
**Reglas de negocio asociadas:**
- Un email debe ser único en el sistema.
- Un usuario con `teacher_request_status=PENDING` espera aprobación del admin.
- Solo admins pueden cambiar roles.
- `is_active=false` impide el login.

### 2.2 Module

```
┌─────────────────────────────────────────────────────┐
│                     Module                            │
├─────────────────────────────────────────────────────┤
│ - id: Optional[int]                    (IDENTITY)    │
│ - title: str                                         │
│ - description: str                                   │
│ - theory_content: Optional[str]                      │
│ - teacher_id: int                    (FK → User)     │
│ - status: ContentStatus {DRAFT, PENDING_REVIEW,      │
│            APPROVED, REJECTED, PENDING_DELETION}      │
│ - order: int                          (default 0)    │
│ - is_published: bool                  (default False)│
│ - difficulty: int                     (default 1)    │
│ - lesson_count: int                   (default 0)    │
│ - created_at: datetime                               │
│ - updated_at: datetime                               │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

**Identidad:** `id`.  
**Ciclo de vida:** Creado por teacher en DRAFT → enviado a PENDING_REVIEW → admin aprueba (APPROVED) o rechaza (REJECTED). Puede solicitarse eliminación (PENDING_DELETION → admin approve/reject).  
**Reglas de negocio:**
- Solo módulos APPROVED + is_published son visibles globalmente.
- Un teacher solo puede editar sus propios módulos.
- La eliminación requiere aprobación del admin.

### 2.3 Exercise

```
┌─────────────────────────────────────────────────────┐
│                    Exercise                           │
├─────────────────────────────────────────────────────┤
│ - id: Optional[int]                    (IDENTITY)    │
│ - module_id: int                     (FK → Module)   │
│ - lesson_id: Optional[int]          (FK → Lesson)    │
│ - title: str                                         │
│ - description: str                                   │
│ - instructions: str                                  │
│ - theory_content: Optional[str]                      │
│ - difficulty: int                      (1-5)         │
│ - points: int                         (default 100)  │
│ - order: int                          (default 0)    │
│ - solution_output: Optional[str]                     │
│ - solution_type: str                  (output/test)  │
│ - test_code: Optional[str]                           │
│ - metadata: Dict                                     │
│ - created_at: datetime                               │
│ - updated_at: datetime                               │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

**Identidad:** `id`.  
**Reglas de negocio:**
- `solution_type` determina el método de evaluación: "output" compara stdout, "test" ejecuta test_code.
- `difficulty` debe estar entre 1 y 5.
- `points` se otorgan al estudiante si pasa el ejercicio.

### 2.4 Challenge

```
┌─────────────────────────────────────────────────────┐
│                    Challenge                          │
├─────────────────────────────────────────────────────┤
│ - id: Optional[int]                    (IDENTITY)    │
│ - title: str                                         │
│ - description: str                                   │
│ - instructions: str                                  │
│ - teacher_id: int                    (FK → User)     │
│ - difficulty: int                      (1-5)         │
│ - points: int                         (default 100)  │
│ - base_code: Optional[str]                           │
│ - solution_code: Optional[str]                       │
│ - solution_type: str                                 │
│ - solution_output: Optional[str]                     │
│ - test_code: Optional[str]                           │
│ - deadline: Optional[datetime]                       │
│ - is_published: bool                                 │
│ - max_attempts: int                                  │
│ - created_at: datetime                               │
│ - updated_at: datetime                               │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

**Identidad:** `id`.  
**Reglas de negocio:**
- Los challenges tienen fecha límite (`deadline`).
- `max_attempts` limita los intentos del estudiante.
- Solo teachers pueden crear challenges.

### 2.5 Enrollment

```
┌─────────────────────────────────────────────────────┐
│                    Enrollment                         │
├─────────────────────────────────────────────────────┤
│ - id: Optional[int]                    (IDENTITY)    │
│ - student_id: int                    (FK → User)     │
│ - module_id: int                    (FK → Module)    │
│ - status: str                        (active/completed)│
│ - enrolled_at: Optional[datetime]                    │
│ - completed_at: Optional[datetime]                   │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

**Identidad:** `id`.  
**Reglas de negocio:**
- Un estudiante no puede inscribirse dos veces al mismo módulo.
- `status` cambia de "active" a "completed" cuando el estudiante completa todas las lecciones.
- Solo módulos APPROVED + is_published son inscribibles.

### 2.6 Achievement

```
┌─────────────────────────────────────────────────────┐
│                    Achievement                        │
├─────────────────────────────────────────────────────┤
│ - id: Optional[int]                    (IDENTITY)    │
│ - name: str                                          │
│ - description: str                                   │
│ - icon: Optional[str]                                │
│ - points: int                                        │
│ - criteria: Dict {type, count, ...}                  │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────┐
│                  UserAchievement                     │
├─────────────────────────────────────────────────────┤
│ - id: Optional[int]                    (IDENTITY)    │
│ - user_id: int                      (FK → User)      │
│ - achievement_id: int             (FK → Achievement) │
│ - earned_at: datetime                                │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

**Reglas de negocio:**
- `criteria` define qué debe lograr el estudiante (tipo: exercise_complete, module_complete, streak_days, challenge_complete, first_try, exercise_fail_then_pass).
- Un achievement solo puede ser otorgado una vez por estudiante (ON CONFLICT DO NOTHING).

### 2.7 Alert

```
┌─────────────────────────────────────────────────────┐
│                     Alert (Pydantic)                  │
├─────────────────────────────────────────────────────┤
│ - id: Optional[str]                                   │
│ - teacher_id: int                   (FK → User)      │
│ - student_id: Optional[int]                           │
│ - module_id: Optional[int]                            │
│ - type: AlertType {DIFFICULTY, SLOW_LEARNER,         │
│                     FAST_LEARNER}                     │
│ - priority: AlertPriority {HIGH, MEDIUM, LOW}        │
│ - message: str                                       │
│ - recommendations: List[str]                         │
│ - created_at: str                                    │
│ - student_name: Optional[str]                        │
│ - module_name: Optional[str]                         │
└─────────────────────────────────────────────────────┘
```

**Reglas de negocio:**
- Las alertas se generan dinámicamente (no se persisten).
- `DIFFICULTY` se activa si ≥40% de la clase tiene progreso <50% del promedio.
- `SLOW_LEARNER` se activa si progreso_velocity < 30% del promedio tras 7+ días.
- `FAST_LEARNER` se activa si progreso_velocity > 200% del promedio y progreso > 50%.

### 2.8 Lesson

```
┌─────────────────────────────────────────────────────┐
│                     Lesson (Implícita en SQL)          │
├─────────────────────────────────────────────────────┤
│ - id: int                              (IDENTITY)    │
│ - module_id: int                     (FK → Module)   │
│ - title: str                                         │
│ - theory_content: str  (markdown)                    │
│ - order: int                                         │
└─────────────────────────────────────────────────────┘
```

**Nota:** Lesson no tiene clase Python explícita en `domain/entities/` — se maneja como fila SQL y se mapea a dict en el código de `main.py`. Es una **entidad anémica** que debería formalizarse.

---

## 3. Value Objects

### 3.1 Progress

```
┌─────────────────────────────────────────────────────┐
│                    Progress (Value Object)            │
├─────────────────────────────────────────────────────┤
│ - user_id: int                        (contextual)   │
│ - module_id: int                       (contextual)  │
│ - percentage: float                    (0.0 - 100.0) │
│ - completed_exercises: int                           │
│ - total_exercises: int                               │
│ - points_earned: int                                 │
│ - last_activity: datetime                            │
│ - is_completed: bool                                 │
├─────────────────────────────────────────────────────┤
│ + update_progress(completed, total, points)           │
│ + to_dict(): dict                                    │
└─────────────────────────────────────────────────────┘
```

**Inmutabilidad:** No es estrictamente inmutable (tiene `update_progress()`) pero se comporta como VO porque **no tiene identidad propia** — se identifica por la combinación `(user_id, module_id)`. Su igualdad es por valor de sus atributos.

**Regla de negocio:** `percentage` debe estar entre 0 y 100. Se calcula como `(completed_exercises / total_exercises) * 100`.

### 3.2 StudentMetrics

```
┌─────────────────────────────────────────────────────┐
│                 StudentMetrics (VO)                   │
├─────────────────────────────────────────────────────┤
│ - student_id: int                     (contextual)   │
│ - session_days: int                   (default 0)    │
│ - total_sessions: int                 (default 0)    │
│ - total_time_minutes: float           (default 0.0)  │
│ - exercise_attempts: int              (default 0)    │
│ - passed_exercises: int               (default 0)    │
│ - error_rate: float                   (default 0.0)  │
│ - forum_interactions: int             (default 0)    │
│ - content_views: int                  (default 0)    │
│ - last_updated: Optional[datetime]                   │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
│ + from_dict(data): StudentMetrics       (classmethod) │
└─────────────────────────────────────────────────────┘
```

### 3.3 WeeklyStudentMetrics

```
┌─────────────────────────────────────────────────────┐
│               WeeklyStudentMetrics (VO)               │
├─────────────────────────────────────────────────────┤
│ - student_id: int                     (contextual)   │
│ - week_number: int                                   │
│ - year: int                                          │
│ - avg_session_days: float                            │
│ - avg_total_sessions: float                          │
│ - avg_total_time_minutes: float                      │
│ - avg_exercise_attempts: float                       │
│ - avg_passed_exercises: float                        │
│ - avg_error_rate: float                              │
│ - avg_forum_interactions: float                      │
│ - avg_content_views: float                           │
│ - engagement_score: float                            │
│ - performance_score: float                           │
│ - frustration_score: float                           │
│ - dropout_risk: float                                │
│ - cluster_id: int                                    │
│ - cluster_name: str                                  │
│ - created_at: Optional[datetime]                     │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
│ + from_dict(data): WeeklyStudentMetrics (classmethod) │
└─────────────────────────────────────────────────────┘
```

### 3.4 MLPrediction

```
┌─────────────────────────────────────────────────────┐
│                   MLPrediction (VO)                   │
├─────────────────────────────────────────────────────┤
│ - student_id: int                     (contextual)   │
│ - week_number: int                                   │
│ - predicted_engagement: float                        │
│ - predicted_performance: float                       │
│ - predicted_dropout_prob: float                      │
│ - predicted_frustration_level: int                   │
│ - cluster_id: int                                    │
│ - cluster_name: str                                  │
│ - anomaly_score: float                               │
│ - is_anomaly: bool                                   │
│ - feature_importances: Optional[Dict]                │
│ - created_at: Optional[datetime]                     │
├─────────────────────────────────────────────────────┤
│ + to_dict(): dict                                    │
│ + from_dict(data): MLPrediction        (classmethod) │
└─────────────────────────────────────────────────────┘
```

### 3.5 Enums (Value Objects Primitivos)

```
┌─────────────────────────────────────────────────────┐
│  UserRole (Enum)        │  TeacherRequestStatus      │
│  ─────────────          │  (Enum)                    │
│  STUDENT = "student"    │  ───────────────           │
│  TEACHER = "teacher"    │  PENDING = "pending"       │
│  ADMIN = "admin"        │  APPROVED = "approved"     │
│                         │  REJECTED = "rejected"     │
├─────────────────────────┴───────────────────────────┤
│  ContentStatus (Enum)   │  AlertType (Enum)          │
│  ────────────────       │  ──────────────            │
│  DRAFT = "draft"        │  DIFFICULTY = "difficulty" │
│  PENDING_REVIEW = ...   │  SLOW_LEARNER = "slow..."  │
│  APPROVED = "approved"  │  FAST_LEARNER = "fast..."  │
│  REJECTED = "rejected"  │                            │
│  PENDING_DELETION = ... │  AlertPriority (Enum)      │
│                         │  ────────────────          │
│                         │  HIGH = "high"             │
│                         │  MEDIUM = "medium"         │
│                         │  LOW = "low"               │
└─────────────────────────────────────────────────────┘
```

---

## 4. Servicios de Dominio

### 4.1 AIService (Port — Puerto de Dominio)

```
┌────────────────────────────────────────────────────────────┐
│                  «interface» AIService                       │
├────────────────────────────────────────────────────────────┤
│ + get_recommendations(user_id, history): List[Dict]         │
│ + chat_with_dialogflow(session_id, message): str            │
│ + predict_student_performance(student_id, module_id): float │
│ + detect_learning_path(student_id): Dict                    │
└────────────────────────────────────────────────────────────┘
```

**Propósito:** Puerto que define la interfaz para servicios de IA/ML del dominio. Implementado por `AIServiceImpl` en la capa de infraestructura.

### 4.2 SandboxService (Servicio de Dominio)

```
┌────────────────────────────────────────────────────────────┐
│                     SandboxService                           │
├────────────────────────────────────────────────────────────┤
│ - executor: CodeExecutor                                    │
├────────────────────────────────────────────────────────────┤
│ + validate_code(code): Optional[str]                       │
│ + execute_code(code): Dict                                 │
│ + execute_and_compare(code, expected, type, test): Dict    │
└────────────────────────────────────────────────────────────┘
```

**Propósito:** Ejecuta código Python de forma segura. Valida AST, chequea patrones peligrosos y delega a `CodeExecutor` (Docker).

### 4.3 IntelligentTutor (Servicio de Dominio)

```
┌────────────────────────────────────────────────────────────┐
│                     IntelligentTutor                         │
├────────────────────────────────────────────────────────────┤
│ - orchestrator: MLOrchestrator (opcional)                   │
│ - llm_tutor: AITutorService (opcional)                      │
├────────────────────────────────────────────────────────────┤
│ + detect_intent(message): Dict {intent, confidence}         │
│ + generate_response(message, profile, exercise, df): Dict  │
│ + generate_hint(exercise_id, data, profile): str            │
│ + get_student_level(profile): str                           │
└────────────────────────────────────────────────────────────┘
```

**Propósito:** Servicio de dominio que encapsula la lógica de detección de intención, adaptación al nivel del estudiante y detección de frustración. No depende de infraestructura directamente (usa LLM inyectado opcionalmente).

### 4.4 LLMService (Servicio de Infraestructura con Lógica de Dominio)

```
┌────────────────────────────────────────────────────────────┐
│                      LLMService                              │
├────────────────────────────────────────────────────────────┤
│ - base_url: str                          (Ollama URL)       │
│ - model: str                              (model ID)        │
│ - _client: httpx.AsyncClient                               │
├────────────────────────────────────────────────────────────┤
│ + generate(prompt, system, temperature, max_tokens): str   │
│ + chat(messages, temperature, max_tokens): str             │
│ + embed(text): List[float]                                 │
│ + is_available(): bool                                     │
└────────────────────────────────────────────────────────────┘
```

### 4.5 MLOrchestrator (Servicio de Dominio)

```
┌────────────────────────────────────────────────────────────┐
│                     MLOrchestrator                           │
├────────────────────────────────────────────────────────────┤
│ - _prediction_cache: Dict                                   │
│ - predictores: EngagementPredictor, PerformancePredictor,   │
│   DropoutPredictor, FrustrationPredictor,                  │
│   LearningClustering, AnomalyDetector, Recommender         │
├────────────────────────────────────────────────────────────┤
│ + predict_student(student_id): Dict                        │
│ + predict_batch(student_ids): Dict                         │
│ + predict_class(student_ids): Dict                         │
│ + reload_models(): bool                                    │
│ + cache_status(): Dict                                     │
│ + feature_importances(): Dict                              │
└────────────────────────────────────────────────────────────┘
```

**Propósito:** Orquesta 6 modelos ML para generar predicciones por estudiante. Es un **servicio de dominio** porque encapsula lógica de negocio predictiva.

### 4.6 RAGService (Servicio de Dominio)

```
┌────────────────────────────────────────────────────────────┐
│                       RAGService                             │
├────────────────────────────────────────────────────────────┤
│ - embedding_service: EmbeddingService                       │
│ - llm_service: LLMService                                   │
├────────────────────────────────────────────────────────────┤
│ + index_content(text, source_type, source_id, metadata)    │
│ + search(query, top_k, source_type): List[Dict]            │
│ + build_context(query, top_k): str                         │
└────────────────────────────────────────────────────────────┘
```

### 4.7 ExerciseGeneratorService (Servicio de Dominio)

```
┌────────────────────────────────────────────────────────────┐
│                 ExerciseGeneratorService                     │
├────────────────────────────────────────────────────────────┤
│ - llm_service: LLMService                                   │
├────────────────────────────────────────────────────────────┤
│ + generate_suggestion(exercise_id, exercise_data): Dict    │
│ + get_pending_suggestions(): List[Dict]                    │
│ + approve_suggestion(suggestion_id): bool                  │
│ + reject_suggestion(suggestion_id): bool                   │
└────────────────────────────────────────────────────────────┘
```

**Propósito:** Genera variantes de ejercicios usando LLM, con flujo de aprobación admin.

---

## 5. Reglas de Negocio (Business Rules)

| ID | Regla | Tipo | Entidad(es) | Archivo |
|----|-------|------|-------------|---------|
| BR1 | Un email debe ser único en el sistema | **Invariante** | User | `register_user.py:27-29` |
| BR2 | La contraseña debe tener al menos 6 caracteres | **Validación** | User | `register_user.py:23-24` |
| BR3 | Un usuario inactivo no puede iniciar sesión | **Invariante** | User | `main.py:213-214` |
| BR4 | Solo admins pueden cambiar roles de usuario | **Autorización** | User | `main.py:2482-2500` |
| BR5 | Un teacher no puede editar módulos de otros teachers | **Autorización** | Module | `main.py:2334-2335` |
| BR6 | La eliminación de un módulo requiere aprobación admin | **Proceso** | Module | `main.py:2354-2379` |
| BR7 | Un módulo debe estar APPROVED + is_published para ser visible globalmente | **Invariante** | Module | `main.py:2133` |
| BR8 | Un estudiante no puede inscribirse dos veces al mismo módulo | **Invariante** | Enrollment | `enroll_student.py:39-41` |
| BR9 | Módulos no publicados no son inscribibles | **Validación** | Module, Enrollment | `enroll_student.py:35-36` |
| BR10 | Un módulo se completa cuando todas las lecciones están completadas | **Invariante** | Module, Lesson | `main.py:1597-1606` |
| BR11 | Después de 3 intentos fallidos, se muestra la solución al estudiante | **Regla de presentación** | Exercise | `main.py:1339-1342` |
| BR12 | La dificultad de un ejercicio debe estar entre 1 y 5 | **Validación** | Exercise | (schema implícito) |
| BR13 | El progreso es el ratio ejercicios completados / totales * 100 | **Cálculo** | Progress | `progress.py:23` |
| BR14 | Un logro solo puede otorgarse una vez por estudiante | **Invariante** | Achievement | `dependencies.py:291-293` |
| BR15 | Alertas DIFFICULTY requieren ≥3 estudiantes y ≥40% con bajo progreso | **Regla de generación** | Alert | `generate_ai_alerts.py:77` |
| BR16 | SLOW_LEARNER requiere 7+ días inscrito y velocidad <30% del promedio | **Regla de generación** | Alert | `generate_ai_alerts.py:97` |
| BR17 | FAST_LEARNER requiere velocidad >200% del promedio y progreso >50% | **Regla de generación** | Alert | `generate_ai_alerts.py:117` |
| BR18 | El código ejecutado en el sandbox no debe contener patrones peligrosos (os, subprocess, eval, exec, open, socket, etc.) | **Seguridad** | Code Execution | `sandbox_service.py:9-14` |
| BR19 | El sandbox Docker tiene restricciones: 64MB RAM, 0.5 CPU, sin red, solo lectura, sin new-privileges | **Seguridad** | Code Execution | `code_executor.py:10,36-41` |
| BR20 | El token JWT expira después de `ACCESS_TOKEN_EXPIRE_MINUTES` (default 7 días) | **Seguridad** | Auth | `dependencies.py:117-118` |

---

## 6. Agregados

### 6.1 Aggregate Root: Module

```
┌─────────────────────────────────────────────────────────────┐
│              «Aggregate Root» Module                         │
├─────────────────────────────────────────────────────────────┤
│  Module {id, title, description, teacher_id, status, ...}   │
│      │                                                       │
│      ├── Lesson[] {id, title, theory_content, order}        │
│      │     │                                                 │
│      │     └── Exercise[] {id, title, difficulty, points,   │
│      │                      solution_output, test_code, ...} │
│      │                                                       │
│      └── Enrollment[] {student_id, status, enrolled_at, ...} │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Entidades internas:** Lesson, Exercise.  
**Entidades externas referenciadas:** Enrollment (referencia `module_id`), User (referencia `teacher_id`).  
**Invariantes del agregado:**
- `status` sigue el workflow: DRAFT → PENDING_REVIEW → APPROVED/REJECTED (o PENDING_DELETION).
- El `order` de lecciones y ejercicios debe ser secuencial.
- `lesson_count` se actualiza automáticamente al crear/eliminar lecciones.

### 6.2 Aggregate Root: User

```
┌─────────────────────────────────────────────────────────────┐
│              «Aggregate Root» User                           │
├─────────────────────────────────────────────────────────────┤
│  User {id, email, password_hash, role, points, ...}         │
│      │                                                       │
│      ├── UserAchievement[] {achievement_id, earned_at}      │
│      │                                                       │
│      ├── Enrollment[]  (referencia vía student_id)           │
│      │                                                       │
│      ├── ExerciseAttempt[] (referencia vía student_id)       │
│      │                                                       │
│      ├── Progress[] (referencia vía user_id)                 │
│      │                                                       │
│      ├── ChallengeAttempt[] (referencia vía student_id)      │
│      │                                                       │
│      └── LessonCompletion[] (referencia vía student_id)      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Entidades internas:** UserAchievement.  
**Entidades externas referenciadas:** Enrollment, ExerciseAttempt, Progress, ChallengeAttempt, LessonCompletion.  
**Invariantes:**
- `points` aumenta con cada ejercicio pasado y logro obtenido.
- `streak_days` refleja la racha de actividad diaria.

### 6.3 Aggregate Root: Class (Aula Virtual)

```
┌─────────────────────────────────────────────────────────────┐
│              «Aggregate Root» Class                          │
├─────────────────────────────────────────────────────────────┤
│  Class {id, title, description, teacher_id, category,       │
│         difficulty, is_published, ...}                       │
│      │                                                       │
│      ├── ClassModule[] {title, description, theory_content, │
│      │                    order}                              │
│      │     │                                                 │
│      │     └── ClassExercise[] {title, instructions,         │
│      │                          difficulty, points, ...}      │
│      │                                                       │
│      └── ClassEnrollment[] {student_id, status,             │
│                              enrolled_at}                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Nota:** Class no tiene clase Python explícita en `domain/entities/` — se maneja completamente en SQL y `main.py`.

### 6.4 Aggregate Root: Challenge

```
┌─────────────────────────────────────────────────────────────┐
│              «Aggregate Root» Challenge                       │
├─────────────────────────────────────────────────────────────┤
│  Challenge {id, title, description, instructions,           │
│             teacher_id, difficulty, points, ...}             │
│      │                                                       │
│      └── ChallengeAttempt[] {student_id, passed, score,     │
│                               attempt_count, ...}            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.5 Diagrama de Agregados y Relaciones

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Module    │     │    User      │     │  Challenge  │
│  (Root)     │     │   (Root)     │     │   (Root)    │
├─────────────┤     ├──────────────┤     ├─────────────┤
│ - id        │     │ - id         │     │ - id        │
│ - title     │     │ - email      │     │ - title     │
│ - teacher_id│────►│ - role       │◄────│ - teacher_id│
│ - status    │     │ - points     │     │ - deadline  │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                     │
       │  ┌────────────────┼─────────────────────┘
       │  │                │
       ▼  ▼                ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Lesson     │    │  Enrollment  │    │   Progress   │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ - id         │    │ - student_id │    │ - user_id    │
│ - module_id  │    │ - module_id  │    │ - module_id  │
│ - order      │    │ - status     │    │ - percentage │
└──────┬───────┘    └──────────────┘    └──────────────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Exercise   │    │  Exercise    │    │  User        │
├──────────────┤    │  Attempt     │    │  Achievement │
│ - id         │    ├──────────────┤    ├──────────────┤
│ - lesson_id  │    │ - student_id │    │ - user_id    │
│ - difficulty │    │ - exercise_id│    │ - achievement│
│ - points     │    │ - passed     │    │ - earned_at  │
└──────────────┘    └──────────────┘    └──────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    Class     │    │ ClassModule  │    │ ClassExercise│
│   (Root)     │───►├──────────────┤───►├──────────────┤
├──────────────┤    │ - class_id   │    │ - class_mod  │
│ - id         │    │ - order      │    │ - difficulty │
│ - teacher_id │    └──────────────┘    └──────────────┘
│ - category   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ ClassEnrollment  │
├──────────────────┤
│ - student_id     │
│ - class_id       │
│ - status         │
└──────────────────┘
```

---

## 7. Repositorios (Ports)

### 7.1 UserRepository

```
┌────────────────────────────────────────────────────────────┐
│             «interface» UserRepository                      │
├────────────────────────────────────────────────────────────┤
│  + create(user: User) → User                               │
│  + get_by_id(user_id: int) → Optional[User]                │
│  + get_by_email(email: str) → Optional[User]               │
│  + list_all() → List[User]                                 │
│  + update(user: User) → User                               │
│  + get_by_public_id(public_id: str) → Optional[User]       │
│  + delete(user_id: int) → bool                             │
└────────────────────────────────────────────────────────────┘
```

**Implementación:** `UserRepositoryImpl` (PostgreSQL)

### 7.2 ModuleRepository

```
┌────────────────────────────────────────────────────────────┐
│             «interface» ModuleRepository                    │
├────────────────────────────────────────────────────────────┤
│  + create(module: Module) → Module                         │
│  + get_by_id(module_id: int) → Optional[Module]            │
│  + get_by_teacher(teacher_id: int) → List[Module]          │
│  + list_published() → List[Module]                         │
│  + update(module: Module) → Module                         │
│  + delete(module_id: int) → bool                           │
└────────────────────────────────────────────────────────────┘
```

**Implementación:** `ModuleRepositoryImpl` (PostgreSQL)

### 7.3 EnrollmentRepository

```
┌────────────────────────────────────────────────────────────┐
│             «interface» EnrollmentRepository                │
├────────────────────────────────────────────────────────────┤
│  + create(enrollment: Enrollment) → Enrollment             │
│  + get_by_id(enrollment_id: int) → Optional[Enrollment]    │
│  + get_by_student_and_module(student_id, module_id) → ... │
│  + get_by_student(student_id: int) → List[Enrollment]     │
│  + get_by_module(module_id: int) → List[Enrollment]       │
│  + update(enrollment: Enrollment) → Enrollment             │
│  + delete(enrollment_id: int) → bool                      │
└────────────────────────────────────────────────────────────┘
```

**Implementación:** `EnrollmentRepositoryImpl` (PostgreSQL)

### 7.4 TeacherRepository

```
┌────────────────────────────────────────────────────────────┐
│             «interface» TeacherRepository                   │
├────────────────────────────────────────────────────────────┤
│  + get_teacher_students(teacher_id) → List[Dict]           │
│  + get_teacher_metrics(teacher_id) → Dict                  │
│  + get_student_details(teacher_id, student_id) → Optional  │
└────────────────────────────────────────────────────────────┘
```

**Implementación:** `TeacherRepositoryImpl` (PostgreSQL + stored procedures)

### 7.5 EventRepository (Infraestructura, no es puerto formal)

```
┌────────────────────────────────────────────────────────────┐
│                     EventRepository                          │
├────────────────────────────────────────────────────────────┤
│  + log_event(event_type, user_id, data) → str              │
│  + get_user_events(user_id) → List                         │
│  + get_user_exercise_history(user_id) → List               │
│  + log_chat_interaction(user_id, message, response, sess)  │
│  + log_exercise_attempt(user_id, exercise_id, data)        │
│  + log_progress_snapshot(student_id, module_id, data)      │
│  + close()                                                  │
└────────────────────────────────────────────────────────────┄
```

### 7.6 Repositorios de Infraestructura (MongoDB)

```
┌────────────────────────────────────────────────────────────┐
│  BehavioralRepository (MongoDB)                             │
│  ─────────────────────────────                              │
│  + get_db() → DB                                            │
│  + log_session_start/activity/end(user_id, session_id)     │
│  + log_exercise_action(user_id, exercise_id, action, meta) │
│  + log_frustration_signal(user_id, exercise_id, type, det) │
│  + log_code_analysis(user_id, exercise_id, code, error)    │
│  + update_engagement_score(user_id, module_id) → Dict      │
│  + get_student_behavioral_profile(user_id) → Dict          │
│  + close()                                                  │
├────────────────────────────────────────────────────────────┤
│  MLPredictionsRepository (MongoDB)                          │
│  ──────────────────────────────────────                    │
│  + save_prediction(prediction: MLPrediction)               │
│  + get_prediction(student_id, week_number) → MLPrediction  │
│  + get_latest_prediction(student_id) → MLPrediction        │
│  + get_student_predictions(student_id) → List[MLPrediction]│
│  + get_predictions_by_week(week_number) → List             │
├────────────────────────────────────────────────────────────┤
│  StudentMetricsRepository (MongoDB)                         │
│  ────────────────────────────────────────                  │
│  + save_metrics(metrics: StudentMetrics)                   │
│  + get_metrics(student_id) → StudentMetrics                │
│  + get_all_metrics() → List[StudentMetrics]                │
├────────────────────────────────────────────────────────────┤
│  WeeklyMetricsRepository (MongoDB)                          │
│  ──────────────────────────────────────                    │
│  + save_weekly_metrics(metrics: WeeklyStudentMetrics)      │
│  + get_weekly_metrics(student_id, week, year) → Metrics    │
│  + get_student_weekly_metrics(student_id) → List           │
│  + get_class_trends(module_id, week, year) → List          │
└────────────────────────────────────────────────────────────┘
```

---

## 8. Casos de Uso

### 8.1 RegisterUserUseCase

```
┌────────────────────────────────────────────────────────────┐
│               RegisterUserUseCase                           │
├────────────────────────────────────────────────────────────┤
│  Dependencias: UserRepository                               │
├────────────────────────────────────────────────────────────┤
│  execute(email, password, full_name, request_teacher)       │
│  ───────────────────────────────────────────────             │
│  1. Validar campos requeridos  ← BR1, BR2                   │
│  2. Verificar email no duplicado                            │
│  3. Hash password (bcrypt)                                  │
│  4. Crear entidad User (STUDENT, opcionalmente PENDING)     │
│  5. Persistir en UserRepository                             │
│  6. Retornar {success, user, teacher_request_pending}       │
└────────────────────────────────────────────────────────────┘
```

### 8.2 EnrollStudentUseCase

```
┌────────────────────────────────────────────────────────────┐
│               EnrollStudentUseCase                           │
├────────────────────────────────────────────────────────────┤
│  Dependencias: UserRepository, ModuleRepository,           │
│                EnrollmentRepository, EventRepository        │
├────────────────────────────────────────────────────────────┤
│  execute(student_id, module_id)                             │
│  ──────────────────────────────────                         │
│  1. Validar que el estudiante existe  ← BR8                 │
│  2. Validar que el módulo existe y está publicado  ← BR9    │
│  3. Verificar que no hay enrollment duplicado  ← BR8        │
│  4. Crear Enrollment (status="active")                      │
│  5. Persistir en EnrollmentRepository                       │
│  6. Log evento (fire-and-forget, no crítico)                │
│  7. Retornar {success, enrollment}                          │
└────────────────────────────────────────────────────────────┘
```

### 8.3 GetRecommendationsUseCase

```
┌────────────────────────────────────────────────────────────┐
│               GetRecommendationsUseCase                      │
├────────────────────────────────────────────────────────────┤
│  Dependencias: AIService, ModuleRepository,                 │
│                EventRepository                               │
├────────────────────────────────────────────────────────────┤
│  execute(user_id)                                           │
│  ──────────────────                                         │
│  1. Obtener historial de ejercicios del usuario             │
│  2. Llamar a AIService.get_recommendations(history)         │
│  3. Enriquecer cada recomendación con datos del módulo      │
│  4. Log evento "recommendations_retrieved"                  │
│  5. Retornar {success, recommendations}                     │
└────────────────────────────────────────────────────────────┘
```

### 8.4 TeacherDashboardUseCase

```
┌────────────────────────────────────────────────────────────┐
│               TeacherDashboardUseCase                        │
├────────────────────────────────────────────────────────────┤
│  Dependencias: TeacherRepository                            │
├────────────────────────────────────────────────────────────┤
│  get_students(teacher_id)                                   │
│  ──────────────────────────                                  │
│  1. Delegar a TeacherRepository.get_teacher_students()      │
│  2. Retornar {success, students}                            │
│                                                             │
│  get_metrics(teacher_id)                                    │
│  ─────────────────────────                                   │
│  1. Delegar a TeacherRepository.get_teacher_metrics()       │
│  2. Retornar {success, metrics}                             │
│                                                             │
│  get_student_detail(teacher_id, student_id)                 │
│  ──────────────────────────────────────────                  │
│  1. Delegar a TeacherRepository.get_student_details()       │
│  2. Retornar {success, student} o error si no pertenece     │
└────────────────────────────────────────────────────────────┘
```

### 8.5 GenerateAIAlertsUseCase

```
┌────────────────────────────────────────────────────────────┐
│               GenerateAIAlertsUseCase                        │
├────────────────────────────────────────────────────────────┤
│  Dependencias: TeacherRepository                            │
├────────────────────────────────────────────────────────────┤
│  execute(teacher_id)                                        │
│  ──────────────────────                                      │
│  1. Obtener estudiantes del teacher agrupados por módulo    │
│  2. Para cada módulo:                                       │
│     a. Calcular promedio de progreso y velocidad            │
│     b. ¿≥40% clase con progreso <50% del promedio?          │
│        → Alert(DIFFICULTY, HIGH)  ← BR15                    │
│  3. Para cada estudiante:                                   │
│     a. ¿7+ días y velocidad <30% del promedio?              │
│        → Alert(SLOW_LEARNER, MEDIUM)  ← BR16               │
│     b. ¿Velocidad >200% del promedio y progreso >50%?      │
│        → Alert(FAST_LEARNER, LOW)  ← BR17                  │
│  4. Ordenar por prioridad (HIGH → MEDIUM → LOW)            │
│  5. Retornar {success, alerts}                              │
└────────────────────────────────────────────────────────────┘
```

### 8.6 Use Cases No Formalizados (en main.py)

Además de los 5 casos de uso formales en `application/useCases/`, existen múltiples operaciones que son casos de uso implícitos dentro de `main.py`:

| Operación | Descripción | Endpoint |
|-----------|-------------|----------|
| SubmitExercise | Evaluar código, registrar intento, actualizar progreso, otorgar puntos, verificar logros | `POST /api/exercises/submit` |
| SubmitClassExercise | Igual pero para ejercicios de clase | `POST /api/classes/{id}/modules/{mid}/exercises/{eid}/submit` |
| SubmitChallenge | Evaluar solución de challenge, contar intentos, verificar límites | `POST /api/challenges/submit` |
| CompleteModule | Verificar lecciones completadas, marcar enrollment como completed, otorgar puntos | `POST /api/modules/complete` |
| CompleteLesson | Marcar lección como completada, actualizar engagement | `POST /api/lessons/{id}/complete` |
| ExecuteCode | Validar, ejecutar en sandbox, retornar resultado | `POST /api/execute-code` |
| ChatWithAI | Orquestar Dialogflow → Ollama → OpenAI → IntelligentTutor | `POST /api/chatbot` |
| TutorAsk | Detectar intención, nivel, frustración, generar respuesta | `POST /api/tutor/ask` |
| CheckAndAwardAchievements | Evaluar todos los criterios de logros no obtenidos | (llamado internamente) |
| WarmPredictions | Calcular predicciones en background para dashboard | `POST /api/analytics/predictions/prewarm` |
| GenerateExerciseSuggestion | LLM genera variante de ejercicio, guarda pendiente | `POST /api/ai/exercises/suggest` |
| IndexRAGContent | Chunk + embed + store en pgvector | `POST /api/ai/rag/index` |

---

## 9. Diagrama de Arquitectura Hexagonal (DDD Layers)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERFACES DE USUARIO                        │
│  (Next.js Pages + Components)                                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  /dashboard/*  |  /login  |  /register  |  Chat Widget     │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP (fetch credentials: include)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CAPA DE APLICACIÓN                              │
│  (FastAPI Routes + Middleware + Dependencies)                        │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Use Cases                                                    │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │   │
│  │  │RegisterUser  │ │EnrollStudent │ │GetRecommendations    │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘  │   │
│  │  ┌──────────────┐ ┌──────────────────────────────────────┐  │   │
│  │  │TeacherDashbrd│ │GenerateAIAlerts                      │  │   │
│  │  └──────────────┘ └──────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ SubmitExercise | SubmitChallenge | CompleteModule    │  │   │
│  │  │ ChatWithAI | TutorAsk | ExecuteCode                 │  │   │
│  │  │ WarmPredictions | IndexRAG | GenerateSuggestion     │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Application Services (orquestación, no lógica de dominio)   │   │
│  │  AITutorService | ExerciseGeneratorService                  │   │
│  │  SandboxService | AnalyticsScheduler | MetricsService        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CAPA DE DOMINIO                                │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  ENTITIES    │  │ VALUE OBJECTS│  │  DOMAIN SERVICES         │  │
│  │              │  │              │  │                          │  │
│  │  • User      │  │ • Progress   │  │  • IntelligentTutor      │  │
│  │  • Module    │  │ • StudentMet │  │  • MLOrchestrator         │  │
│  │  • Exercise  │  │ • WeeklyStu  │  │  • RAGService             │  │
│  │  • Challenge │  │ • MLPredict  │  │  • LLMService             │  │
│  │  • Enrollment│  │ • Enums (7)  │  │                          │  │
│  │  • Achievemt │  │              │  │                          │  │
│  │  • Alert     │  │              │  │                          │  │
│  │  • UserAchiev│  │              │  │                          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  PORTS (Repositories)                                         │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │   │
│  │  │UserRepository│ │ModuleRepo    │ │EnrollmentRepository  │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘  │   │
│  │  ┌──────────────┐ ┌──────────────────────────────────────┐  │   │
│  │  │TeacherRepo   │ │AIService (Domain Port)               │  │   │
│  │  └──────────────┘ └──────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE INFRAESTRUCTURA                           │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  ADAPTADORES DE SALIDA (Output Adapters)                     │   │
│  │                                                              │   │
│  │  PostgreSQL:                                                  │   │
│  │  • UserRepositoryImpl  • ModuleRepositoryImpl                │   │
│  │  • EnrollmentRepositoryImpl  • TeacherRepositoryImpl          │   │
│  │  • PostgresConnection (pool)  • ProcedureRunner              │   │
│  │                                                              │   │
│  │  MongoDB:                                                     │   │
│  │  • EventRepositoryImpl  • BehavioralRepository               │   │
│  │  • MLPredictionsRepository  • StudentMetricsRepository       │   │
│  │  • WeeklyMetricsRepository                                   │   │
│  │                                                              │   │
│  │  Redis:                                                       │   │
│  │  • AICache  • RateLimiter                                    │   │
│  │                                                              │   │
│  │  Docker:                                                      │   │
│  │  • CodeExecutor (sandbox)                                    │   │
│  │                                                              │   │
│  │  ML Models (scikit-learn):                                    │   │
│  │  • EngagementPredictor  • PerformancePredictor               │   │
│  │  • DropoutPredictor  • FrustrationPredictor                  │   │
│  │  • LearningClustering  • AnomalyDetector  • Recommender      │   │
│  │  • FeatureExtractor  • SyntheticDataset                      │   │
│  │                                                              │   │
│  │  AI Services:                                                  │   │
│  │  • AIServiceImpl (Dialogflow + scikit-learn)                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  CONFIGURACIÓN                                                │   │
│  │  • config/settings.py  (Pydantic BaseSettings)                │   │
│  │  • config/database_init.py  (Auto-migration)                  │   │
│  │  • scripts/*.sql  (Schema + Stored Procedures + Seeds)        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10. Análisis DDD: Cumplimiento y Desviaciones

### ✅ Aciertos DDD

| Aspecto | Estado | Evidencia |
|---------|--------|-----------|
| **Entidades anémicas** | ❌ **Problema** | `Exercise`, `Challenge`, `Enrollment`, `Achievement` son solo contenedores de datos sin comportamiento |
| **Agregados correctos** | ✅ Parcial | `Module` es el mejor agregado (raíz con Lessons + Exercises). `User` es agregado pero sin lazy loading de relaciones. `Class` no está formalizado como entidad. |
| **Value Objects correctos** | ✅ Parcial | `Progress` tiene validación (`percentage 0-100`). `StudentMetrics` y `MLPrediction` son inmutables vía dataclass. |
| **Puertos abstractos** | ✅ Correcto | 5 interfaces `Repository` + 1 `AIService` correctamente definidos en `domain/ports/` |
| **Inversión de dependencias** | ✅ Correcto | Casos de uso reciben puertos por inyección (`__init__`), infraestructura implementa puertos |
| **Casos de uso granulares** | ✅ Parcial | 5 casos de uso formales, pero la mayoría de la lógica está en `main.py` como handlers |
| **Lógica de dominio fuera de entidades** | ❌ **Problema** | `check_and_award_achievements()` está en `dependencies.py` y `main.py` (duplicado), no en el dominio |
| **Bounded Context** | ❌ **No definido** | No hay separación explícita entre contextos (learning, analytics, auth comparten el mismo código) |

### ⚠️ Desviaciones y Riesgos

| # | Problema | Impacto |
|---|----------|---------|
| 1 | **Lógica de negocio en `main.py`** — 4000+ líneas con rutas, orquestación, SQL y validación mezclados | Violación SRP, difícil de testear, modificar |
| 2 | **Duplicación de `check_and_award_achievements`** — en `dependencies.py:204` y `main.py:1930` | Inconsistencia potencial, mantenimiento duplicado |
| 3 | **Reglas de negocio hardcodeadas** — BR12 (dificultad 1-5) no está validada en la entidad `Exercise`, solo implícita en la BD | Error si se inserta valor inválido |
| 4 | **SQL crudo en handlers HTTP** — consultas SQL en `main.py` mezcladas con lógica HTTP | Fachada de repositorio rota, viola encapsulamiento |
| 5 | **Lesson no es entidad formal** — no existe clase Python en `domain/entities/`, solo fila SQL | Inconsistencia en el modelo de dominio, no hay validación |
| 6 | **Class no es entidad formal** — igual que Lesson, solo existe como tablas SQL | Falta de abstracción, lógica esparcida |
| 7 | **Casos de uso que retornan dict** — no retornan objetos de dominio ni DTOs | Type safety reducido, acoplamiento a formato serializado |
| 8 | **Servicios de dominio con dependencias de infraestructura** — `AIServiceImpl` importa `joblib`, `sklearn`, `google.cloud` | Acoplamiento a librerías externas desde el dominio |
| 9 | **EventRepository no tiene puerto** — es clase concreta de infraestructura usada directamente | Violación de inversión de dependencias |
| 10 | **No hay factories** — las entidades se crean con `new` directo en lugar de factories | Creación dispersa, sin validación centralizada |

---

## 11. Recomendaciones DDD

### Prioridad Alta
1. **Extraer `main.py`** — separar rutas (controllers) de casos de uso y lógica de negocio. Cada caso de uso debe ser una clase en `application/useCases/`.
2. **Formalizar Lesson y Class como entidades** — crear clases Python en `domain/entities/`.
3. **Eliminar duplicación de achievements** — unificar `check_and_award_achievements` en un solo caso de uso.
4. **Agregar validación en entidades** — reglas como BR12 (difficulty 1-5), BR13 (percentage 0-100) deben estar en setters.

### Prioridad Media
5. **Crear puerto para EventRepository** — definir interfaz en `domain/ports/`.
6. **Mover stored procedures a repositorios** — centralizar llamadas a `fn_*` y `sp_*` en los adaptadores PostgreSQL.
7. **Implementar factories** — `UserFactory.create_student()`, `ModuleFactory.create_for_teacher()`.
8. **Implementar DTOs** — los casos de uso deben retornar DTOs tipados, no `dict`.
9. **Separar contextos** — definir Bounded Contexts (Learning, Analytics, Identity, Tutoring) con integración vía eventos.

### Prioridad Baja
10. **Agregar Domain Events** — eventos como `ModuleApproved`, `ExercisePassed`, `AchievementAwarded` para desacoplar contextos.
11. **Implementar Specification pattern** — para las reglas de generación de alertas (BR15-BR17).
12. **Event Sourcing para analítica** — en lugar de snapshots semanales, reconstruir métricas desde eventos.

---

*Fin del reporte de Reconstrucción del Dominio.*
