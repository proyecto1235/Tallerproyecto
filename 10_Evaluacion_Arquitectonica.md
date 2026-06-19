# Evaluación Arquitectónica — RoboLearn

**Rol:** Arquitecto Empresarial  
**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Propósito:** Evaluar el sistema en 6 dimensiones clave con calificación 1–5, justificación técnica y recomendaciones de mejora.

---

## Resumen de Calificaciones

| Dimensión | Calificación | Nivel |
|-----------|:----------:|-------|
| **Cohesión** | ★★★★☆ 4/5 | Alta |
| **Acoplamiento** | ★★★☆☆ 3/5 | Moderado |
| **Escalabilidad** | ★★★☆☆ 3/5 | Moderada |
| **Mantenibilidad** | ★★★★☆ 4/5 | Alta |
| **Testabilidad** | ★★★★☆ 4/5 | Alta |
| **Seguridad** | ★★☆☆☆ 2/5 | Baja |
| **Promedio General** | **3.3/5** | Moderado-Alto |

---

## 1. Cohesión (4/5 — Alta)

### Definición
La cohesión mide el grado en que los elementos de un módulo/capa pertenecen lógicamente juntos. Alta cohesión = responsabilidades afines agrupadas.

### Evaluación

| Aspecto | Evidencia | Puntaje |
|---------|-----------|:-------:|
| **Capa de dominio** | `domain/entities/` contiene 7 entidades de negocio puras sin dependencias externas — máxima cohesión funcional | ★★★★★ |
| **Puertos (interfaces)** | `domain/ports/` con 5 interfaces cohesivas (UserRepository, ModuleRepository, EnrollmentRepository, TeacherRepository, AIService) | ★★★★★ |
| **Servicios ML** | `application/services/ml/` agrupa 12 archivos cohesivos: 6 predictores + orquestador + feature extractor + dataset sintético | ★★★★★ |
| **Analytics** | `analytics/` con 3 archivos (router + metrics + scheduler) — alta cohesión funcional | ★★★★☆ |
| **Adaptadores PostgreSQL** | 4 repositorios en `postgres/` + pool de conexiones — alta cohesión por tecnología | ★★★★☆ |
| **main.py** | 4082 líneas con routing, lógica de negocio, SQL inline y manejo de errores **mezclados** — **baja cohesión** | ★★☆☆☆ |
| **dependencies.py** | 305 líneas con lazy loading, repos, servicios, JWT, DI wiring — cohesión funcional media-alta | ★★★☆☆ |

### Justificación

**Fortalezas:**
- La arquitectura hexagonal impone una separación natural: dominio puro (`domain/`), aplicación (`application/`), infraestructura (`infrastructure/`). Cada una de estas capas tiene alta cohesión interna.
- Los servicios ML están agrupados con propósito único (predicción). Los adaptadores de base de datos están agrupados por tecnología.
- Las entidades de dominio no dependen de nada externo — cohesión máxima.

**Debilidades:**
- **main.py es el punto débil**: 4000+ líneas donde conviven endpoints, autenticación, lógica de negocio, consultas SQL, manejo de sesiones y logging. Esto viola el principio de responsabilidad única y rompe la cohesión de la capa de presentación.
- Algunos servicios en `application/services/` mezclan lógica de dominio con lógica de infraestructura (ej: `ai_service_impl.py` que maneja Dialogflow, ML y PostgreSQL).
- `dependencies.py` hace demasiadas cosas: lazy loading, creación de instancias, funciones de JWT, verificación de tokens — sería más cohesivo separado en varios módulos.

### Recomendaciones

1. **Refactorizar main.py** en routers por dominio:
   - `routers/auth.py`, `routers/users.py`, `routers/modules.py`, `routers/exercises.py`, `routers/classes.py`, `routers/challenges.py`, `routers/analytics.py`, `routers/ai.py`, `routers/admin.py`
2. **Separar dependencies.py** en:
   - `deps/jwt.py` (JWT + token blacklist)
   - `deps/auth.py` (verify_token, verify_teacher, verify_admin)
   - `deps/container.py` (DI wiring de repos y servicios)
3. **Mover lógica de negocio** de main.py a casos de uso o servicios dedicados (ej: perfil de usuario, búsqueda, progreso).

---

## 2. Acoplamiento (3/5 — Moderado)

### Definición
El acoplamiento mide el grado de dependencia entre módulos. Bajo acoplamiento = cambios en un módulo no afectan a otros.

### Evaluación

| Aspecto | Evidencia | Puntaje |
|---------|-----------|:-------:|
| **Dominio sin dependencias** | `domain/` no importa nada de infraestructura, FastAPI ni BD — **mínimo acoplamiento** | ★★★★★ |
| **Puertos → Implementaciones** | Los casos de uso dependen de interfaces, no de implementaciones — inversión de dependencias | ★★★★★ |
| **Servicios en main.py** | main.py importa directamente repos, servicios, config — **acoplamiento alto** | ★★☆☆☆ |
| **SQL inline** | Consultas SQL crudo en main.py y repos — acoplado al esquema PostgreSQL | ★★☆☆☆ |
| **Lazy proxies** | `_LazyAI`, `_LazyMLOrchestrator` — acoplan dependencies.py a implementaciones concretas | ★★★☆☆ |
| **Schemas → Entidades** | `app/schemas/` importa `domain/entities/` — acoplamiento necesario y controlado | ★★★★☆ |
| **Frontend ↔ Backend** | Comunicación vía API REST con contratos JSON — **acoplamiento bajo** (solo contrato) | ★★★★★ |
| **ML Pipeline** | Independiente del backend — se comunica via archivos .pkl — **mínimo acoplamiento** | ★★★★★ |

### Justificación

**Fortalezas:**
- La arquitectura hexagonal garantiza que el dominio no conoce nada externo. Los puertos invierten la dependencia.
- Frontend y backend están débilmente acoplados (solo API REST).
- El pipeline ML es completamente independiente.
- Los DTOs (Pydantic schemas) desacoplan la entrada/salida de las entidades de dominio.

**Debilidades:**
- **main.py tiene acoplamiento alto**: importa directamente 20+ módulos (repos, servicios, config, schemas) y los usa inline en los handlers. Un cambio en cualquier repositorio o servicio puede afectar múltiples endpoints.
- **SQL crudo acoplado al esquema**: cualquier cambio en la estructura de tablas requiere cambios en consultas SQL esparcidas por main.py y los repositorios.
- **Lazy proxies ocultan dependencias**: `_LazyAI` acopla dependencies.py a `ai_service_impl.py` en tiempo de ejecución, pero la dependencia no es visible en los imports.
- **JWT_SECRET compartido** frontend/backend crea acoplamiento de seguridad no deseado.

### Recomendaciones

1. **Reducir acoplamiento en main.py**: cada router debe tener sus propias dependencias, no un único punto de wiring global.
2. **Evaluar SQLAlchemy** como ORM para desacoplar consultas SQL del esquema físico.
3. **Separar JWT_SECRET** entre frontend y backend (claves RS256 asimétricas).
4. **Reemplazar lazy proxies** por inyección explícita de dependencias con un contenedor DI (ej: `dependency-injector` o manual).

---

## 3. Escalabilidad (3/5 — Moderada)

### Definición
La escalabilidad mide la capacidad del sistema para manejar creciente carga de trabajo agregando recursos.

### Evaluación

| Aspecto | Evidencia | Puntaje |
|---------|-----------|:-------:|
| **Backend monolítico** | Un solo proceso FastAPI — escalable horizontalmente con balanceador | ★★★☆☆ |
| **Frontend stateless** | Next.js sin estado de sesión — escalable horizontalmente con CDN/balanceador | ★★★★★ |
| **PostgreSQL** | Pool de 5-50 conexiones, sin réplicas, sin sharding — cuello de botella principal | ★★☆☆☆ |
| **MongoDB** | Sin replica set, sin sharding — escalabilidad limitada | ★★☆☆☆ |
| **Redis** | Caché y rate limiting — escalable con Redis Cluster | ★★★☆☆ |
| **Sandbox Docker** | Por request, sincrónico — contención de recursos con muchos estudiantes | ★★☆☆☆ |
| **Ollama** | Instancia única con 4GB RAM límite — no escalable horizontalmente | ★☆☆☆☆ |
| **Timeouts cortos** | 3s MongoDB, 5s predicciones, 10s sandbox — protegen contra degradación | ★★★★☆ |
| **Migración a microservicios** | Módulos `ml/` y `analytics/` preparados para ser extraídos | ★★★★☆ |

### Justificación

**Fortalezas:**
- Frontend stateless permite escalado horizontal inmediato.
- Backend puede escalar a múltiples instancias detrás de un balanceador (stateless — JWT contiene toda la sesión).
- Los módulos internos (`ml/`, `analytics/`) están diseñados con alta cohesión y bajo acoplamiento, lo que facilita una futura extracción a microservicios.
- Los timeouts cortos y degradaciones graceful evitan que un componente lento bloquee todo el sistema.

**Debilidades:**
- **PostgreSQL es el principal cuello de botella**: 22 tablas, pool de solo 50 conexiones, sin réplicas de lectura. Las consultas analíticas pesadas compiten con consultas transaccionales.
- **Sandbox Docker sincrónico**: cada ejecución de código bloquea una conexión del pool. Con 100+ estudiantes ejecutando código simultáneamente, el sistema se degrada.
- **Ollama no escala**: instancia única, límite de 4GB. Con múltiples requests de tutor IA concurrentes, se convierte en cuello de botella.
- **Sin event bus**: Las tareas asíncronas (`asyncio.create_task`) no persisten — si el backend se cae, los eventos se pierden.
- **Sin cacheo de respuestas frecuentes** (endpoints de módulos, ejercicios populares).

### Recomendaciones

1. **Configurar réplicas de lectura** en PostgreSQL para separar consultas transaccionales de analíticas.
2. **Migrar sandbox a workers background** con cola de tareas (Redis + Celery/ARQ) para no bloquear el pool HTTP.
3. **Implementar API caching** con Redis para endpoints GET frecuentes (módulos, ejercicios, clases).
4. **Agregar Ollama multi-instancia** o balanceo de requests entre Ollama y OpenAI.
5. **Evaluar Redis Streams** para event bus persistente en lugar de `asyncio.create_task`.
6. **Configurar connection pooling más alto** en PostgreSQL (100-200) para producción.

---

## 4. Mantenibilidad (4/5 — Alta)

### Definición
La mantenibilidad mide la facilidad con que el sistema puede ser modificado, entendido y extendido.

### Evaluación

| Aspecto | Evidencia | Puntaje |
|---------|-----------|:-------:|
| **Estructura hexgonal** | `domain/`, `application/`, `infrastructure/`, `app/`, `config/` — claramente separadas | ★★★★★ |
| **main.py monolítico** | 4082 líneas en un solo archivo — difícil de navegar y modificar | ★★☆☆☆ |
| **Casos de uso** | 5 casos de uso formales con responsabilidad única — fáciles de entender | ★★★★★ |
| **Schemas Pydantic** | 9 archivos con validación explícita — facilita entender contratos de API | ★★★★★ |
| **Config centralizada** | `settings.py` con Pydantic Settings — toda la configuración en un lugar | ★★★★★ |
| **CI/CD completo** | linting + tests + build + deploy automatizado | ★★★★★ |
| **Swagger/OpenAPI** | Documentación automática de API en `/docs` | ★★★★★ |
| **Nombrado de archivos** | Convenciones consistentes (repository_impl, service, use_case) | ★★★★☆ |
| **Testing** | 28 tests backend + vitest frontend — pero sin tests de integración | ★★★☆☆ |
| **Logging** | Logger configurado con formato consistente, niveles INFO/DEBUG/ERROR | ★★★★☆ |
| **Sin lock file Python** | requirements.txt sin hashes — dificulta reproducibilidad | ★★☆☆☆ |

### Justificación

**Fortalezas:**
- La arquitectura hexagonal es altamente mantenible: cada capa tiene responsabilidad clara, el dominio es puro, los adaptadores son intercambiables.
- Los casos de uso formales (`RegisterUserUseCase`, `EnrollStudentUseCase`, etc.) son ejemplos de código mantenible: hacen una sola cosa y dependen de interfaces.
- Pydantic schemas proporcionan contratos explícitos con validación automática — cambiar un schema propaga los cambios de forma segura.
- Config centralizada con validación de obligatoriedad al arrancar (evita errores por variables faltantes).
- CI/CD completo atrapa errores antes de llegar a producción.

**Debilidades:**
- **main.py es el mayor problema de mantenibilidad**: 4000+ líneas donde conviven múltiples responsabilidades. Modificar un sistema de autenticación requiere navegar por un archivo masivo.
- **SQL inline** esparcido: la misma consulta puede aparecer en main.py y en el repositorio, dificultando cambios.
- **Sin tests de integración** que validen el flujo completo API → DB → respuesta.
- **Ausencia de lock file** para Python: entornos de desarrollo pueden diferir en versiones de dependencias transivas.
- No hay documentación de arquitectura/diseño más allá de los comentarios en código.

### Recomendaciones

1. **Priorizar refactor de main.py** en routers separados (máximo 200-300 líneas por router).
2. **Agregar lock file** (`pip freeze > requirements-lock.txt` con hash).
3. **Agregar tests de integración** que validen el flujo endpoint → use case → repositorio → DB.
4. **Documentar decisiones arquitectónicas** en ADRs formales dentro del repositorio.
5. **Centralizar consultas SQL** en los repositorios y eliminar las que están en main.py.

---

## 5. Testabilidad (4/5 — Alta)

### Definición
La testabilidad mide la facilidad con que el sistema puede ser probado de forma unitaria, integrada y automatizada.

### Evaluación

| Aspecto | Evidencia | Puntaje |
|---------|-----------|:-------:|
| **Puertos y DI** | Los casos de uso dependen de interfaces — fácil de mockear/stub | ★★★★★ |
| **Entidades de dominio puras** | Sin dependencias externas — testeables sin infraestructura | ★★★★★ |
| **Casos de uso pequeños** | Responsabilidad única — fáciles de testear unitariamente | ★★★★★ |
| **CI con servicios** | GitHub Actions levanta PostgreSQL, MongoDB y Redis para tests | ★★★★★ |
| **Bad Smell: SQL inline en main.py** | Lógica de negocio en endpoints — requiere levantar toda la app para probar | ★★☆☆☆ |
| **Bad Smell: Fire-and-forget** | `asyncio.create_task` sin manejo — imposible de testear | ★☆☆☆☆ |
| **Lazy imports** | ML packages cargados diferidos — dependencias ocultas en tests | ★★★☆☆ |
| **Sin tests de carga reales** | k6 test solo cubre endpoints básicos, no IA ni sandbox | ★★★☆☆ |
| **Cobertura** | pytest-cov configurado, pero sin métricas visibles actuales | ★★★☆☆ |

### Justificación

**Fortalezas:**
- La arquitectura hexagonal destaca en testabilidad: los puertos permiten mockear repositorios y servicios externos sin infraestructura real.
- Las entidades de dominio son Python puro — testeables en aislamiento.
- Los casos de uso tienen constructor que recibe interfaces — un test puede inyectar mocks fácilmente.
- CI/CD ejecuta tests con PostgreSQL, MongoDB y Redis reales como service containers.
- Pydantic schemas validan datos de entrada/salida — reducen necesidad de tests de validación manual.

**Debilidades:**
- **main.py con lógica inline** requiere levantar FastAPI completo para probar la mayoría de los endpoints. No se puede testear la lógica de negocio sin el framework HTTP.
- **Fire-and-forget con `asyncio.create_task`** : las tareas de logging a MongoDB se disparan y olvidan — no hay forma de verificar en tests que el evento se registró correctamente.
- **Lazy proxies** ocultan dependencias: un test no sabe qué implementación concreta se usará hasta tiempo de ejecución.
- **Sin tests de estrés para IA**: el k6 test solo cubre endpoints básicos. El sandbox, tutor y chatbot no están cubiertos por pruebas de carga.
- **Algunas funciones de 200+ líneas** en main.py — difíciles de entender y probar.

### Recomendaciones

1. **Mover lógica a casos de uso**: la lógica de main.py (registro, login, progreso, logros) debe migrarse a casos de uso formales, testeables unitariamente.
2. **Agregar wrapper para fire-and-forget**: crear un `BackgroundTaskTracker` que permita esperar tareas en tests.
3. **Agregar tests de estrés para IA y sandbox** en k6.
4. **Hacer explícitos los lazy proxies**: que los tests puedan inyectar implementaciones mock sin depender del proxy.
5. **Configurar Codecov correctamente** para tracking de cobertura en cada PR.

---

## 6. Seguridad (2/5 — Baja)

### Definición
La seguridad mide la capacidad del sistema para resistir ataques, proteger datos y mantener la confidencialidad, integridad y disponibilidad.

### Evaluación

| Aspecto | Evidencia | Puntaje |
|---------|-----------|:-------:|
| **JWT con bcrypt** | Contraseñas hasheadas con bcrypt, JWT firmado, cookie HTTP-only | ★★★★☆ |
| **CVE-2024-33663** | python-jose 3.3.0 — algorithm confusion (CVSS 9.3, CRÍTICA) | ★☆☆☆☆ |
| **exec() con blacklist** | Sandbox_service.py usa exec() con blacklist bypasseable — RCE potencial | ★☆☆☆☆ |
| **JWT_SECRET compartido** | Frontend y backend usan la misma clave HMAC | ★★☆☆☆ |
| **SQL Injection** | `database_init.py:111` con f-string en table_name | ★★☆☆☆ |
| **Sin TLS/HTTPS** | Tráfico en texto plano entre todos los servicios | ★★☆☆☆ |
| **Password truncado 72 chars** | `request.password[:72]` — límite innecesario | ★★★☆☆ |
| **Token blacklist frágil** | Depende de Redis — si Redis caído, tokens revocados son válidos | ★★☆☆☆ |
| **Rate limiting desactivado** | Si Redis caído, no hay rate limiting | ★★☆☆☆ |
| **Contraseñas por defecto** | `robolearn_dev` hardcodeado en docker-compose.yml | ★☆☆☆☆ |
| **Audit logging** | Middleware audita rutas sensibles (auth, admin, profile, execute-code) | ★★★★☆ |
| **Security headers** | CSP, HSTS, X-Frame-Options, X-Content-Type-Options configurados | ★★★★★ |
| **Fire-and-forget sin control** | Excepciones de logging silenciosas — posible pérdida de auditoría | ★★★☆☆ |
| **CORS permisivo** | Multi-origen permitido — puede incluir orígenes de más en producción | ★★★☆☆ |
| **Red interna sin cifrado** | Tráfico plano entre backend ↔ BD en internal_net | ★★☆☆☆ |

### Justificación

**Fortalezas:**
- bcrypt para hashing (estándar de industria).
- JWT con soporte HS256 y RS256.
- Cookie HTTP-only + SameSite Lax previene XSS de robo de token.
- Security headers completos (CSP, HSTS, X-Frame-Options, etc.).
- Audit logging en rutas sensibles.
- Redes Docker internas aíslan bases de datos.
- Sandbox Docker tiene restricciones reales (sin red, solo lectura, recursos limitados).

**Debilidades CRÍTICAS:**
1. **CVE-2024-33663 (python-jose 3.3.0, CVSS 9.3)**: permite falsificar cualquier JWT usando la clave pública — autenticación completamente evitable.
2. **exec() en sandbox**: la blacklist de patrones peligrosos es trivialmente bypasseable (`"o"+"s"+"."+"system"`). Aunque Docker limita el daño, es una vulnerabilidad evitable.
3. **JWT_SECRET compartido**: si el frontend es comprometido (XSS), el atacante obtiene la clave para firmar JWTs.

**Debilidades ALTAS:**
4. **Sin TLS/HTTPS**: todo el tráfico (login, tokens, datos) viaja en texto plano.
5. **Contraseñas por defecto** en docker-compose.yml.
6. **Token blacklist y rate limiting dependen de Redis**: si Redis falla, ambos se desactivan.
7. **Password truncado** reduce el espacio de búsqueda.

### Recomendaciones

#### Urgentes (Críticas)
1. **Actualizar python-jose** de 3.3.0 a ≥3.4.0 (o migrar a PyJWT).
2. **Reemplazar exec() por CodeExecutor Docker** — eliminar `sandbox_service.py` y usar siempre `code_executor.py`.
3. **Separar JWT_SECRET** entre frontend y backend — migrar a RS256.

#### Altas
4. **Agregar TLS/HTTPS** con Caddy o nginx como proxy reverso + Let's Encrypt.
5. **Eliminar contraseñas por defecto** del docker-compose.yml — validar que .env existe.
6. **Agregar local fallback** para token blacklist y rate limiting (diccionario en memoria) cuando Redis no está disponible.
7. **No truncar passwords** — eliminar `[:72]`.
8. **Cifrar tráfico interno** con TLS entre servicios (al menos PostgreSQL).

#### Medias
9. **Reforzar validación de CORS_ORIGINS** en producción (solo el dominio específico).
10. **Agregar rate limiting por IP** en el middleware antes de llegar a los handlers.
11. **Validar algoritmo JWT contra allowlist** estricta en `_decode_token_fallback`.
12. **Revisar SQL injection en database_init.py** — usar `sql.Identifier()`.

---

## Tabla Resumen

| Dimensión | Calificación | Fortaleza Principal | Debilidad Principal | Prioridad de Mejora |
|-----------|:----------:|---------------------|---------------------|:-------------------:|
| **Cohesión** | ★★★★☆ 4/5 | Capas hexagonales con dominio puro | main.py de 4000+ líneas mezcla todo | Alta |
| **Acoplamiento** | ★★★☆☆ 3/5 | Puertos + inversión de dependencias | main.py importa 20+ módulos directamente | Media |
| **Escalabilidad** | ★★★☆☆ 3/5 | Frontend stateless, módulos extraíbles | PostgreSQL sin réplicas, sandbox sincrónico | Alta |
| **Mantenibilidad** | ★★★★☆ 4/5 | Estructura hexagonal, schemas, CI/CD | main.py monolítico, SQL inline | Alta |
| **Testabilidad** | ★★★★☆ 4/5 | Puertos mockeables, dominio puro | Lógica inline en endpoints, fire-and-forget | Media |
| **Seguridad** | ★★☆☆☆ 2/5 | bcrypt, JWT, security headers | CVE-2024-33663, exec() inseguro, JWT compartido, sin TLS | **Crítica** |

---

## Prioridad General de Mejoras

| Prioridad | Acciones |
|-----------|---------|
| 🔴 **Crítica** | 1. Actualizar python-jose. 2. Reemplazar exec() sandbox por Docker. 3. Separar JWT_SECRET. |
| 🟡 **Alta** | 4. Refactor main.py en routers. 5. Agregar TLS/HTTPS. 6. Configurar réplicas PostgreSQL y caché. |
| 🟢 **Media** | 7. Agregar lock file Python. 8. Tests de integración y estrés. 9. Event bus persistente. |
| 🔵 **Baja** | 10. Documentación ADRs formal. 11. Feature flags. 12. Evaluar GraphQL. |

---

*Fin del reporte de Evaluación Arquitectónica.*
