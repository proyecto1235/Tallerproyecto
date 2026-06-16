# Auditoría de Seguridad OWASP Top 10 — Robolearn

**Fecha:** 2026-06-12  
**Versión del código:** commit actual (post-FURPS+ Fase 2)  
**Alcance:** `backend/`, `frontend/`, `docker-compose.yml`

---

## Score Global de Seguridad: 🔴 50/100

| Categoría OWASP | Severidad | Score |
|----------------|-----------|:-----:|
| A1: Broken Access Control | 🟡 Medio | 6/10 |
| A2: Cryptographic Failures | 🔴 Alto | 4/10 |
| A3: Injection | 🟢 Bajo | 9/10 |
| A4: Insecure Design | 🔴 Crítico | 3/10 |
| A5: Security Misconfiguration | 🔴 Alto | 3/10 |
| A6: Vulnerable Components | 🟡 Medio | 5/10 |
| A7: Authentication Failures | 🔴 Alto | 4/10 |
| A8: Software/Data Integrity Failures | 🟡 Medio | 6/10 |
| A9: Security Logging & Monitoring Failures | 🟢 Bajo | 7/10 |
| A10: Server-Side Request Forgery (SSRF) | 🔴 Alto | 3/10 |
| **Score Global** | **🔴 50/100** | |

---

## A1: Broken Access Control 🟡 Medio (6/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 1.1 | `verify_admin()` confía ciegamente en el claim `role` del JWT sin verificación en base de datos | `app/dependencies.py` | ~205 | 🔴 Alto |
| 1.2 | Rol administrador incrustado en JWT sin mecanismo de revocación | `app/dependencies.py` | ~200-210 | 🟡 Medio |
| 1.3 | No hay `jti` (token ID) — la blacklist usa el token completo como clave Redis | `app/dependencies.py` | ~155 | 🟡 Medio |
| 1.4 | No hay rate limiting por recurso (solo global en `/api/auth/`) | `app/main.py` | ~40 | 🟢 Bajo |

### Detalle

**1.1:** `verify_admin()` decodifica el JWT y verifica `payload.get("role") == "admin"` pero nunca consulta la base de datos para confirmar que el usuario sigue teniendo rol admin. Si un JWT es forjado con `role: admin`, el middleware lo acepta. Contraste con `verify_teacher()` que sí hace una consulta DB (`await db.fetchrow(...)`).

**1.2:** No hay forma de revocar el acceso de un usuario al que se le quitó el rol admin hasta que su token expire. La blacklist solo cubre logout explícito.

### Recomendación

- Hacer que `verify_admin()` también consulte la DB para verificar el rol actual
- Agregar `jti` (JWT ID) al payload y usar Redis para invalidar tokens por `jti` en lugar del token completo
- Agregar rate limiting por ruta sensible

---

## A2: Cryptographic Failures 🔴 Alto (4/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 2.1 | Algoritmo HS256 simétrico — si `SECRET_KEY` se filtra, todos los tokens son forjables | `config/settings.py` | ~30 | 🔴 Crítico |
| 2.2 | No hay `iat` (issued-at) en el JWT — sin trazabilidad | `app/dependencies.py` | ~135 | 🟡 Medio |
| 2.3 | Sin refresh tokens — tokens longeva (hasta 365 días si se configura) | `app/dependencies.py` | ~130 | 🟡 Medio |
| 2.4 | `passlib==1.7.4` sin mantenimiento desde 2022 | `requirements.txt` | — | 🟡 Medio |
| 2.5 | Contraseña truncada a 72 caracteres antes de verificar | `app/dependencies.py` | ~120 | 🟢 Bajo |
| 2.6 | Filtrado de excepción criptográfica al cliente | `app/dependencies.py` | ~125 | 🟡 Medio |

### Detalle

**2.1:** HS256 requiere que el cliente y servidor compartan el mismo secreto. Cualquier leak de `SECRET_KEY` (en logs, en docker-compose, en `.env` subido a git) permite forjar tokens arbitrarios. Se recomienda migrar a RS256 (asimétrico) o usar un proveedor externo (Auth0, Firebase).

**2.4:** `passlib` es la biblioteca de hashing de contraseñas y no recibe mantenimiento desde 2022. Vulnerabilidades conocidas sin parche.

**2.6:** La línea `detail=f"Password verification error: {e}"` filtra el mensaje de error de bcrypt al cliente, exponiendo detalles internos del sistema de hashing.

### Recomendación

- Migrar a RS256 (clave pública/privada) para JWT
- Actualizar `passlib` → `bcrypt` o `argon2` directamente
- No truncar contraseñas
- No filtrar excepciones criptográficas al cliente
- Agregar `iat` y `jti` a los tokens

---

## A3: Injection 🟢 Bajo (9/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 3.1 | ✅ Todas las consultas SQL usan parámetros `%s` | Todos los routers | — | 🟢 Sin riesgo |
| 3.2 | ✅ No hay concatenación de strings en SQL | Todos los routers | — | 🟢 Sin riesgo |
| 3.3 | No se identificó NoSQL injection visible | — | — | 🟢 Sin riesgo |
| 3.4 | Sin command injection visible | — | — | 🟢 Sin riesgo |

### Detalle

No se encontraron vulnerabilidades de inyección. Todas las consultas SQL usan parámetros posicionales (`%s`). Las construcciones f-string en SQL solo usan nombres de columna que están hardcodeados, no derivados de input del usuario.

### Recomendación

- Mantener el patrón actual de uso de parámetros `%s`
- Agregar pruebas de seguridad (fuzzing) para endpoints que aceptan SQL-like input

---

## A4: Insecure Design 🔴 Crítico (3/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 4.1 | Sandbox `exec()` es trivialmente evadible — acceso a objetos internos de Python | `infrastructure/adapters/input/exercises_router.py` | ~80-120 | 🔴 Crítico |
| 4.2 | Blacklist case-sensitive — `"import os"` bloqueado pero `"Import OS"` no | `infrastructure/adapters/input/exercises_router.py` | ~90 | 🔴 Crítico |
| 4.3 | Sin timeout en `exec()` — loop infinito congela el worker async | `infrastructure/adapters/input/exercises_router.py` | ~100 | 🔴 Alto |
| 4.4 | Sin límite de memoria en sandbox `exec()` | `infrastructure/adapters/input/exercises_router.py` | ~80-120 | 🟡 Medio |
| 4.5 | `safe_builtins` incluye `getattr`, `type`, `eval` — vectores de escape conocidos | `infrastructure/adapters/input/exercises_router.py` | ~85 | 🔴 Crítico |

### Detalle

**4.1-4.5:** El endpoint `/api/execute-code` implementa un sandbox vía `exec()` con `safe_builtins` restringidos y una blacklist de palabras clave. Sin embargo:

- `().__class__.__bases__[0].__subclasses__()` NO está bloqueado — permite acceder a TODAS las clases cargadas en el intérprete, incluyendo `os.Popen`, `subprocess.Popen`, etc.
- `getattr` está en `safe_builtins` — permite bypassear la blacklist de atributos
- `eval` está permitido indirectamente

El Docker sandbox (`CodeExecutor`) sí es seguro (network_disabled, read-only filesystem, sin capabilities), pero el endpoint NO usa este sandbox — usa el `exec()` inseguro.

### Recomendación

- **URGENTE**: Reemplazar `exec()` con el Docker sandbox (`CodeExecutor`) como mecanismo único de ejecución
- Agregar timeout de 5 segundos a toda ejecución de código
- Agregar límite de memoria por contenedor (vía `docker run --memory`)
- Eliminar completamente el sandbox basado en `exec()` — es imposible de asegurar

---

## A5: Security Misconfiguration 🔴 Alto (3/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 5.1 | PostgreSQL, MongoDB y Redis sin contraseña por defecto | `.env.example`, `docker-compose.yml` | — | 🔴 Alto |
| 5.2 | Frontend recibe credenciales de base de datos en docker-compose | `docker-compose.yml` | — | 🔴 Alto |
| 5.3 | Ruta de Google credentials key por defecto (`./backend/robolearn-key.json`) | `config/settings.py` | — | 🟡 Medio |
| 5.4 | Redis sin AUTH — cualquiera en la red Docker tiene acceso total | `docker-compose.yml` | — | 🔴 Alto |
| 5.5 | Sin `Content-Security-Policy` header | `backend/app/main.py` | — | 🟡 Medio |
| 5.6 | Sin HTTPS redirect middleware | `backend/app/main.py` | — | 🟡 Medio |
| 5.7 | `X-XSS-Protection: 0` — deshabilita el filtro XSS del navegador | `backend/app/main.py` | — | 🟡 Medio |
| 5.8 | `token_blacklist` falla abierto si Redis no está disponible | `app/dependencies.py` | ~160 | 🟡 Medio |
| 5.9 | Red Docker plana — 6 servicios comparten la misma red sin segmentación | `docker-compose.yml` | — | 🟡 Medio |

### Detalle

**5.2:** El frontend en `docker-compose.yml` tiene acceso a variables de entorno con credenciales de base de datos (`POSTGRES_PASSWORD`, `MONGODB_URI`). Si el bundle client-side incluye accidentalmente estos módulos (Next.js puede tree-shake incorrectamente), las credenciales se exponen al navegador.

**5.8:** Cuando Redis no está disponible, `token_blacklist(...)` captura la excepción con `except Exception: pass` y retorna exitosamente — el token se considera válido aunque debería estar en blacklist.

### Recomendación

- Configurar contraseñas obligatorias para todos los servicios de datos
- Eliminar credenciales de BD del frontend en docker-compose
- Agregar `requirepass` a Redis
- Agregar cabeceras de seguridad: `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`
- Cambiar `X-XSS-Protection: 0` a `X-XSS-Protection: 1; mode=block`
- Hacer que `token_blacklist` falle cerrado cuando Redis no está disponible
- Segmentar la red Docker en al menos 2 redes (frontend + backend, servicios internos)

---

## A6: Vulnerable Components 🟡 Medio (5/10)

### Hallazgos

| # | Hallazgo | Versión actual | Última versión | Severidad |
|---|---------|---------------|----------------|-----------|
| 6.1 | `fastapi` desactualizado | 0.109.0 | ~0.115.x | 🟡 Medio |
| 6.2 | `passlib` sin mantenimiento | 1.7.4 (2022) | — (abandonado) | 🟡 Medio |
| 6.3 | `python-jose` semi-abandonado | 3.3.0 (2021) | — | 🟡 Medio |
| 6.4 | `requests` con CVE conocido | 2.31.0 | 2.32.0+ | 🟡 Medio |
| 6.5 | `pydantic` desactualizado | 2.5.0 | 2.10.x | 🟢 Bajo |
| 6.6 | `ollama:latest` tag mutable en docker-compose | latest | — | 🟡 Medio |
| 6.7 | `jsonwebtoken` + `jose` duplicados en frontend | — | — | 🟢 Bajo |

### Recomendación

- Actualizar todas las dependencias a sus últimas versiones estables
- Reemplazar `passlib` con `bcrypt` o `argon2` directo
- Reemplazar `python-jose` con `PyJWT` (mantenido activamente)
- Usar `ollama:0.3.x` (tag fijo) en lugar de `:latest`
- Eliminar dependencia duplicada `jose` del frontend si `jsonwebtoken` es suficiente

---

## A7: Authentication Failures 🔴 Alto (4/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 7.1 | Mensaje de excepción filtrado al cliente: `detail=f"Password verification error: {e}"` | `app/dependencies.py` | ~125 | 🔴 Alto |
| 7.2 | `except Exception: pass` silencia errores de Redis/blacklist | `app/dependencies.py` | ~160 | 🔴 Alto |
| 7.3 | Password truncado a 72 caracteres | `app/dependencies.py` | ~120 | 🟡 Medio |
| 7.4 | Sin bloqueo por intentos fallidos (solo rate limiting por IP) | `app/dependencies.py` | — | 🟡 Medio |
| 7.5 | Sin MFA, sin verificación de email, sin password reset | — | — | 🟡 Medio |

### Detalle

**7.2:** Hay 3 lugares donde `except Exception: pass` oculta errores críticos:
- `token_blacklist()`: si Redis falla, el token se considera válido
- Operaciones de caché: si Redis falla, se devuelve `None` silenciosamente
- Esto impide detectar ataques de denegación de servicio contra Redis

### Recomendación

- No filtrar detalles de excepciones al cliente — usar mensajes genéricos
- Reemplazar `except Exception: pass` con logging + manejo explícito
- Agregar bloqueo de cuenta después de N intentos fallidos
- Considerar agregar MFA y verificación de email

---

## A8: Software/Data Integrity Failures 🟡 Medio (6/10)

### Hallazgos

| # | Hallazgo | Archivo | Severidad |
|---|---------|---------|-----------|
| 8.1 | `npm install` en Dockerfile en vez de `npm ci` | `Dockerfile` | 🟡 Medio |
| 8.2 | `ollama:latest` — actualización impredecible | `docker-compose.yml` | 🟡 Medio |
| 8.3 | No hay verificación de firmas en dependencias | `requirements.txt`, `package.json` | 🟢 Bajo |
| 8.4 | Frontend con drivers `pg` y `mongodb` — riesgo de leak en bundle | `package.json` | 🟡 Medio |

### Detalle

**8.1:** `npm install` permite drift de versiones — la misma imagen construida en distintas fechas puede tener distintas dependencias transactivas. `npm ci` instala exactamente lo que está en `package-lock.json`.

**8.4:** El frontend tiene `pg` y `mongodb` como dependencias. Si Next.js incluye estos módulos en el bundle client-side (por ejemplo, mediante import incorrecto), las credenciales de base de datos expuestas en docker-compose quedarían disponibles en el navegador.

### Recomendación

- Cambiar `npm install` → `npm ci` en Dockerfile
- Usar tags fijos para todas las imágenes Docker
- Eliminar dependencias de base de datos del frontend si no son necesarias

---

## A9: Security Logging & Monitoring Failures 🟢 Bajo (7/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 9.1 | No se loggea el user ID en rutas sensibles | `app/logging_config.py` | — | 🟡 Medio |
| 9.2 | No se loggea el resultado (success/failure) de operaciones de auth | `app/dependencies.py` | ~125 | 🟡 Medio |
| 9.3 | `except Exception: pass` evita que errores críticos sean registrados | Múltiples archivos | — | 🔴 Alto |
| 9.4 | Sin alertas de seguridad automáticas | — | — | 🟡 Medio |

### Recomendación

- Incluir `user_id` y `result` (success/failure) en todos los logs de auditoría
- Agregar logger a todos los `except` que actualmente son `pass`
- Configurar alertas para: múltiples login fallidos, errores de Redis, accesos a rutas admin

---

## A10: Server-Side Request Forgery (SSRF) 🔴 Alto (3/10)

### Hallazgos

| # | Hallazgo | Archivo | Línea | Severidad |
|---|---------|---------|-------|-----------|
| 10.1 | Sandbox `exec()` evadido permite acceso completo a red interna | `exercises_router.py` | ~80-120 | 🔴 Crítico |
| 10.2 | Red plana: 6 servicios sin segmentación | `docker-compose.yml` | — | 🔴 Alto |
| 10.3 | El atacante puede atacar postgres:5432, mongo:27017, redis:6379, ollama:11434 | — | — | 🔴 Crítico |
| 10.4 | No hay SSRF directo vía input de usuario | — | — | 🟢 Bajo |

### Detalle

**10.1-10.3:** Aunque la aplicación no acepta URLs de usuario directamente, la vulnerabilidad A4 (sandbox `exec()` evadible) permite ejecución remota de código en el contenedor backend. Una vez dentro, el atacante tiene acceso a TODOS los servicios de la red plana:
- `postgres:5432` — robo/exfiltración de datos
- `mongo:27017` — robo de datos de usuario
- `redis:6379` — manipulación de sesiones/blacklist
- `ollama:11434` — consultas maliciosas al LLM, posible jailbreak
- `frontend:3000` — XSS server-side

### Recomendación

- **URGENTE**: Deshabilitar el sandbox `exec()` y usar solo Docker sandbox
- **URGENTE**: Segmentar red Docker en 3 capas:
  - Red pública: frontend, backend
  - Red interna: postgres, mongo, redis (sin acceso desde frontend)
  - Red aislada: ollama (solo backend → ollama, sin retorno)
- Agregar reglas de iptables/firewall entre servicios

---

## Resumen de Recomendaciones Priorizadas

### 🔴 Críticas (acción inmediata)

| # | Acción | Categoría | Esfuerzo | Impacto |
|---|-------|-----------|----------|---------|
| C1 | Reemplazar sandbox `exec()` por Docker sandbox en `/api/execute-code` | A4, A10 | 1 día | Elimina RCE y SSRF |
| C2 | Segmentar red Docker en 3 capas | A10, A5 | 1 día | Contiene daño post-exploit |
| C3 | Migrar a RS256 o proveedor externo para JWT | A2 | 2 días | Elimina riesgo de forja de tokens |

### 🔴 Altas (próximo sprint)

| # | Acción | Categoría | Esfuerzo | Impacto |
|---|-------|-----------|----------|---------|
| H1 | Agregar autenticación a Redis (requirepass) | A5 | 30 min | Protege sesiones y blacklist |
| H2 | Reemplazar `passlib` por `bcrypt`/`argon2` | A2 | 1 hora | Hashing de passwords seguro |
| H3 | Corregir `except Exception: pass` para que falle cerrado | A7, A9 | 30 min | Previene fallos silenciosos |
| H4 | Eliminar credenciales de BD del frontend | A5, A8 | 30 min | Elimina leak de credenciales |
| H5 | Agregar timeout y límite de memoria a ejecución de código | A4 | 1 hora | Mitiga DoS |
| H6 | Hacer `verify_admin()` consultar DB | A1 | 30 min | Verificación real de rol admin |

### 🟡 Medias (próximo release)

| # | Acción | Categoría | Esfuerzo | Impacto |
|---|-------|-----------|----------|---------|
| M1 | Agregar `jti` a JWT, mejorar blacklist | A1, A2 | 1 hora | Revocación granular de tokens |
| M2 | Agregar `Content-Security-Policy` y otras cabeceras | A5 | 30 min | Mitiga XSS |
| M3 | Cambiar `X-XSS-Protection: 0` → `1; mode=block` | A5 | 5 min | Activa filtro XSS |
| M4 | Agregar rate limiting por ruta | A1 | 1 hora | Mitiga brute force |
| M5 | Actualizar dependencias (fastapi, requests, pydantic) | A6 | 1 hora | Parches de seguridad |
| M6 | Usar `npm ci` y tags fijos Docker | A8 | 30 min | Integridad de dependencias |

### 🟢 Bajas (backlog)

| # | Acción | Categoría | Esfuerzo | Impacto |
|---|-------|-----------|----------|---------|
| L1 | Agregar `iat` a JWT | A2 | 5 min | Trazabilidad |
| L2 | No truncar contraseñas a 72 chars | A7 | 5 min | Consistencia |
| L3 | Agregar bloqueo por intentos fallidos | A7 | 2 horas | Mitiga brute force |
| L4 | Agregar logging de user ID en rutas sensibles | A9 | 1 hora | Auditoría |
| L5 | Eliminar `jose` duplicado del frontend | A6 | 10 min | Limpieza |

---

## Scoring Methodology

- Cada categoría OWASP se puntúa de 1 a 10 basado en:
  - Número de hallazgos por severidad (Crítico: -3, Alto: -2, Medio: -1, Bajo: -0.5)
  - Puntuación base de 10, con descuentos acumulativos
  - Factor de explotabilidad (facilidad de ataque)
  - Factor de impacto (daño potencial)
- Score Global = promedio de los 10 scores individuales

---

*Documento generado automáticamente como parte del plan de mejora FURPS+.*
*Próximo paso: Fase 3 (Query Optimization, UX, Accessibility) y Fase 4 (Monitoring, Tech Debt).*
