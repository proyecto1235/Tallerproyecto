# Auditoría de Implementación OWASP — Robolearn

**Auditor:** Agente 6 — Auditor Independiente de Seguridad  
**Fecha:** 2026-06-12  
**Documentos base:** `04_Auditoria_OWASP.md`, `05_Plan_OWASP.md`  
**Estado:** Post-implementación de remediaciones  

---

## Resumen Ejecutivo

| Indicador | Valor |
|-----------|-------|
| Vulnerabilidades planificadas | 12 |
| ✅ Corregidas correctamente | 7 |
| ⚠️ Parcialmente corregidas | 3 |
| ❌ No corregidas | 0 |
| 🔴 Bugs nuevos introducidos | 1 |
| 🟡 Riesgos residuales | 3 |

**Score OWASP:** 50 → **75**/100 (objetivo: 85)  
**Impacto del bug crítico:** -5 puntos  
**Conclusión:** Implementación mayormente exitosa con 1 bug crítico que debe corregirse antes del deploy.

---

## Estado por Vulnerabilidad

### ✅ C1 — Fortalecer sandbox exec() + timeout — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| `type`, `getattr`, `setattr`, `hasattr` eliminados de `safe_builtins` | `safe_builtins` sin esos símbolos | `exercises_router.py:248-258` |
| Blacklist expandida con `__class__`, `__bases__`, `__subclasses__`, `__mro__`, `__globals__`, `__code__` | `DANGEROUS_PATTERNS` lista completa | `exercises_router.py:281-287` |
| Matching case-insensitive via `code_lower` | `if pattern in code_lower or pattern in request.code` | `exercises_router.py:305-311` |
| Timeout 10s via `asyncio.wait_for` | `_EXEC_TIMEOUT = 10` + `asyncio.wait_for(... timeout=_EXEC_TIMEOUT)` | `exercises_router.py:232,319-328` |
| `exec()` movido a ThreadPoolExecutor | `_get_executor()` con `ThreadPoolExecutor(max_workers=4)` | `exercises_router.py:236-241` |

**Riesgo residual:** `exec()` aún se usa directamente (no se migró a Docker sandbox como indicaba el plan). El enfoque actual es "endurecimiento del `exec()`" en lugar de "reemplazo del `exec()`". Esto es una desviación del plan pero preserva la funcionalidad de `jump()`/`forward()` y reduce significativamente la superficie de ataque. Score A4 sube de 3→7.

---

### ✅ C2 — Segmentar red Docker — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| 3 redes definidas | `frontend_net`, `internal_net`, `ai_net` | `docker-compose.yml:174-183` |
| `internal_net` con `internal: true` | Aislamiento de red interna | `docker-compose.yml:178-180` |
| Frontend solo en `frontend_net` | `networks: - frontend_net` | `docker-compose.yml:165-166` |
| Postgres/Mongo/Redis solo en `internal_net` | Los 3 servicios en `internal_net` | `docker-compose.yml:27-28,51-52,71-72` |
| Backend en las 3 redes | `frontend_net`, `internal_net`, `ai_net` | `docker-compose.yml:143-146` |
| Ollama solo en `ai_net` | `networks: - ai_net` | `docker-compose.yml:89-90` |

**Riesgo residual:** Ninguno. Segmentación completa. Score A10 sube de 3→7.

---

### ⚠️ H1 — Redis con autenticación — PARCIALMENTE CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| `redis_password` field agregado | `redis_password: str = Field(default="", ...)` | `settings.py:44` |
| `REDIS_PASSWORD` env en backend | `REDIS_PASSWORD: ${REDIS_PASSWORD:-}` | `docker-compose.yml:120` |
| Redis command con `--requirepass` | `command: ["redis-server", "--requirepass", "${REDIS_PASSWORD:-}", ...]` | `docker-compose.yml:64` |
| Validator inyecta password en URL | `inject_redis_password` model_validator | `settings.py:98-104` |
| `.env.example` actualizado | `REDIS_PASSWORD=` documentado | `.env.example:44` |

**🔴 Hallazgo:** Si `REDIS_PASSWORD` no está configurada (vacía), Redis arranca SIN autenticación. El `--requirepass ""` es equivalente a no tener password. No hay validación que exija password cuando `NODE_ENV=production`.

```
docker-compose.yml:64
  command: ["redis-server", "--requirepass", "${REDIS_PASSWORD:-}", "--appendonly", "yes"]
  # Si REDIS_PASSWORD no está definida, --requirepass "" → SIN AUTH
```

**Riesgo residual:** Medio — en producción, si el operador no configura `REDIS_PASSWORD`, Redis queda expuesto en la red interna.

**Recomendación:** Agregar validación en `settings.py` que rechace `redis_password` vacío cuando `node_env == "production"`.

---

### ✅ H4 — Eliminar credenciales BD del frontend — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| Frontend solo tiene 2 env vars | `NEXT_PUBLIC_API_URL` y `NEXT_PUBLIC_BACKEND_URL` | `docker-compose.yml:157-159` |
| Variables eliminadas | `POSTGRES_PASSWORD`, `POSTGRES_USER`, `POSTGRES_HOST`, `POSTGRES_DB`, `MONGODB_URI`, `MONGODB_DB`, `JWT_SECRET` | — |

**Riesgo residual:** Ninguno. Score A5 sube de 3→6.

---

### ✅ H6 — verify_admin() consulta DB — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| Consulta DB en verify_admin | `user = await user_repository.get_by_id(token_data.user_id)` | `dependencies.py:144` |
| Verificación de rol desde DB | `if user.role != UserRole.ADMIN:` | `dependencies.py:147` |
| Mismo patrón que verify_teacher() | Idéntica estructura a líneas 134-140 | `dependencies.py:134-149` |

**Riesgo residual:** Mínimo. Depende de la implementación de `UserRepositoryImpl.get_by_id()`.

---

### ✅ H2 — Reemplazar passlib por bcrypt directo — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| No hay imports de passlib en .py | `grep "from passlib"` → 0 resultados | — |
| `_PasswordContext` con bcrypt | `bcrypt.hashpw()`/`bcrypt.checkpw()` | `dependencies.py:32-40` |
| `register_user.py` usa bcrypt directo | `bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())` | `register_user.py:34` |
| `requirements.txt` sin passlib | `bcrypt==3.2.0` presente, `passlib` eliminado | `requirements.txt:5` |
| `[:72]` truncation eliminado | `request.password` sin slice | `auth_router.py:53` |
| Error message leak corregido | `detail="Error interno al verificar la contraseña"` | `auth_router.py:56` |

**Riesgo residual:** Hashes existentes en DB fueron creados con `passlib` con bcrypt. Ambos usan formato `$2b$` compatible. Sin embargo, no hay re-hashing automático en login exitoso.

**Recomendación:** Agregar re-hashing en login cuando el hash fue creado con passlib (no urgente, bcrypt 3.2.0 es compatible con hashes `$2b$` existentes).

---

### ⚠️ H3 — Corregir `except Exception: pass` — PARCIALMENTE CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| `code_executor.py` logging agregado | `logging.getLogger("robolearn").warning(...)` | `code_executor.py:64-65,77-78` |
| Logout logging agregado | `logger.error(f"Error blacklisting token: {e}")` | `auth_router.py:93` |
| `is_token_blacklisted` fail-closed en except | `except Exception: ... return True` | `dependencies.py:109-112` |

**🔴 Hallazgo (inconsistencia):** `is_token_blacklisted` tiene dos caminos de fallo con comportamientos opuestos:

```python
dependencies.py:104-112
async def is_token_blacklisted(token: str) -> bool:
    try:
        r = await rate_limiter._get_redis()
        if r is None:        # ← Redis no disponible (sin excepción)
            return False     #    FAIL-OPEN: token considerado VÁLIDO
        return await r.exists(f"token_blacklist:{token}")
    except Exception as e:   # ← Error inesperado
        logger.error(...)
        return True          #    FAIL-CLOSED: token considerado INVÁLIDO
```

Cuando Redis no está disponible (`_get_redis()` retorna `None`), la función retorna `False` (token NO está en blacklist → válido). Pero cuando hay una excepción, retorna `True` (token SÍ está en blacklist → inválido). Son comportamientos opuestos para la misma condición subyacente (Redis caído).

**Recomendación:** Cambiar `if r is None: return False` → `if r is None: return True` para consistencia fail-closed.

---

### ✅ H5 — Timeout y límite de memoria — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| Timeout en execute_code | `_EXEC_TIMEOUT = 10` + `asyncio.wait_for` | `exercises_router.py:232,319-328` |
| `CodeExecutor` memory limit | `mem_limit="64m"` por defecto | `code_executor.py:10` |
| `CodeExecutor` timeout | `timeout=10` por defecto | `code_executor.py:10` |
| Límite de tamaño de código | 10000 caracteres | `exercises_router.py:303-304` |

**Riesgo residual:** Timeout de 10s puede ser insuficiente para ejercicios que procesan grandes volúmenes de datos. ThreadPoolExecutor limitado a 4 workers.

---

### ⚠️ C3 — Migrar HS256 a RS256 — PARCIALMENTE CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| `jwt_private_key` y `jwt_public_key` en settings | Campos agregados | `settings.py:24-25` |
| `_get_sign_key()` usa RS256 si disponible | `if settings.jwt_private_key: return ..., "RS256"` | `dependencies.py:68-71` |
| `_decode_token_fallback()` prueba RS256→HS256 | Loop de algoritmos con fallback | `dependencies.py:74-87` |
| `auto_algorithm_for_rsa` validator | `if self.jwt_private_key and self.jwt_public_key: self.algorithm = "RS256"` | `settings.py:106-110` |
| `.env.example` documentado | Comentarios con instrucciones `openssl` | `.env.example:22-26` |

**🟡 Hallazgo:** No hay validación del formato PEM de las claves RSA. Si las claves están mal formateadas (faltan headers `-----BEGIN RSA PRIVATE KEY-----`, newlines incorrectos, etc.), `jwt.encode()`/`jwt.decode()` lanzarán `JWTError` sin un mensaje claro sobre la causa raíz.

**Recomendación:** Agregar validación de formato PEM en settings.py usando `cryptography` o `rsa` para verificar que las claves son válidas antes de usarlas.

---

### ❌ M1 — jti + blacklist granular — BUG CRÍTICO

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| `jti` agregado a `create_access_token()` | `to_encode.update({"exp": ..., "iat": ..., "jti": str(uuid.uuid4())})` | `dependencies.py:98` |
| `jti` extraído en `verify_token()` | `jti: str = payload.get("jti")` | `dependencies.py:126` |
| `jti` en TokenData schema | `jti: Optional[str] = None` | `common.py:11` |
| Logout usa `jti` como key | `blacklist_key = token_data.jti if token_data.jti else ...` | `auth_router.py:86` |

**🔴 BUG CRÍTICO — Blacklist key mismatch:**

```python
# logout (auth_router.py:91) — GUARDA con key = jti
await r.setex(f"token_blacklist:{blacklist_key}", ttl, "1")
# blacklist_key = token_data.jti → "token_blacklist:550e8400-..."

# is_token_blacklisted (dependencies.py:108) — BUSCA con key = token completo
return await r.exists(f"token_blacklist:{token}")
# token = "eyJhbGciOiJIUzI1NiIs..." → "token_blacklist:eyJhbGciOi..."
```

**Impacto:** Cuando un token tiene `jti` (todos los tokens nuevos):
1. Usuario hace logout → se guarda `token_blacklist:{uuid}`
2. Usuario intenta usar el token → `is_token_blacklisted` busca `token_blacklist:{jwt_string}` 
3. Las claves no coinciden → blacklist NO encontrada → **token considerado VÁLIDO**
4. El logout no tiene efecto real para tokens con `jti`

**Solución:** Modificar `is_token_blacklisted` para extraer `jti` del token sin verificar firma, y buscar por `token_blacklist:{jti}` con fallback al token completo.

---

### ✅ M2/M3 — Cabeceras de seguridad HTTP — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| `X-XSS-Protection: 1; mode=block` | Cambiado de `"0"` a `"1; mode=block"` | `main.py:83` |
| `Content-Security-Policy` agregada | `default-src 'self'; script-src 'self' ...` | `main.py:88-89` |
| Cabeceras existentes preservadas | `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Permissions-Policy` | `main.py:81-87` |

**Riesgo residual:** CSP se implementó directo (no `Report-Only`). Puede bloquear recursos legítimos del frontend. Monitorear errores de consola post-deploy.

---

### ✅ L1/L2 — iat + no truncar password — CORREGIDA

| Aspecto | Evidencia | Archivo:Línea |
|---------|-----------|---------------|
| `iat` en payload JWT | `to_encode.update({"exp": expire, "iat": now, "jti": ...})` | `dependencies.py:98` |
| Password truncation eliminado | `request.password` sin `[:72]` | `auth_router.py:53` |

**Riesgo residual:** Ninguno.

---

## Resumen de Nuevos Hallazgos

### 🔴 Crítico

| # | Hallazgo | Componente | Impacto | Solución |
|---|----------|-----------|---------|----------|
| B1 | Blacklist key mismatch: logout guarda por `jti`, `is_token_blacklisted` busca por token completo | `dependencies.py:108`, `auth_router.py:91` | Logout no invalida tokens con jti | Extraer jti del token en `is_token_blacklisted` vía decode sin firma |

### 🟡 Medio

| # | Hallazgo | Componente | Impacto | Solución |
|---|----------|-----------|---------|----------|
| B2 | `is_token_blacklisted` fail-open inconsistente cuando `r is None` | `dependencies.py:106-107` | Token válido cuando Redis caído | Cambiar `return False` → `return True` |
| B3 | Redis sin password en producción si `REDIS_PASSWORD` no configurada | `docker-compose.yml:64`, `settings.py` | Redis expuesto | Validar `redis_password` requerido en producción |

### 🟢 Bajo

| # | Hallazgo | Componente | Impacto | Solución |
|---|----------|-----------|---------|----------|
| B4 | Sin validación PEM para claves RS256 | `settings.py:24-25` | Error críptico con claves inválidas | Validar formato PEM en startup |

---

## Score de Seguridad Actualizado

| Categoría OWASP | Score Pre | Score Post | Delta | Justificación |
|----------------|:---------:|:----------:|:-----:|---------------|
| A1: Broken Access Control | 6 | 8 | +2 | verify_admin DB check (+1), jti blacklist roto (-1), rate limit solo auth |
| A2: Cryptographic Failures | 4 | 7 | +3 | bcrypt reemplaza passlib (+2), RS256 disponible (+1), sin refresh tokens |
| A3: Injection | 9 | 9 | 0 | Sin cambios necesarios |
| A4: Insecure Design | 3 | 7 | +4 | Sandbox endurecido (+3), timeout (+1), aún exec() no Docker (-1) |
| A5: Security Misconfiguration | 3 | 8 | +5 | Redes segmentadas (+2), CSP/headers (+1), frontend creds (-1 +1), Redis auth parcial |
| A6: Vulnerable Components | 5 | 7 | +2 | passlib eliminado (+1), bcrypt actualizado (+1), resto sin cambios |
| A7: Authentication Failures | 4 | 7 | +3 | Error message fix (+1), fail-closed parcial (+1), sin MFA/bloqueo |
| A8: Integrity Failures | 6 | 7 | +1 | Frontend creds eliminadas (+1), npm/ollama sin cambios |
| A9: Logging & Monitoring | 7 | 8 | +1 | Logging en except (+1), sin user_id en logs de auditoría |
| A10: SSRF | 3 | 7 | +4 | Redes segmentadas (+3), sandbox endurecido (+1), aún exec() no Docker (-1) |
| **Score Global** | **50** | **75** | **+25** | **Objetivo 85 no alcanzado** |

### Score si se corrigen los bugs

| Bug corregido | Impacto | Score post-corrección |
|--------------|---------|:--------------------:|
| B1 (blacklist jti) | +3 en A1 | **78** |
| B2 (fail-open) | +1 en A7 | **79** |
| B3 (Redis password) | +1 en A5 | **80** |
| B1 + B2 + B3 | +5 total | **80** |

---

## Verificación de Regresiones Funcionales

| Aspecto | Status | Evidencia |
|---------|--------|-----------|
| Contratos de API | ✅ Sin cambios | Todos los endpoints mantienen misma ruta, método y formato de respuesta |
| Tests existentes | ✅ 4/4 pasan | `pytest tests/ -v` → 4 passed |
| Sintaxis Python | ✅ 8 archivos OK | `py_compile` en todos los archivos modificados |
| Formato de respuesta execute-code | ✅ Sin cambios | `{"success", "output", "actions", "error"}` preservado |
| Flujo de autenticación | ✅ Sin cambios | `create_access_token`, `verify_token`, `verify_token_optional` preservan firma |
| Funcionalidad jump/forward | ✅ Preservada | `_build_safe_env()` mantiene `jump()` y `forward()` en el entorno `exec()` |
| Docker Compose | ✅ Sintaxis YAML válida | 3 redes, servicios asignados correctamente |

**Conclusión de regresiones:** No se detectaron regresiones funcionales.

---

## Conclusión General

La implementación del plan OWASP fue **mayoritariamente exitosa** pero no completa:

- **7/12** vulnerabilidades corregidas correctamente
- **3/12** corregidas parcialmente con riesgos residuales bajos/medios
- **1 bug crítico introducido** (B1 — blacklist jti mismatch) que debe corregirse antes del deploy
- **2 bugs menores** (B2 fail-open, B3 Redis password) que deben corregirse en el mismo sprint

El score de seguridad subió de **50→75/100**, quedando a 10 puntos del objetivo de 85. Con la corrección de los 3 bugs detectados, el score alcanzaría **~80/100**, requiriendo mejoras adicionales (MFA, refresh tokens, Docker sandbox real, CSP Report-Only testing) para llegar a 85.

**Recomendación:** Corregir B1, B2 y B3 antes del deploy a producción.

---

*Documento generado por Agente 6 — Auditor Independiente de Seguridad.*
*Basado en el estado post-implementación de `05_Plan_OWASP.md`.*
