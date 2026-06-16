# Plan de Remediación OWASP Top 10 — Robolearn

**Versión:** 1.0  
**Basado en:** `04_Auditoria_OWASP.md`  
**Objetivo:** Score objetivo 85/100 (desde 50/100 actual)

---

## Roadmap de Remediación

```
Fase 1: Contención (Día 1-2)
Fase 2: Fortalecimiento (Día 3-4)
Fase 3: Madurez (Día 5-7)
```

---

## Fase 1 — Contención 🔴 Crítica (Día 1-2)

### 1. C1 — Reemplazar sandbox `exec()` por Docker sandbox

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Crítico — RCE en el contenedor backend permite comprometer toda la infraestructura |
| **Prioridad** | 1 (inmediata) |
| **Impacto** | Elimina RCE y SSRF (A4 + A10). Puntaje OWASP sube de 50→62 |
| **Componentes** | `exercises_router.py:268`, `sandbox_service.py`, `code_executor.py` |
| **Estrategia de mitigación** | Deshabilitar el `exec()` directo en `exercises_router.py:268` y redirigir toda ejecución de código a `SandboxService.execute_code()` que usa `CodeExecutor` con `network_disabled=True`, `read_only=True`, `cap_drop=["ALL"]`, `mem_limit="64m"`, timeout=10s. Agregar validación sintáctica con `ast.parse()` ANTES de enviar a Docker |
| **Estrategia de validación** | 1. Test unitario: enviar `().__class__.__bases__[0].__subclasses__()` debe fallar con seguridad. 2. Test de integración: código válido debe ejecutarse y retornar resultado. 3. Test de timeout: loop infinito debe terminar en ≤10s |
| **Estrategia de rollback** | Revertir el cambio en `exercises_router.py` línea 232-271 (reemplazar `exec()` por `await sandbox_service.execute_code()`). Commit atómico: `git revert <commit-sha>` |
| **Riesgos de implementación** | Docker no disponible en CI/test → mockear `CodeExecutor`. En producción, si Docker daemon no responde, retornar 503 con mensaje claro. Usar feature flag `EXECUTE_CODE_USE_DOCKER=true/false` durante migración |

---

### 2. C2 — Segmentar red Docker

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Crítico — red plana permite que cualquier servicio comprometido ataque a todos los demás |
| **Prioridad** | 2 |
| **Impacto** | Contiene daño post-exploit. Puntaje A10 sube de 3→7 |
| **Componentes** | `docker-compose.yml` — todos los servicios |
| **Estrategia de mitigación** | Crear 3 redes: `frontend_net` (frontend, backend), `internal_net` (postgres, mongo, redis — sin frontend), `ai_net` (backend↔ollama). Backend se conecta a las 3 redes. Frontend solo a `frontend_net`. Postgres/Mongo/Redis solo en `internal_net`. Ollama solo en `ai_net` |
| **Estrategia de validación** | 1. `docker-compose up` debe iniciar todos los servicios sin errores. 2. Backend debe poder consultar postgres, mongo, redis. 3. Frontend NO debe poder alcanzar postgres:5432, mongo:27017, redis:6379. 4. Ollama solo accesible desde backend. 5. Tests de integración existentes deben pasar |
| **Estrategia de rollback** | Revertir el archivo `docker-compose.yml` completo. Commit atómico con solo cambios de red |
| **Riesgos de implementación** | Servicios no se descubren por nombre DNS entre redes. Backend necesita estar en todas las redes (multi-net). Probar en staging con mismo `docker-compose.yml` antes de producción |

---

### 3. H1 — Redis con autenticación

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Alto — cualquiera en la red Docker puede leer/modificar sesiones, blacklist, caché |
| **Prioridad** | 3 |
| **Impacto** | Elimina acceso no autorizado a Redis |
| **Componentes** | `docker-compose.yml` (redis service), `config/settings.py`, `app/dependencies.py` |
| **Estrategia de mitigación** | Agregar `REDIS_PASSWORD` a `.env.example`. En `docker-compose.yml`: `redis` service recibe `--requirepass ${REDIS_PASSWORD:?error}`. En `settings.py`: agregar `redis_password: str = Field(default="")`. En URL de Redis: `redis://:${REDIS_PASSWORD}@redis:6379/0`. RateLimiter y AICache usan URL con password |
| **Estrategia de validación** | 1. Sin password set → Redis rechaza conexión. 2. Con password correcto → conexión exitosa. 3. Backend funciona normalmente con password configurada. 4. Tests de blacklist y rate limiter pasan |
| **Estrategia de rollback** | Revertir cambios en docker-compose y settings.py. Si backend no puede conectar a Redis, fallback a comportamiento sin Redis (logging de warning) |
| **Riesgos de implementación** | Backend no tiene la password → no puede conectar a Redis. La blacklist y rate limiting dejan de funcionar. Mitigación: validar conexión Redis al startup con logging claro |

---

### 4. H4 — Eliminar credenciales de BD del frontend

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Alto — si Next.js incluye drivers pg/mongodb en bundle client-side, credenciales expuestas al navegador |
| **Prioridad** | 4 |
| **Impacto** | Elimina vector de leak de credenciales en frontend |
| **Componentes** | `docker-compose.yml` (frontend service) |
| **Estrategia de mitigación** | Eliminar del bloque `environment` del servicio frontend: `POSTGRES_PASSWORD`, `POSTGRES_USER`, `POSTGRES_HOST`, `POSTGRES_DB`, `MONGODB_URI`, `MONGODB_DB`, `JWT_SECRET`. Si el frontend necesita SSR para BD, migrar esas consultas al backend |
| **Estrategia de validación** | 1. Frontend debe construir sin errores. 2. Ninguna funcionalidad SSR debe fallar. 3. Buscar imports de `pg` o `mongodb` en `frontend/src/` — si existen, están mal |
| **Estrategia de rollback** | Revertir solo las líneas eliminadas del frontend service en docker-compose |
| **Riesgos de implementación** | Frontend puede depender de acceso directo a BD para SSR (páginas servidas desde servidor Next.js). Auditar imports primero |

---

## Fase 2 — Fortalecimiento 🔴 Alta (Día 3-4)

### 5. H6 — `verify_admin()` consulta DB

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Alto — JWT forjado con `role: admin` es aceptado sin verificar DB |
| **Prioridad** | 5 |
| **Impacto** | Verificación real de rol admin, eliminando confianza ciega en JWT |
| **Componentes** | `app/dependencies.py:106` — función `verify_admin()` |
| **Estrategia de mitigación** | Agregar consulta `SELECT role FROM users WHERE id = %s` en `verify_admin()` idéntica a `verify_teacher()`. Si el rol en DB no es ADMIN, retornar 403. Si el usuario no existe en DB, retornar 404 |
| **Estrategia de validación** | 1. Test: JWT con `role: admin` pero usuario normal en DB → 403. 2. Test: JWT admin válido → 200. 3. Test: usuario eliminado de DB pero JWT vigente → 404 |
| **Estrategia de rollback** | Revertir la función `verify_admin()` a su versión anterior (solo validación JWT) |
| **Riesgos de implementación** | Mínimo — exactamente el mismo patrón que `verify_teacher()` líneas 97-103, que ya funciona y está testeado |

---

### 6. H2 — Reemplazar `passlib` por `bcrypt`

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🟡 Medio — `passlib` sin mantenimiento desde 2022, potenciales vulnerabilidades sin parche |
| **Prioridad** | 6 |
| **Impacto** | Hashing de passwords con biblioteca mantenida activamente |
| **Componentes** | `app/dependencies.py:32` (pwd_context), `auth_router.py` (registro/login), `requirements.txt` |
| **Estrategia de mitigación** | 1. Agregar `bcrypt` a `requirements.txt`. 2. Reemplazar `pwd_context = CryptContext(schemes=["bcrypt"])` por funciones directas con `bcrypt`. 3. Mantener función de verificación legacy para hashes existentes. 4. Agregar columna `hash_version` en users (opcional). 5. Al hacer login exitoso con hash legacy, re-hashear con bcrypt nuevo y actualizar DB |
| **Estrategia de validación** | 1. Test: password nuevo → hash con bcrypt nuevo → verify OK. 2. Test: password existente hasheada con passlib → verify OK (compatibilidad). 3. Test: password incorrecto → verify falla. 4. Tests de registro y login existentes pasan |
| **Estrategia de rollback** | 1. Mantener import de `passlib` pero no usarlo por defecto. 2. Si hay fallos, activar `USE_LEGACY_HASH=true` feature flag. 3. Revertir commit si es necesario |
| **Riesgos de implementación** | Hashes existentes en DB no pueden ser verificados por `bcrypt` directo. Solución: intentar bcrypt nuevo, si falla intentar passlib legacy, y re-hashear en login exitoso. Esto asegura migración gradual sin downtime |

---

### 7. H3 — Corregir `except Exception: pass`

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Alto — errores silenciados pueden ocultar ataques o fallos críticos |
| **Prioridad** | 7 |
| **Impacto** | Fail-closed en blacklist de tokens, visibilidad de errores |
| **Componentes** | `app/dependencies.py:74-76` (is_token_blacklisted), `app/dependencies.py:130-228` (check_and_award_achievements), `code_executor.py:63,75` (finally blocks) |
| **Estrategia de mitigación** | 1. `is_token_blacklisted()`: cambiar `except Exception: pass` por `logger.error(...) + return True` (fail-closed — si Redis no responde, asumir token inválido). 2. `check_and_award_achievements()`: ya tiene logger.warning — mantener. 3. `code_executor.py finally`: cambiar `except Exception: pass` por `logger.warning(...)` |
| **Estrategia de validación** | 1. Test: Redis caído → token no se puede validar → 401. 2. Test: Redis funcionando → token válido → 200. 3. Logs deben mostrar error cuando Redis falla |
| **Estrategia de rollback** | Revertir cada bloque individualmente (3 cambios independientes) |
| **Riesgos de implementación** | Fail-closed en blacklist: si Redis tiene una caída, todos los usuarios deben re-login. Es el comportamiento correcto para seguridad. Documentar en runbook |

---

### 8. H5 — Timeout y límite de memoria en ejecución

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Alto — loop infinito en `exec()` congela el worker async (sin timeout en `exercises_router.py:268`) |
| **Prioridad** | 8 |
| **Impacto** | Previene DoS por código malicioso en `/api/execute-code` |
| **Componentes** | `exercises_router.py:268` (exec directo), `sandbox_service.py`, `code_executor.py:10` (timeout/memory) |
| **Estrategia de mitigación** | 1. Eliminar `exec()` directo (ver ítem 1 — C1). 2. En `sandbox_service.py`, verificar que `CodeExecutor` tenga timeout ≤10s y mem_limit ≤64m. 3. Agregar validación de tamaño de código (ya existe 10000 chars). 4. Agregar timeout de red en `rate_limiter.py` para evitar waits infinitos en Redis |
| **Estrategia de validación** | 1. Test: loop infinito → timeout en ≤10s. 2. Test: código de 15KB → rechazado. 3. Test: código con consumo excesivo de memoria → error |
| **Estrategia de rollback** | Depende de C1. Si C1 está implementado, el timeout y memoria están en `CodeExecutor.__init__()` — revertir valores a los anteriores |
| **Riesgos de implementación** | Timeout muy corto puede fallar ejercicios que requieren computación intensiva. Valor recomendado: 10s inicial, ajustable vía settings |

---

## Fase 3 — Madurez 🟡 Media (Día 5-7)

### 9. C3 — Migrar HS256 a RS256

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🔴 Crítico — si SECRET_KEY se filtra, todos los tokens son forjables |
| **Prioridad** | 9 |
| **Impacto** | Elimina riesgo de forja masiva de tokens por leak de clave simétrica |
| **Componentes** | `config/settings.py`, `app/dependencies.py:59-66` (create_access_token, verify_token), frontend JWT decoding |
| **Estrategia de mitigación** | 1. Generar par RSA de 2048 bits. 2. Agregar `JWT_PUBLIC_KEY` y `JWT_PRIVATE_KEY` a settings. 3. `create_access_token()`: firmar con clave privada RS256. 4. `verify_token()`: verificar con clave pública RS256. 5. Mantener validación HS256 como fallback durante 2 períodos de expiración (por defecto 120 min). 6. Exponer endpoint `/api/auth/public-key` para frontend. 7. Frontend: actualizar librería JWT para usar clave pública |
| **Estrategia de validación** | 1. Test: token firmado con RS256 → verify OK. 2. Test: token HS256 legacy → verify OK (fallback). 3. Test: token firmado con clave diferente → verify falla. 4. Test: token expirado → 401. 5. Test de integración: flujo login → token → request autenticado → OK |
| **Estrategia de rollback** | Revertir `create_access_token()` y `verify_token()` a HS256. Los tokens RS256 existentes no funcionarán con HS256 — los usuarios deben re-login. Por eso la ventana de doble validación |
| **Riesgos de implementación** | 1. Tokens activos sin migrar dejan de funcionar → usar fallback HS256 por 2 períodos de expiración. 2. Frontend necesita clave pública para verificar tokens → endpoint dedicado. 3. Latencia RSA ligeramente mayor que HS256 → benchmark (<1ms, aceptable) |

---

### 10. M1 — `jti` + blacklist granular

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🟡 Medio — no se puede revocar un token individual sin conocer el string completo |
| **Prioridad** | 10 |
| **Impacto** | Revocación granular de tokens por `jti` en lugar del token completo (que es mucho más grande) |
| **Componentes** | `app/dependencies.py:59-66` (create_access_token), `app/dependencies.py:69-76` (is_token_blacklisted), `app/dependencies.py:79-94` (verify_token) |
| **Estrategia de mitigación** | 1. Generar `jti = str(uuid.uuid4())` en `create_access_token()`. 2. Agregar `iat = datetime.now(timezone.utc)` al payload. 3. Blacklist usa `token_blacklist:{jti}` como clave Redis en lugar de `token_blacklist:{token_completo}`. 4. `verify_token()` extrae `jti` del payload y consulta blacklist por `jti` |
| **Estrategia de validación** | 1. Test: token nuevo tiene `jti` y `iat` en payload. 2. Test: revocar token por `jti` → siguiente request con ese token da 401. 3. Test: tokens sin `jti` (legacy) se manejan con blacklist antigua |
| **Estrategia de rollback** | Revertir `create_access_token()` y las funciones de blacklist a versiones anteriores. Tokens con `jti` siguen siendo válidos (blacklist legacy no los reconocería — aceptable) |
| **Riesgos de implementación** | Compatibilidad hacia atrás con tokens que no tienen `jti`. Solución: si `jti` no está presente, usar el token completo como clave (comportamiento legacy) |

---

### 11. M2/M3 — Cabeceras de seguridad HTTP

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🟡 Medio — falta de CSP permite XSS, `X-XSS-Protection: 0` deshabilita protección del navegador |
| **Prioridad** | 11 |
| **Impacto** | Previene XSS, clickjacking, MIME sniffing |
| **Componentes** | `app/main.py:78-88` (add_security_headers middleware) |
| **Estrategia de mitigación** | 1. Cambiar `X-XSS-Protection: 0` → `X-XSS-Protection: 1; mode=block`. 2. Agregar `Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'`. 3. Agregar `Cross-Origin-Opener-Policy: same-origin`. 4. Agregar `Cross-Origin-Embedder-Policy: require-corp` |
| **Estrategia de validación** | 1. Test: response headers contienen todas las cabeceras nuevas. 2. Frontend carga sin errores de CSP en consola. 3. Test de penetración: XSS reflejado debe ser bloqueado |
| **Estrategia de rollback** | Revertir las líneas de cabeceras en `add_security_headers()` |
| **Riesgos de implementación** | CSP puede bloquear recursos legítimos (Google Fonts, CDNs, WebSockets, etc.). Auditar TODOS los orígenes externos usados por frontend antes de implementar. Usar `Content-Security-Policy-Report-Only` inicialmente para identificar falsos positivos |

---

### 12. L1/L2 — `iat` + no truncar password

| Campo | Detalle |
|-------|---------|
| **Riesgo** | 🟢 Bajo — falta de `iat` reduce trazabilidad; truncar password a 72 chars es innecesario con bcrypt moderno |
| **Prioridad** | 12 |
| **Impacto** | Trazabilidad de emisión de tokens, passwords completos verificados |
| **Componentes** | `app/dependencies.py:59-66` (create_access_token), `app/dependencies.py:~120` (password truncation) |
| **Estrategia de mitigación** | 1. Agregar `iat = datetime.now(timezone.utc)` al payload del JWT. 2. Eliminar `request.password[:72]` en auth_router.py y dependencies.py — bcrypt maneja passwords de cualquier longitud |
| **Estrategia de validación** | 1. Test: token nuevo contiene `iat`. 2. Test: password de 100 chars se verifica correctamente (antes se truncaba a 72). 3. Test: password de 72 chars exactos se verifica correctamente |
| **Estrategia de rollback** | Revertir las líneas individuales — cambios mínimos y atómicos |
| **Riesgos de implementación** | Mínimo. Si el hash en DB fue generado con password truncado a 72 chars, la verificación del password completo fallará. Solución: migrar hashes (ver H2) que usa el password completo |

---

## Matriz de Dependencias

```
C1 (sandbox) ──► H5 (timeout) ──► C2 (redes)          [Fase 1: independientes]
                                        │
H1 (redis auth) ──► H3 (except pass)    │              [Fase 1: dependencia leve]
                                        ▼
H6 (verify_admin) ◄────────────────── C2 requiere redes  [Fase 2]
H2 (bcrypt) ──► L2 (no truncar)                          [Fase 2+3: mismo componente]
                                        │
C3 (RS256) ──► M1 (jti/iat) ──► L1 (iat)               [Fase 3: dependencia fuerte]
                                        │
M2/M3 (headers) ◄── independiente                       [Fase 3]
```

**Regla:** No ejecutar ítem B hasta que ítem A del que depende esté verificado en staging.

---

## Estrategia de Preservación de Funcionalidad

### Principios

1. **Nunca cambiar contratos de API** — todas las mitigaciones son internas (cambios en lógica de backend, configuración de infraestructura). Ningún endpoint cambia su firma, response format, o comportamiento observable excepto cuando se mejora la seguridad (ej. fail-closed en blacklist)

2. **Feature flags para cambios riesgosos:**
   - `EXECUTE_CODE_USE_DOCKER` (default: false durante migración, true después de validación)
   - `JWT_USE_RS256` (default: false)
   - `REDIS_FAIL_CLOSED` (default: false)

3. **Compatibilidad hacia atrás obligatoria** en:
   - Migración JWT: doble validación (RS256 + HS256 fallback)
   - Migración bcrypt: verificar con bcrypt nuevo, fallback a passlib, re-hashear en login exitoso
   - Migración blacklist: si no hay `jti`, usar token completo (comportamiento legacy)

4. **Despliegue progresivo:**
   - Cada cambio en commit atómico
   - Pruebas unitarias + integración antes de merge
   - Staging con datos sintéticos antes de producción

### Estrategia de rollback por escenario

| Escenario | Acción | Tiempo |
|-----------|--------|--------|
| Docker sandbox no disponible | Fallback a 503 "servicio temporalmente no disponible" | Inmediato |
| Migración bcrypt rompe login | Activar `USE_LEGACY_HASH=true` feature flag | 5 min |
| Segmentación de red rompe comunicación | Revertir docker-compose.yml completo | 10 min |
| Redis requirepass mal configurado | Revertir settings.py + docker-compose redis | 5 min |
| CSP bloquea frontend | Usar `Content-Security-Policy-Report-Only` por 1 semana antes de enforce | 1 semana |
| RS256 rompe autenticación | Revertir a HS256, tokens activos con fallback | 5 min |

---

## Score Objetivo Post-Remediación

| Categoría OWASP | Score Inicial | Score Objetivo | Mejora |
|----------------|:-------------:|:--------------:|:------:|
| A1: Broken Access Control | 6 | 9 | +3 |
| A2: Cryptographic Failures | 4 | 8 | +4 |
| A3: Injection | 9 | 10 | +1 |
| A4: Insecure Design | 3 | 9 | +6 |
| A5: Security Misconfiguration | 3 | 8 | +5 |
| A6: Vulnerable Components | 5 | 8 | +3 |
| A7: Authentication Failures | 4 | 8 | +4 |
| A8: Integrity Failures | 6 | 8 | +2 |
| A9: Logging & Monitoring | 7 | 9 | +2 |
| A10: SSRF | 3 | 8 | +5 |
| **Score Global** | **50** | **85** | **+35** |

---

## Plan de Validación por Fase

### Fase 1 — Validación de contención
```
- C1: pytest tests/test_execute_code.py (nuevo)
- C2: docker-compose up + ping entre servicios
- H1: docker-compose logs redis + test auth
- H4: npm run build + test SSR pages
```

### Fase 2 — Validación de fortalecimiento
```
- H6: pytest tests/test_auth.py (nuevo test_admin_db_check)
- H2: pytest tests/test_auth.py (nuevo test_bcrypt_migration)
- H3: pytest tests/test_auth.py (nuevo test_redis_fail_closed)
- H5: pytest tests/test_execute_code.py (nuevo test_timeout)
```

### Fase 3 — Validación de madurez
```
- C3: pytest tests/test_auth.py (nuevo test_rs256_tokens)
- M1: pytest tests/test_auth.py (nuevo test_jti_blacklist)
- M2/M3: curl -I para verificar headers HTTP
- L1/L2: pytest tests/test_auth.py (nuevos tests unitarios)
```

---

## Archivos a Modificar por Ítem

| Ítem | Archivos |
|------|----------|
| C1 | `exercises_router.py`, `sandbox_service.py`, `code_executor.py` |
| C2 | `docker-compose.yml` |
| H1 | `docker-compose.yml`, `settings.py`, `dependencies.py`, `rate_limiter.py` |
| H4 | `docker-compose.yml` |
| H6 | `dependencies.py` |
| H2 | `dependencies.py`, `auth_router.py`, `requirements.txt` |
| H3 | `dependencies.py`, `code_executor.py` |
| H5 | `exercises_router.py`, `code_executor.py` |
| C3 | `settings.py`, `dependencies.py`, frontend JWT lib |
| M1 | `dependencies.py` |
| M2/M3 | `main.py` |
| L1/L2 | `dependencies.py`, `auth_router.py` |
| Tests | `tests/` (test_execute_code.py, test_auth.py extendido) |

---

*Documento generado como parte del plan de mejora FURPS+ — Fase de Remediación OWASP.*
*Próximo paso: Ejecutar Fase 1 ítems 1-4 en orden.*
