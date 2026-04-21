# Nombre del backend
$root = "backend"

# Función para crear archivos
function New-File($path) {
    New-Item -ItemType File -Path $path -Force | Out-Null
}

# =========================
# CREAR ESTRUCTURA
# =========================

$folders = @(
    # DOMAIN
    "$root/domain/entities",
    "$root/domain/valueObjects",
    "$root/domain/ports",

    # APPLICATION
    "$root/application/useCases",
    "$root/application/services",

    # INFRASTRUCTURE
    "$root/infrastructure/adapters/input",
    "$root/infrastructure/adapters/output/postgres",
    "$root/infrastructure/adapters/output/mongo",

    # ROOT FILES
    "$root/config",
    "$root/tests"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}

# =========================
# ARCHIVOS BASE PYTHON
# =========================

# Crear __init__.py en todas las carpetas
Get-ChildItem -Recurse -Directory $root | ForEach-Object {
    New-File "$($_.FullName)/__init__.py"
}

# =========================
# DOMAIN (EJEMPLOS)
# =========================
New-File "$root/domain/entities/user.py"
New-File "$root/domain/entities/module.py"
New-File "$root/domain/entities/exercise.py"

New-File "$root/domain/valueObjects/progress.py"

New-File "$root/domain/ports/user_repository.py"
New-File "$root/domain/ports/module_repository.py"
New-File "$root/domain/ports/ai_service.py"

# =========================
# APPLICATION
# =========================
New-File "$root/application/useCases/register_user.py"
New-File "$root/application/useCases/get_recommendations.py"
New-File "$root/application/useCases/enroll_student.py"

New-File "$root/application/services/ai_recommender.py"

# =========================
# INFRASTRUCTURE - INPUT (FastAPI)
# =========================
New-File "$root/infrastructure/adapters/input/main.py"
New-File "$root/infrastructure/adapters/input/user_controller.py"
New-File "$root/infrastructure/adapters/input/module_controller.py"

# =========================
# INFRASTRUCTURE - OUTPUT
# =========================

# PostgreSQL
New-File "$root/infrastructure/adapters/output/postgres/db.py"
New-File "$root/infrastructure/adapters/output/postgres/user_repository_impl.py"

# MongoDB
New-File "$root/infrastructure/adapters/output/mongo/db.py"
New-File "$root/infrastructure/adapters/output/mongo/event_repository_impl.py"

# =========================
# CONFIG
# =========================
New-File "$root/config/settings.py"

# =========================
# TESTS
# =========================
New-File "$root/tests/test_user.py"

Write-Host "✅ Backend hexagonal creado correctamente."