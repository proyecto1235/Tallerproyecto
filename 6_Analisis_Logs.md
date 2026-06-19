# Análisis de Logs — RoboLearn

**Rol:** Ingeniero de Soporte Nivel 3  
**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Propósito:** Analizar logs de ejecución, errores, advertencias, excepciones, dependencias faltantes, problemas de configuración, red y autenticación.

---

## Metodología

- **No se encontraron archivos de log persistentes** — toda la salida va a stdout/stderr y no se conserva en disco.
- Los hallazgos se extrajeron mediante **análisis estático del código fuente**: todas las sentencias `logger.error()`, `logger.warning()`, `logger.info()`, `print()` y manejos de excepción fueron catalogados y clasificados.
- Se analizaron ~25 archivos fuente con ~3600 líneas de código backend, más scripts ML y tests.
- Cada hallazgo se clasificó por **severidad** y **probabilidad de ocurrencia** en ejecución real.

---

## 1. Errores (logger.error / print("[ERROR]"))

| # | Archivo | Línea | Mensaje | Severidad | Probabilidad |
|---|---------|-------|---------|-----------|-------------|
| E1 | `exceptions.py` | 64 | `Unhandled exception: {type}: {exc}` (cualquier excepción no capturada) | **Crítico** | Media — depende del tráfico |
| E2 | `main.py` | 634 | `Warm error: {e}` (fallo en background warm de predicciones) | **Alto** | Alta — depende de DB/ML |
| E3 | `main.py` | 741 | `Tutor log error: {e}` (fallo al guardar interacción en MongoDB) | **Alto** | Alta — MongoDB frecuentemente no disponible |
| E4 | `main.py` | 876 | `Tutor feedback log error: {e}` (fallo al guardar feedback en MongoDB) | **Alto** | Alta — MongoDB frecuentemente no disponible |
| E5 | `dependencies.py` | 152 | `Redis error in is_token_blacklisted: {e}` | **Alto** | Media |
| E6 | `code_executor.py` | 65 | `Error cleaning up timed-out container: {e}` | **Medio** | Baja — timeout de Docker |
| E7 | `code_executor.py` | 78 | `Error removing container {container_id}: {e}` | **Bajo** | Baja — limpieza fallida |
| E8 | `database_init.py` | 135 | `[ERROR] Failed to create database` | **Crítico** | Alta — si PostgreSQL no responde |
| E9 | `database_init.py` | 157 | `[ERROR] Failed to create schema: {e}` | **Crítico** | Alta — si el script SQL falla |
| E10 | `database_init.py` | 37 | `Error checking if database exists: {e}` | **Alto** | Alta — en primera ejecución |
| E11 | `database_init.py` | 59 | `Error creating database: {e}` | **Crítico** | Alta — en primera ejecución |
| E12 | `database_init.py` | 99 | `Error executing SQL file {file_path}: {e}` | **Alto** | Media — scripts SQL con errores |

---

## 2. Advertencias (logger.warning / print("[WARN]"))

| # | Archivo | Línea | Mensaje | Severidad | Probabilidad |
|---|---------|-------|---------|-----------|-------------|
| W1 | `main.py` | 61 | `Google credentials file not found at: {path}` | **Medio** | Alta — archivo no existe por defecto |
| W2 | `main.py` | 559 | `get_class_predictions timed out – triggering background warm` | **Medio** | Alta — timeout de 5s |
| W3 | `main.py` | 563 | `get_class_predictions failed: {e}` | **Medio** | Alta |
| W4 | `main.py` | 593 | `MongoDB aggregates timed out` | **Medio** | Alta — timeout de 3s |
| W5 | `main.py` | 595 | `MongoDB analytics fetch: {e}` | **Medio** | Alta |
| W6 | `main.py` | 714 | `Dialogflow fallback trigger: {e}` | **Bajo** | Alta — Dialogflow no configurado |
| W7 | `cache.py` | 19–23 | `[AICache] Redis no disponible. El caché de respuestas de IA... está desactivado` | **Alto** | Alta — Redis no disponible en desarrollo |
| W8 | `cache.py` | 35 | `[AICache] Redis no disponible: {e}` | **Alto** | Alta — Redis no disponible en desarrollo |
| W9 | `rate_limiter.py` | 19–22 | `[RateLimiter] Redis no disponible. El rate limiting está desactivado` | **Alto** | Alta — Redis no disponible en desarrollo |
| W10 | `rate_limiter.py` | 35 | `[RateLimiter] Redis no disponible: {e}` | **Alto** | Alta — Redis no disponible en desarrollo |
| W11 | `rate_limiter.py` | 57 | `[RateLimiter] Error en check: {e}` | **Medio** | Baja |
| W12 | `behavioral_repo.py` | 42–46 | `[BehavioralRepository] MongoDB no disponible. Datos de comportamiento... no se persisten` | **Alto** | Alta — MongoDB no disponible en desarrollo |
| W13 | `behavioral_repo.py` | 53–56 | `[BehavioralRepository] MongoDB no disponible. Datos de comportamiento no se persisten.` | **Alto** | Alta |
| W14 | `ai_service_impl.py` | 49 | `[AIServiceImpl] Error en get_recommendations: {e}` | **Medio** | Alta — modelo ML no entrenado |
| W15 | `ai_service_impl.py` | 87 | `[AIServiceImpl] ML predict_student falló: {e}` | **Medio** | Alta — modelo ML no entrenado |
| W16 | `ai_service_impl.py` | 101 | `[AIServiceImpl] Fallback query predict_student falló: {e}` | **Bajo** | Media — PostgreSQL caído |
| W17 | `ai_service_impl.py` | 102 | `[AIServiceImpl] No se pudo predecir rendimiento para student={id}` | **Bajo** | Media |
| W18 | `ai_service_impl.py` | 146 | `[AIServiceImpl] detect_learning_path falló: {e}` | **Bajo** | Media |
| W19 | `ai_service_impl.py` | 172 | `[AIServiceImpl] Error entrenando modelo: {e}` | **Bajo** | Baja |
| W20 | `intelligent_tutor.py` | 60 | `[IntelligentTutor] Error llamando a LLM: {e}` | **Bajo** | Alta — Ollama no disponible |
| W21 | `dependencies.py` | 304 | `Achievement check error: {e}` | **Bajo** | Media |
| W22 | `main.py` | 2058 | `Achievement check error: {e}` | **Bajo** | Media |
| W23 | `database_init.py` | 160 | `[WARN] 001-init.sql not found` | **Crítico** | Media — si el script falta |
| W24 | `database_init.py` | 177 | `[WARN] 002-seed-data.sql not found` | **Crítico** | Media — sin datos semilla |
| W25 | `database_init.py` | 191 | `[WARN] 003-seed-massive.sql not found, skipping` | **Bajo** | Media |
| W26 | `database_init.py` | 93 | `[WARN] {e}` (errores SQL ignorados) | **Medio** | Alta — conflictos SQL silenciados |
| W27 | `database_init.py` | 108 | `[WARN] 004-seed-teacher-data.sql not found, skipping` | **Bajo** | Media |
| W28 | `database_init.py` | 213 | `[WARN] 005-enable-pgvector.sql not found` | **Medio** | Media — pgvector no habilitado |

---

## 3. Excepciones Capturadas (`except Exception`, `except ImportError`)

| # | Archivo | Línea | Excepción Capturada | Acción | Severidad | Riesgo |
|---|---------|-------|---------------------|--------|-----------|--------|
| X1 | `main.py` | 558–564 | `asyncio.TimeoutError, Exception` | Retorna dashboard sin datos | **Medio** | Dashboard parcial |
| X2 | `main.py` | 592–595 | `asyncio.TimeoutError, Exception` | Retorna actividad vacía | **Medio** | Dashboard parcial |
| X3 | `main.py` | 713–714 | `Exception` | Fallback a IntelligentTutor | **Bajo** | Degradación graceful |
| X4 | `main.py` | 740–741 | `Exception` | Fallo al guardar log (silencioso) | **Bajo** | Datos perdidos |
| X5 | `main.py` | 875–877 | `Exception` | Fallo al guardar feedback | **Bajo** | Datos perdidos |
| X6 | `main.py` | 897–899 | `Exception` | Ollama se reporta no disponible | **Bajo** | Fallback correcto |
| X7 | `main.py` | 933–934 | `Exception` | Dialogflow fallback silencioso | **Bajo** | Fallback correcto |
| X8 | `main.py` | 942–944 | `Exception` | Ollama check silencioso | **Bajo** | Fallback correcto |
| X9 | `main.py` | 959–960 | `Exception` | Ollama fallo silencioso | **Bajo** | Fallback correcto |
| X10 | `main.py` | 1028–1029 | `Exception` | Ollama fallo en chat autenticado | **Bajo** | Fallback a OpenAI |
| X11 | `main.py` | 1061–1064 | `ImportError, Exception` | OpenAI no disponible | **Bajo** | Fallback a tutor |
| X12 | `main.py` | 1091–1092 | `Exception` | Fallo al guardar interacción | **Bajo** | Datos perdidos |
| X13 | `main.py` | 1190–1191 | `Exception` | Fallo al loguear ejecución de código | **Bajo** | Datos perdidos |
| X14 | `main.py` | 1321–1337 | `Exception` | Fallo al loguear submission | **Bajo** | Datos perdidos |
| X15 | `main.py` | 1639–1640 | `Exception` | Fallo al loguear completion | **Bajo** | Datos perdidos |
| X16 | `main.py` | 1801–1802 | `Exception` | Fallo al loguear lesson complete | **Bajo** | Datos perdidos |
| X17 | `code_executor.py` | 57–66 | `requests.exceptions.ReadTimeout` | Timeout Docker | **Medio** | Ejercicio fallido |
| X18 | `code_executor.py` | 67–68 | `docker.errors.DockerException` | Error Docker | **Medio** | Sandbox caído |
| X19 | `code_executor.py` | 69–70 | `Exception` | Error inesperado | **Medio** | Error genérico |
| X20 | `ai_service_impl.py` | 69–72 | `ImportError, Exception` | Dialogflow no disponible | **Bajo** | Fallback graceful |
| X21 | `database_init.py` | 36–38, 58–60, 98–100 | `Exception` | Fallos de conexión PostgreSQL | **Crítico** | App no inicia |
| X22 | `database_init.py` | 70–71 | `Exception` | table_exists falla | **Medio** | Inicialización frágil |
| X23 | `database_init.py` | 114–116 | `Exception` | data_exists falla | **Medio** | Seed duplicado |

---

## 4. Dependencias Faltantes o Potencialmente Faltantes

| # | Dependencia | Archivo | Línea | Problema | Severidad | Evidencia |
|---|-------------|---------|-------|----------|-----------|-----------|
| D1 | **python-jose 3.3.0** | `requirements.txt` | — | `CVE-2024-33663` — algorithm confusion (CVSS 9.3) | **Crítico** | `dependencies.py:105` — usa JWT decode |
| D2 | **Next.js 16.2.4** | `package.json` | — | `CVE-2026-44581` — XSS almacenado por CSP nonce | **Alto** | `next.config.mjs` |
| D3 | **Modelos ML** | `models/` | — | No existen `*.pkl` en el repo | **Alto** | `ai_service_impl.py:22-26` — modelo no encontrado |
| D4 | **Parquet dataset** | `ml_pipeline/data/` | — | No existe `robolearn_dataset.parquet` en el repo | **Alto** | `train_models.py:37` — dataset no encontrado |
| D5 | **Docker daemon** | `code_executor.py` | 16–18 | Sandbox requiere Docker en ejecución | **Alto** | `main.py:1104-1198` — `/api/execute-code` falla |
| D6 | **Ollama** | `LLMService` | 7 | Modelo `qwen2.5-coder:1.5b` no descargado | **Alto** | `llm_service.py:50-55` — is_available() falla |
| D7 | **pgvector** | `scripts/` | — | `005-enable-pgvector.sql` puede faltar | **Medio** | `database_init.py:205-213` |
| D8 | **Google Cloud credentials** | `./` | — | `robolearn-key.json` no existe por defecto | **Medio** | `main.py:55-61` |
| D9 | [google-cloud-dialogflow] | `requirements.txt` | — | Dependencia opcional pero no listada explícitamente | **Medio** | `ai_service_impl.py:60` — `from google.cloud import dialogflow` |
| D10 | **Numpy (diferido)** | `analytics_router` | — | Import lazy en lifespan — si falla, rutas analytics caen | **Medio** | `main.py:68` |
| D11 | **docker SDK** | `requirements.txt` | `docker` | Requerido para sandbox | **Alto** | `code_executor.py:1` |
| D12 | **httpx** | `requirements.txt` | `httpx` | Requerido para LLMService | **Alto** | `llm_service.py:4` |
| D13 | **redis.asyncio** | `requirements.txt` | `redis` | Requerido para caché y rate limiter | **Alto** | `cache.py:5`, `rate_limiter.py:4` |
| D14 | **pymongo** | `requirements.txt` | `pymongo` | Requerido para behavioral repository | **Alto** | `behavioral_repository.py:4` |

---

## 5. Problemas de Configuración

| # | Problema | Archivo | Línea | Descripción | Severidad |
|---|----------|---------|-------|-------------|-----------|
| C1 | **JWT_SECRET compartido** | `docker-compose.yml` | 167 | Backend y frontend usan el mismo `SECRET_KEY` para JWT | **Crítico** |
| C2 | **Contraseñas por defecto** | `docker-compose.yml` | — | `robolearn_dev` hardcodeado para PG, Mongo | **Crítico** |
| C3 | **SQL Injection** | `database_init.py` | 111 | `f"SELECT COUNT(*) FROM {table_name}"` — interpolación directa | **Alto** |
| C4 | **exec() sin sandbox real** | `main.py` | 1177 | `exec(request.code, env)` con blacklist de strings (bypasseable) | **Crítico** |
| C5 | **Sin TLS/HTTPS** | `docker-compose.yml` | — | No hay proxy reverso, todo HTTP plano | **Alto** |
| C6 | **Sin lock file Python** | `requirements.txt` | — | Sin hashes ni versiones fijas | **Alto** |
| C7 | **bcrypt 72-char limit** | `dependencies.py` | 34–35 | `request.password[:72]` — trunca passwords >72 chars | **Medio** |
| C8 | **Debug log no visible** | `logging_config.py` | 8 | Nivel INFO, pero código tiene `logger.debug(...)` | **Bajo** |
| C9 | **test_debug.txt artefacto** | `backend/app/test_debug.txt` | 1 | Archivo `start` residual en producción | **Bajo** |
| C10 | **Fire-and-forget sin manejo** | `main.py` | 232 | `asyncio.create_task` — excepciones silenciosas | **Medio** |
| C11 | **Red interna sin cifrado** | `docker-compose.yml` | — | `internal_net` con bridge, tráfico plano entre servicios | **Medio** |
| C12 | **ON CONFLICT sin unique constraint** | `main.py` | 1265 | `ON CONFLICT (student_id, exercise_id, attempt_count)` — puede que no exista el índice único | **Alto** |
| C13 | **k6 endpoint incorrecto** | `tests/load/k6-load-test.js` | 100 | `GET /api/auth/profile` — el endpoint real es `GET /api/users/profile` | **Alto** |
| C14 | **NODE_ENV duplicado** | `settings.py` | 24 | `node_env = settings("NODE_ENV", default="development")` sin uso real | **Bajo** |
| C15 | **MongoDB no tiene autenticación forzada** | `docker-compose.yml` | 33–39 | Usuario configurado pero no validado en conexión | **Medio** |

---

## 6. Problemas de Red

| # | Problema | Origen | Destino | Puerto | Descripción | Severidad |
|---|----------|--------|---------|--------|-------------|-----------|
| N1 | **PostgreSQL inaccesible** | Backend | `postgres` | 5432 | App no inicia sin DB | **Crítico** |
| N2 | **MongoDB inaccesible** | Backend | `mongo` | 27017 | Behavioral data no persiste, dashboard sin datos | **Alto** |
| N3 | **Redis inaccesible** | Backend | `redis` | 6379 | Sin rate limiting, sin caché de IA | **Alto** |
| N4 | **Ollama inaccesible** | Backend | `ollama` | 11434 | Tutor IA no disponible, fallback a reglas | **Alto** |
| N5 | **Dialogflow inaccesible** | Backend | `dialogflow.googleapis.com` | 443 | Chatbot usa fallback Ollama → tutor | **Bajo** |
| N6 | **Docker no disponible** | Backend | Docker socket | — | Sandbox de código falla | **Alto** |
| N7 | **Timeout en aggregates MongoDB** | Dashboard | `mongo:27017` | 27017 | Timeout de 3s muy ajustado para agregaciones | **Medio** |
| N8 | **Timeout en class predictions** | Dashboard | PostgreSQL | 5432 | Timeout de 5s ajustado | **Medio** |
| N9 | **CORS misconfigurado** | Frontend | Backend | 8000 | `CORS_ORIGINS` permite localhost:3000 pero puede no incluir dominio producción | **Medio** |
| N10 | **No healthcheck en frontend Docker** | `docker-compose.yml` | — | — | Frontend no verifica que backend esté listo | **Medio** |

---

## 7. Problemas de Autenticación

| # | Problema | Archivo | Línea | Descripción | Severidad |
|---|----------|---------|-------|-------------|-----------|
| A1 | **JWT algorithm confusion** | `dependencies.py` | 89–108 | `_decode_token_fallback` prueba RS256 luego HS256 — ataque de confusión de algoritmos | **Crítico** |
| A2 | **Token no vinculado a sesión** | `dependencies.py` | 111–121 | JWT sin refresh token, sin revocación real (blacklist en Redis — si Redis caído, no se puede revocar) | **Alto** |
| A3 | **verify_token_optional expone endpoint** | `dependencies.py` | 187–201 | Algunos endpoints aceptan token opcional — filtra datos parciales | **Medio** |
| A4 | **JWT expiración larga** | `.env.example` | 17 | `ACCESS_TOKEN_EXPIRE_MINUTES=10080` = 7 días | **Medio** |
| A5 | **Rate limiting desactivado por defecto** | `rate_limiter.py` | 19–22 | Redis no disponible → sin límite de requests | **Alto** |
| A6 | **auth-token cookie sin Secure** | `main.py` | 183 | `secure=settings.app_env == "production"` — en desarrollo, cookie viaja en HTTP plano | **Medio** |
| A7 | **Token blacklist depende de Redis** | `dependencies.py` | 143–153 | Si Redis falla, `is_token_blacklisted` retorna False → tokens revocados aún válidos | **Alto** |
| A8 | **Password hash expuesto en log** | `main.py` | 206 | `logger.debug(f"bcrypt error: {type(e).__name__}: {e}")` — el error de bcrypt puede contener el hash | **Bajo** |
| A9 | **Sin rate limiting por IP** | `main.py` | — | Rate limiting no está implementado en los endpoints reales, solo existe la clase | **Medio** |
| A10 | **Contraseñas en URLs de conexión** | `.env.example` | — | `MONGODB_URL=mongodb://...`, `REDIS_URL=redis://...` — URLs visibles en logs si se imprimen | **Medio** |

---

## Matriz de Hallazgos

| ID | Categoría | Descripción Corta | Severidad | Componente | Mitigación Sugerida |
|----|-----------|-------------------|-----------|------------|---------------------|
| E1 | Error | Unhandled exception global | **Crítico** | Backend (exceptions.py) | Monitoreo + alertas en el handler global |
| E8 | Error | Failed to create database | **Crítico** | DB Init | Healthcheck pre-arranque, reintentos |
| E9 | Error | Failed to create schema | **Crítico** | DB Init | Validar scripts SQL antes de deploy |
| E11 | Error | Error creating database | **Crítico** | DB Init | Logs detallados, reintentos exponenciales |
| D1 | Dep. Falta | python-jose 3.3.0 (CVE-2024-33663) | **Crítico** | Seguridad JWT | Actualizar a >=3.4.0 |
| C1 | Config | JWT_SECRET compartido frontend/backend | **Crítico** | docker-compose | Usar RS256, claves separadas |
| C2 | Config | Contraseñas por defecto en compose | **Crítico** | docker-compose | Exigir .env con valores fuertes |
| C4 | Config | exec() con blacklist bypasseable | **Crítico** | Sandbox Code | Usar contenedores Docker reales + timeouts |
| A1 | Auth | JWT algorithm confusion | **Crítico** | dependencies.py | Validar algoritmo contra allowlist |
| D2 | Dep. Falta | Next.js 16.2.4 (CVE-2026-44581) | **Alto** | Frontend | Actualizar a >=16.2.5 |
| D3 | Dep. Falta | Modelos ML no existen | **Alto** | ML Pipeline | Agregar al repo o generarlos en build |
| D4 | Dep. Falta | Parquet dataset no existe | **Alto** | ML Pipeline | Agregar o generar en setup |
| D5 | Dep. Falta | Docker daemon requerido | **Alto** | Sandbox | Validar disponibilidad al iniciar |
| D6 | Dep. Falta | Ollama modelo no descargado | **Alto** | LLM Service | Pull automático validado |
| D11 | Dep. Falta | docker SDK puede faltar | **Alto** | requirements.txt | Incluir en dev/prod |
| D12 | Dep. Falta | httpx puede faltar | **Alto** | requirements.txt | Incluir en dev/prod |
| D13 | Dep. Falta | redis.asyncio puede faltar | **Alto** | requirements.txt | Incluir en dev/prod |
| D14 | Dep. Falta | pymongo puede faltar | **Alto** | requirements.txt | Incluir en dev/prod |
| C3 | Config | SQL Injection en database_init.py | **Alto** | DB Init | Usar `sql.Identifier()` en lugar de f-strings |
| C5 | Config | Sin TLS/HTTPS | **Alto** | Infraestructura | Agregar nginx/caddy con Let's Encrypt |
| C6 | Config | Sin lock file Python | **Alto** | Dependencias | Generar requirements.txt con hashes |
| C12 | Config | ON CONFLICT sin unique constraint | **Alto** | main.py | Verificar índice único existe |
| C13 | Config | k6 endpoint incorrecto | **Alto** | Tests | Corregir `/api/users/profile` |
| N1 | Red | PostgreSQL inaccesible | **Crítico** | Backend | Healthcheck, waiting script |
| N2 | Red | MongoDB inaccesible | **Alto** | Backend | Degradación graceful + alerta |
| N3 | Red | Redis inaccesible | **Alto** | Backend | Degradación graceful + alerta |
| N4 | Red | Ollama inaccesible | **Alto** | Backend | Fallback a IntelligentTutor |
| A5 | Auth | Rate limiting desactivado | **Alto** | rate_limiter.py | Cache local fallback si Redis caído |
| A7 | Auth | Token blacklist depende de Redis | **Alto** | dependencies.py | Cache local + Redis como primario |
| W1 | Warning | Google credentials no encontradas | **Medio** | main.py | Log más visible, no silenciar |
| W2 | Warning | get_class_predictions timeout | **Medio** | main.py | Aumentar timeout o async |
| W4 | Warning | MongoDB aggregates timeout | **Medio** | main.py | Timeout 3s muy agresivo |
| W7 | Warning | Redis caché desactivado | **Alto** | cache.py | Fallback a dict en memoria |
| W9 | Warning | Rate limiting desactivado | **Alto** | rate_limiter.py | Fallback a dict en memoria |
| W12 | Warning | MongoDB no disponible | **Alto** | behavioral_repo.py | Fallback a SQLite o archivo |
| W14 | Warning | Modelo ML no entrenado | **Medio** | ai_service_impl.py | Modelo por defecto siempre disponible |
| C7 | Config | bcrypt 72-char limit | **Medio** | dependencies.py | Usar hash previo si >72 |
| C10 | Config | Fire-and-forget sin manejo | **Medio** | main.py | Capturar excepciones en create_task |
| N7 | Red | Timeout agregaciones MongoDB | **Medio** | Dashboard | Aumentar a 10s |
| N8 | Red | Timeout class predictions | **Medio** | Dashboard | Aumentar a 15s |
| A6 | Auth | Cookie sin Secure en dev | **Medio** | main.py | Forzar Secure en todos los entornos |
| W20 | Warning | Error llamando a LLM | **Bajo** | intelligent_tutor.py | Esperado si Ollama no disponible |
| W23 | Warning | 001-init.sql not found | **Crítico** | DB Init | Validar archivos en build |
| W24 | Warning | 002-seed-data.sql not found | **Crítico** | DB Init | Validar archivos en build |
| C8 | Config | Debug logs no visibles | **Bajo** | logging_config.py | Cambiar a DEBUG en desarrollo |
| C9 | Config | test_debug.txt residual | **Bajo** | Backend | Eliminar archivo |
| C14 | Config | NODE_ENV sin uso | **Bajo** | settings.py | Eliminar variable |

---

## Resumen por Severidad

| Severidad | Conteo | Hallazgos Clave |
|-----------|--------|-----------------|
| **Crítico** | 11 | E1, E8, E9, E11, D1, C1, C2, C4, A1, W23, W24 |
| **Alto** | 25 | E2–E5, D2–D6, D11–D14, C3, C5, C6, C12, C13, N2–N4, A5, A7, W7, W9, W12 |
| **Medio** | 20 | W1–W5, W14, C7, C10, N7, N8, A6, E6, X1, X2, X17–X19, C11 |
| **Bajo** | 16 | W6, W15–W22, W25–W27, C8, C9, C14, X3–X16 |

---

## Top 5 Hallazgos Más Críticos

### 1. 🚨 CVE-2024-33663 — python-jose 3.3.0 (Algorithm Confusion)
- **Componente:** `backend/requirements.txt`, `dependencies.py:89-108`
- **Impacto:** Atacante puede falsificar tokens JWT usando clave pública como HMAC
- **CVSS:** 9.3 (Crítico)
- **Acción:** Actualizar a python-jose >= 3.4.0

### 2. 🚨 Sandbox de Código Inseguro (`exec()`)
- **Componente:** `main.py:1115-1129`, `sandbox_service.py:9-14`
- **Impacto:** Blacklist de strings es trivial de bypassear (e.g., `eval("o"+"pen")`)
- **Riesgo:** Ejecución remota de código (RCE)
- **Acción:** Usar sandboxing real con contenedores Docker (ya existe `CodeExecutor` en `code_executor.py` pero no se usa — `main.py` usa `exec()` directo en su lugar)

### 3. 🚨 SQL Injection en `database_init.py`
- **Componente:** `database_init.py:111`
- **Impacto:** Inyección SQL si `table_name` contiene datos maliciosos (bajo riesgo porque solo se usa con constantes, pero mala práctica)
- **Acción:** Usar `sql.Identifier(table_name)` en lugar de f-string

### 4. 🚨 Secretos Compartidos y por Defecto
- **Componente:** `docker-compose.yml`
- **Impacto:** JWT_SECRET compartido backend ↔ frontend; contraseñas `robolearn_dev` hardcodeadas
- **Riesgo:** Falsificación de tokens, acceso a bases de datos
- **Acción:** Rotar secretos, usar RS256, exigir `.env` en producción

### 5. 🚨 Dependencias Múltiples Faltantes en Tiempo de Ejecución
- **Componente:** Múltiples servicios
- **Impacto:** MongoDB, Redis, Ollama, Docker daemon, modelos ML no existen por defecto — la app arranca en modo degradado sin que el usuario lo sepa claramente
- **Acción:** Implementar healthchecks visibles en `/health`, dashboard de estado de servicios

---

## Conclusión

**El sistema tiene 11 hallazgos críticos y 25 de alta severidad.** La aplicación arrancaría en un estado mayormente degradado sin MongoDB, Redis, Ollama ni modelos ML entrenados. Las advertencias (W7, W9, W12) se dispararían inmediatamente al primer request que intente usar caché, rate limiting o behavioral tracking.

El problema de seguridad más urgente es el **sandbox de código con `exec()` directo** (main.py:1177) que permite RCE, seguido de la **vulnerabilidad de python-jose** y la **configuración insegura de JWT compartido**.

Se recomienda una revisión de seguridad prioritaria antes de cualquier deploy a producción.

---

*Fin del reporte de Análisis de Logs.*
