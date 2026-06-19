# Auditoría de Software — Dependencias

**Proyecto:** RoboLearn  
**Fecha:** 2026-06-19  
**Auditor:** Asistente de IA (análisis automatizado + búsqueda de vulnerabilidades)  
**Propósito:** Inventario completo, clasificación y análisis de seguridad de todas las dependencias del proyecto.

---

## Archivos de Dependencias Encontrados

| Archivo | Ubicación | Tipo | Paquetes |
|---------|-----------|------|----------|
| `requirements.txt` | `backend/` | Python (pip) | 19 producción |
| `requirements.txt` | `ml_pipeline/` | Python (pip) | 7 producción |
| `package.json` | `frontend/` | Node.js (npm) | 30 producción + 9 desarrollo |
| `package-lock.json` | `frontend/` | Node.js (npm) | Lock file (versiones congeladas) |

**No encontrados:** `pyproject.toml`, `Pipfile`, `Cargo.toml`, `go.mod`, `Gemfile`, `composer.json`, `pom.xml`, `build.gradle`.

---

## 1. Inventario Completo

### Backend (`backend/requirements.txt`) — Python 3.11

| # | Paquete | Versión | Propósito | Licencia |
|---|---------|---------|-----------|----------|
| 1 | fastapi | 0.109.0 | Framework REST API | MIT |
| 2 | uvicorn[standard] | 0.27.0 | Servidor ASGI | BSD-3 |
| 3 | python-jose[cryptography] | 3.3.0 | JWT | MIT |
| 4 | bcrypt | 3.2.0 | Hashing de contraseñas | Apache-2.0 |
| 5 | python-multipart | 0.0.6 | Parseo de formularios | Apache-2.0 |
| 6 | pymongo | 4.6.0 | Driver MongoDB | Apache-2.0 |
| 7 | psycopg2-binary | 2.9.9 | Driver PostgreSQL | LGPL-3 |
| 8 | python-dotenv | 1.0.0 | Variables de entorno | BSD-3 |
| 9 | pydantic | 2.5.0 | Validación de datos | MIT |
| 10 | pydantic-settings | 2.1.0 | Configuración por entorno | MIT |
| 11 | scikit-learn | 1.8.0 | ML — modelos | BSD-3 |
| 12 | joblib | 1.5.3 | Serialización de modelos | BSD-3 |
| 13 | numpy | 1.26.3 | Cómputo numérico | BSD-3 |
| 14 | pandas | 2.1.4 | DataFrames | BSD-3 |
| 15 | scipy | 1.11.4 | Cómputo científico | BSD-3 |
| 16 | apscheduler | 3.10.4 | Tareas programadas | MIT |
| 17 | docker | 7.1.0 | SDK Docker Python | Apache-2.0 |
| 18 | redis[hiredis] | 5.1.0 | Cliente Redis + C | MIT |
| 19 | httpx | 0.27.0 | Cliente HTTP async | BSD-3 |

### ML Pipeline (`ml_pipeline/requirements.txt`) — Python 3

| # | Paquete | Versión (mín) | Propósito | Licencia |
|---|---------|---------------|-----------|----------|
| 1 | pandas | >=1.5.0 | DataFrames | BSD-3 |
| 2 | numpy | >=1.24.0 | Cómputo numérico | BSD-3 |
| 3 | scikit-learn | >=1.3.0 | Modelos ML | BSD-3 |
| 4 | joblib | >=1.2.0 | Serialización | BSD-3 |
| 5 | matplotlib | >=3.7.0 | Gráficos estáticos | BSD-3 |
| 6 | seaborn | >=0.12.0 | Gráficos estadísticos | BSD-3 |
| 7 | pyarrow | >=12.0.0 | Archivos Parquet | Apache-2.0 |

### Frontend (`frontend/package.json`) — Node.js 20 / Next.js 16

#### Producción (30 dependencias)

| # | Paquete | Versión (lock) | Propósito |
|---|---------|----------------|-----------|
| 1 | @codemirror/lang-markdown | ^6.5.0 | Lenguaje Markdown en editor |
| 2 | @codemirror/lang-python | ^6.2.1 | Lenguaje Python en editor |
| 3 | @codemirror/language-data | ^6.5.2 | Datos de lenguajes CodeMirror |
| 4 | @codemirror/theme-one-dark | ^6.1.3 | Tema oscuro CodeMirror |
| 5 | @hookform/resolvers | ^3.9.1 | Validación para react-hook-form |
| 6 | @radix-ui/react-alert-dialog | 1.1.15 | Diálogo de alerta accesible |
| 7 | @radix-ui/react-avatar | 1.1.11 | Avatar |
| 8 | @radix-ui/react-checkbox | 1.3.3 | Checkbox |
| 9 | @radix-ui/react-dialog | 1.1.15 | Diálogo modal |
| 10 | @radix-ui/react-dropdown-menu | 2.1.16 | Menú desplegable |
| 11 | @radix-ui/react-label | 2.1.8 | Label accesible |
| 12 | @radix-ui/react-popover | 1.1.15 | Popover |
| 13 | @radix-ui/react-progress | 1.1.8 | Barra de progreso |
| 14 | @radix-ui/react-scroll-area | 1.2.10 | Área de scroll |
| 15 | @radix-ui/react-select | 2.2.6 | Select accesible |
| 16 | @radix-ui/react-separator | 1.1.8 | Separador |
| 17 | @radix-ui/react-slot | 1.2.4 | Slot de composición |
| 18 | @radix-ui/react-switch | 2.2.6 | Switch |
| 19 | @radix-ui/react-tabs | 1.1.13 | Tabs |
| 20 | @radix-ui/react-toggle | 1.1.10 | Toggle |
| 21 | @radix-ui/react-tooltip | 1.2.8 | Tooltip |
| 22 | @uiw/react-codemirror | ^4.25.9 | Editor de código React |
| 23 | @vercel/analytics | 1.6.1 | Analytics Vercel |
| 24 | class-variance-authority | ^0.7.1 | Variantes CSS |
| 25 | clsx | ^2.1.1 | Clases condicionales |
| 26 | date-fns | 4.1.0 | Manipulación de fechas |
| 27 | jose | ^6.2.2 | JWT (frontend) |
| 28 | lucide-react | ^0.564.0 | Iconos SVG |
| 29 | next | ^16.2.4 | Framework React |
| 30 | next-themes | ^0.4.6 | Modo oscuro |
| 31 | react | 19.2.4 | UI library |
| 32 | react-day-picker | 9.13.2 | Selector de fechas |
| 33 | react-dom | 19.2.4 | Renderizado React |
| 34 | react-hook-form | ^7.54.1 | Formularios |
| 35 | react-markdown | ^10.1.0 | Renderizado Markdown |
| 36 | react-syntax-highlighter | ^15.6.1 | Resaltado de sintaxis |
| 37 | recharts | 2.15.0 | Gráficos |
| 38 | rehype-raw | ^7.0.0 | HTML en Markdown |
| 39 | remark-gfm | ^4.0.1 | GitHub Flavored Markdown |
| 40 | sonner | ^1.7.1 | Notificaciones toast |
| 41 | tailwind-merge | ^3.3.1 | Merge de clases Tailwind |
| 42 | zod | ^3.24.1 | Validación de esquemas |

#### Desarrollo (9 dependencias)

| # | Paquete | Versión (lock) | Propósito |
|---|---------|----------------|-----------|
| 1 | @tailwindcss/postcss | ^4.2.0 | Plugin PostCSS de Tailwind |
| 2 | @types/node | ^22 | Tipos Node.js |
| 3 | @types/react | 19.2.14 | Tipos React |
| 4 | @types/react-dom | 19.2.3 | Tipos React DOM |
| 5 | @types/react-syntax-highlighter | ^15.5.13 | Tipos syntax highlighter |
| 6 | postcss | ^8.5 | Procesador CSS |
| 7 | tailwindcss | ^4.2.0 | Framework CSS |
| 8 | tw-animate-css | 1.3.3 | Animaciones CSS |
| 9 | typescript | 5.7.3 | Compilador TS |

---

## 2. Dependencias de Producción

### Backend (19)
fastapi, uvicorn, python-jose, bcrypt, python-multipart, pymongo, psycopg2-binary, python-dotenv, pydantic, pydantic-settings, scikit-learn, joblib, numpy, pandas, scipy, apscheduler, docker, redis, httpx

### ML Pipeline (7)
pandas, numpy, scikit-learn, joblib, matplotlib, seaborn, pyarrow

### Frontend (42)
Ver listado completo en sección anterior (producción + todas las Radix UI, CodeMirror, recharts, etc.)

---

## 3. Dependencias de Desarrollo

### Frontend (9)
@tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @types/react-syntax-highlighter, postcss, tailwindcss, tw-animate-css, typescript

### Observación
Backend y ML Pipeline no tienen separación dev/prod en `requirements.txt`. Dependencias como `pytest`, `pytest-cov`, `httpx`, `flake8`, `mypy`, `isort` se instalan solo en CI (archivo `.github/workflows/ci.yml`) pero no están declaradas en ningún archivo de dependencias persistente.

---

## 4. Dependencias Críticas

Son aquellas cuyo fallo compromete toda la aplicación:

| Dependencia | Versión | ¿Por qué es crítica? |
|-------------|---------|----------------------|
| **fastapi** | 0.109.0 | Framework base del backend — sin él no hay API |
| **uvicorn** | 0.27.0 | Servidor HTTP — punto de entrada del backend |
| **next** | 16.2.4 | Framework base del frontend |
| **react / react-dom** | 19.2.4 | UI runtime — toda la interfaz depende de ellos |
| **pydantic** | 2.5.0 | Validación de todas las entradas/salidas del backend |
| **python-jose** | 3.3.0 | Autenticación JWT — vulnerabilidad CRÍTICA detectada |
| **bcrypt** | 3.2.0 | Hashing de contraseñas |
| **psycopg2-binary** | 2.9.9 | Conexión a PostgreSQL — sin él no hay datos |
| **pymongo** | 4.6.0 | Conexión a MongoDB — eventos y analítica |
| **scikit-learn** | 1.8.0 | Todos los modelos ML predictivos |
| **jose** | 6.2.2 | Verificación JWT del lado frontend (middleware) |

---

## 5. Dependencias Obsoletas

| Dependencia | Versión actual | Última versión (2026) | Diferencia | Riesgo |
|-------------|---------------|----------------------|------------|--------|
| **python-jose** | 3.3.0 | 3.4.0+ | Una versión atrás | **CRÍTICO** — 2 CVEs sin parche |
| **pydantic** | 2.5.0 | 2.13.4 | ~8 versiones atrás | Medio — features perdidas |
| **pydantic-settings** | 2.1.0 | 2.8.x+ | ~7 versiones atrás | Bajo |
| **apscheduler** | 3.10.4 | 3.11.x+ | ~1 versión atrás | Bajo |
| **scikit-learn** | 1.8.0 | 1.9.x+ | ~1 versión atrás | Bajo |
| **pandas** | 2.1.4 | 2.2.x+ | ~1 versión atrás | Bajo |
| **numpy** | 1.26.3 | 2.x+ | Breaking change | Medio — requiere migración |
| **python-multipart** | 0.0.6 | 0.0.9+ | ~3 versiones atrás | Bajo |
| **bcrypt** | 3.2.0 | 5.0.0+ | 2 major versions atrás | **Alto** — mejoras de seguridad |
| **docker (SDK)** | 7.1.0 | 7.2.x+ | ~1 versión atrás | Bajo |

---

## 6. Vulnerabilidades Potenciales

### 🔴 CRÍTICAS

#### CVE-2024-33663 — python-jose (CVSS 9.3)
- **Paquete:** `python-jose 3.3.0` (`backend/requirements.txt`)
- **Descripción:** Algorithm confusion — un atacante puede usar claves ECDSA de OpenSSH para falsificar JWT. Similar a CVE-2022-29217.
- **Impacto:** Confidencialidad ALTA, Integridad ALTA. Autenticación completamente evitable.
- **Solución:** Actualizar a `python-jose >= 3.4.0`
- **Evidencia:** `python-jose[cryptography]==3.3.0` en backend/requirements.txt línea 3

#### CVE-2024-33664 — python-jose (CVSS 5.3)
- **Paquete:** `python-jose 3.3.0`
- **Descripción:** JWT Bomb — ataque de denegación de servicio mediante tokens JWE comprimidos.
- **Impacto:** Disponibilidad BAJA. Consumo de recursos.
- **Solución:** Actualizar a `python-jose >= 3.4.0`

### 🟡 ALTAS

#### CVE-2026-44581 — Next.js (CVSS por determinar, XSS almacenado)
- **Paquete:** `next ^16.2.4` (`frontend/package.json`)
- **Descripción:** Aplicaciones App Router que usan CSP nonces pueden ser vulnerables a XSS almacenado cuando se despliegan detrás de cachés compartidos. Nonces malformados derivados de headers pueden reflejarse en HTML.
- **Versiones afectadas:** >= 13.4.0, < 15.5.16 y < 16.2.5
- **Solución:** Actualizar a `next >= 16.2.5`
- **Nota:** 16.2.4 está por debajo de 16.2.5 — **afectado**

#### CVE-2026-23869 / CVE-2026-44578 — Next.js (DoS / SSRF)
- **Paquete:** `next ^16.2.4`
- **Descripción:** DoS via Server Components (CVE-2026-23869, CVSS 7.5, parcheado en 16.2.3) y SSRF via WebSocket (CVE-2026-44578, parcheado en 16.2.5+).
- **16.2.4 está parcheado** para CVE-2026-23869, pero **puede estar afectado** por CVE-2026-44578.
- **Solución:** Actualizar a `next >= 16.2.5`

### 🟢 MODERADAS / BAJAS

| CVE | Paquete | Descripción | Estado en el proyecto |
|-----|---------|-------------|----------------------|
| CVE-2024-3772 | pydantic < 2.4.0 | ReDoS en validación de email (CVSS 5.9) | **✅ PARCHADO** — 2.5.0 > 2.4.0 |
| CVE-2021-29510 | pydantic < 1.8.2 | Infinity loop con `float('inf')` | **✅ PARCHADO** — 2.5.0 |
| CVE-2020-7689 | bcrypt.js (Node) | Integer overflow | **❌ NO APLICA** — es Python, no Node.js |

### 📊 Resumen de Vulnerabilidades

| Gravedad | Cantidad | Dependencias afectadas |
|----------|----------|-----------------------|
| 🔴 CRÍTICA | 1 (con 2 CVEs) | `python-jose` 3.3.0 |
| 🟡 ALTA | 1-3 (según confirmación) | `next` 16.2.4 |
| 🟢 MEDIA | 2 (ya parchadas) | `pydantic` (histórico) |
| ⚪ INFORMATIVA | 1 (no aplica) | `bcrypt` (Node CVE, no Python) |

---

## 7. Dependencias Relacionadas con Seguridad

| Dependencia | Versión | Rol de seguridad | Vulnerabilidades conocidas |
|-------------|---------|------------------|---------------------------|
| **python-jose[cryptography]** | 3.3.0 | Autenticación JWT (emisión y verificación) | 🔴 CVE-2024-33663 (crítica), CVE-2024-33664 |
| **bcrypt** | 3.2.0 | Hashing de contraseñas | ✅ Ninguna conocida para Python |
| **jose** (frontend) | 6.2.2 | Verificación JWT en middleware Next.js | ✅ Sin CVEs reportados |
| **python-multipart** | 0.0.6 | Parseo seguro de formularios | ✅ Sin CVEs recientes |
| **httpx** | 0.27.0 | Cliente HTTP (llamadas a APIs externas) | ✅ Sin CVEs críticos activos |

### Observaciones de seguridad

1. **python-jose 3.3.0 es la vulnerabilidad más crítica del proyecto.** Permite falsificar tokens JWT, lo que compromete toda la autenticación. **Actualización urgente a 3.4.0+ recomendada.**
2. No se encontraron **dependencias con backdoors conocidos** o **typosquatting**.
3. El proyecto no usa `passlib` ni otras librerías de autenticación adicionales.
4. La comunicación JWT entre frontend y backend usa `jose` (frontend) y `python-jose` (backend) — dos implementaciones distintas, lo cual es una buena práctica de separación.

---

## 8. Dependencias Relacionadas con Persistencia

| Dependencia | Base de datos | Rol | Versión |
|-------------|--------------|-----|---------|
| **psycopg2-binary** | PostgreSQL | Driver de conexión | 2.9.9 |
| **pymongo** | MongoDB | Driver de conexión | 4.6.0 |
| **redis[hiredis]** | Redis | Cliente con extensión C | 5.1.0 |
| **pgvector** | PostgreSQL | Extension de vectores (RAG) | No es paquete pip — es extensión SQL |
| **pyarrow** | Archivos Parquet | Lectura/escritura de datasets | >=12.0.0 (ML pipeline) |
| **joblib** | Archivos .pkl | Serialización de modelos ML | 1.5.3 (backend), >=1.2.0 (ML) |

### Observaciones de persistencia

- No se usa **ORM** (SQLAlchemy, Django ORM, Prisma). Todas las consultas son SQL crudo con `psycopg2`. Esto da control total pero aumenta el riesgo de **SQL Injection** si no se usan correctamente las consultas parametrizadas.
- No se usa **ODM** para MongoDB — se usa `pymongo` directamente.
- El cacheo con `redis[hiredis]` usa hiredis para acelerar la comunicación en C.

---

## 9. Dependencias Relacionadas con APIs

| Dependencia | Rol | Versión |
|-------------|-----|---------|
| **fastapi** | Framework REST API | 0.109.0 |
| **uvicorn[standard]** | Servidor ASGI | 0.27.0 |
| **httpx** | Cliente HTTP async (llamadas a Ollama, Dialogflow, OpenAI) | 0.27.0 |
| **python-multipart** | Parseo de formularios multipart | 0.0.6 |
| **pydantic** | Schemas/validación de requests/responses | 2.5.0 |
| **pydantic-settings** | Configuración desde variables de entorno | 2.1.0 |

---

## Tabla Resumen General

| Categoría | Backend | ML Pipeline | Frontend |
|-----------|---------|-------------|----------|
| **Total dependencias** | 19 | 7 | 51 (42 prod + 9 dev) |
| **Lenguaje** | Python 3.11 | Python 3 | TypeScript 5.7 / Node 20 |
| **Framework principal** | FastAPI 0.109 | scikit-learn 1.8 | Next.js 16.2.4 / React 19.2 |
| **Base de datos** | psycopg2, pymongo, redis | pyarrow (Parquet) | — |
| **Seguridad** | python-jose, bcrypt | — | jose |
| **Formato versiones** | Fijo (`==`) | Flexible (`>=`) | Semver (`^`) + fijo |
| **Lock file** | ❌ No | ❌ No | ✅ package-lock.json |
| **🔴 Vulnerabilidades críticas** | 1 (python-jose) | 0 | 0-1 (next, por confirmar) |
| **🟡 Vulnerabilidades altas** | 0 | 0 | 1-2 (next) |

---

## Recomendaciones

### Urgentes
1. **Actualizar `python-jose`** de 3.3.0 a ≥ 3.4.0 — corrige CVE-2024-33663 (algoritmo confusión, CVSS 9.3) y CVE-2024-33664 (JWT bomb, CVSS 5.3).
2. **Actualizar `next`** de 16.2.4 a ≥ 16.2.5 — corrige CVE-2026-44581 (XSS almacenado) y CVE-2026-44578 (SSRF).

### A corto plazo
3. **Agregar un lock file** para `backend/` (`requirements.txt` con hash o `pip freeze > requirements.txt`).
4. **Separar dev/prod deps** en el backend — crear `requirements-dev.txt` con pytest, flake8, mypy.
5. **Evaluar migrar de `python-jose` a `PyJWT`** — `python-jose` no recibe mantenimiento activo.

### A medio plazo
6. **Actualizar numpy** a 2.x (con las adaptaciones necesarias) para mantenerse al día.
7. **Actualizar bcrypt** a 5.x para mejoras de rendimiento y seguridad.
8. **Evaluar ORM** como SQLAlchemy para reducir riesgo de SQL Injection.

---

*Fin del reporte de Auditoría de Dependencias.*
