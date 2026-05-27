"""
Database initialization module - Creates database, tables, and seeds data if they don't exist
"""
import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from config.settings import settings

def find_script(name: str):
    """Find a SQL script by name"""
    base = Path(__file__).parent.parent / "scripts"
    paths = [
        base / name,
        Path("backend/scripts") / name,
        Path("scripts") / name,
    ]
    for p in paths:
        if p.exists():
            return p
    return None

def database_exists(db_name: str) -> bool:
    """Check if database exists"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone() is not None
        cursor.close(); conn.close()
        return exists
    except Exception as e:
        print(f"Error checking if database exists: {e}")
        return False

def create_database(db_name: str):
    """Create database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        try:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        except psycopg2.Error as e:
            if "already exists" not in str(e).lower():
                raise
        cursor.close(); conn.close()
        print(f"[OK] Database '{db_name}' is ready")
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def table_exists(cursor, table_name: str) -> bool:
    """Check if a table exists"""
    try:
        cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = %s AND table_schema = 'public'",
            (table_name,)
        )
        return cursor.fetchone() is not None
    except:
        return False

def execute_sql_file(file_path: Path) -> bool:
    """Execute SQL file against the database"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database=settings.postgres_db
        )
        cursor = conn.cursor()
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        statements = sql_script.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except psycopg2.Error as e:
                    msg = str(e).lower()
                    if "conflict" in msg or "already exists" in msg:
                        pass
                    elif "syntax" in msg:
                        pass
                    else:
                        print(f"  [WARN] {e}")
        conn.commit()
        cursor.close(); conn.close()
        print(f"[OK] Executed: {file_path.name}")
        return True
    except Exception as e:
        print(f"Error executing SQL file {file_path}: {e}")
        return False

def data_exists(table_name: str) -> bool:
    """Check if data exists in a table"""
    try:
        conn = psycopg2.connect(
            host=settings.postgres_host, port=settings.postgres_port,
            user=settings.postgres_user, password=settings.postgres_password,
            database=settings.postgres_db
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.close(); conn.close()
        return count > 0
    except:
        return False

def initialize_database():
    """
    Initialize database:
    1. Create database
    2. Create tables (001-create-tables.sql)
    3. Create stored procedures (002-create-procedures.sql)
    4. Seed data (003-seed-data.sql)
    5. Update module educational content
    """
    print("\n" + "="*50)
    print("Database Initialization Starting...")
    print("="*50)

    # Step 1: Create database
    print("\n[1/4] Checking/Creating Database...")
    if not database_exists(settings.postgres_db):
        print(f"  Creating database '{settings.postgres_db}'...")
        if not create_database(settings.postgres_db):
            print("  [ERROR] Failed to create database")
            return False
    else:
        print(f"  [OK] Database '{settings.postgres_db}' already exists")

    # Step 2: Create tables
    print("\n[2/4] Creating Tables...")
    script_001 = find_script("001-create-tables.sql")
    if script_001:
        if execute_sql_file(script_001):
            print("  [OK] Tables created successfully")
        else:
            print("  [ERROR] Failed to create tables")
            return False
    else:
        print("  [WARN] 001-create-tables.sql not found")

    # Step 3: Create stored procedures
    print("\n[3/4] Creating Stored Procedures...")
    script_002 = find_script("002-create-procedures.sql")
    if script_002:
        try:
            conn = psycopg2.connect(
                host=settings.postgres_host, port=settings.postgres_port,
                user=settings.postgres_user, password=settings.postgres_password,
                database=settings.postgres_db
            )
            cursor = conn.cursor()
            with open(script_002, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            cursor.execute(sql_content)
            conn.commit()
            cursor.close()
            conn.close()
            print("  [OK] Stored procedures created")
        except Exception as e:
            print(f"  [WARN] Stored procedures error (may already exist): {e}")
    else:
        print("  [WARN] 002-create-procedures.sql not found")

    # Step 4: Seed data
    print("\n[4/4] Seeding Data...")
    script_003 = find_script("003-seed-data.sql")
    if script_003:
        try:
            if data_exists("users"):
                print("  [OK] Data already exists (seed skipped)")
            else:
                if execute_sql_file(script_003):
                    print("  [OK] Data seeded successfully")
                else:
                    print("  [WARN] Seed had issues")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  [WARN] 003-seed-data.sql not found")

    print("\n[5/5] Updating Module Content...")
    try:
        _update_module_content_if_needed()
    except Exception as e:
        print(f"  [WARN] Content update: {e}")

    print("\n" + "="*50)
    print("[OK] Database initialization complete!")
    print("="*50 + "\n")
    return True


def _update_module_content_if_needed():
    """Update module theory_content with real educational content if empty"""
    import psycopg2
    conn = psycopg2.connect(
        host=settings.postgres_host, port=settings.postgres_port,
        user=settings.postgres_user, password=settings.postgres_password,
        database=settings.postgres_db
    )
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, theory_content FROM modules WHERE is_global = TRUE AND (theory_content IS NULL OR theory_content = '')")
    modules = cursor.fetchall()

    content_map = {
        "Introducción a Python": """# Introducción a Python

Python es un lenguaje de programación **interpretado**, **multiparadigma** y de **alto nivel**. Fue creado por Guido van Rossum y lanzado en 1991. Su filosofía se centra en la legibilidad del código y la productividad del desarrollador.

## Características principales

- **Sintaxis clara y legible**: Python usa indentación para definir bloques de código.
- **Tipado dinámico**: No necesitas declarar el tipo de las variables.
- **Multiparadigma**: Soporta programación orientada a objetos, funcional y estructurada.
- **Extensa biblioteca estándar**: Incluye módulos para casi cualquier tarea.

## Tu primer programa

```python
print("¡Hola, Mundo!")
```

Para ejecutarlo, guarda el código en un archivo `.py` y ejecuta `python archivo.py` en tu terminal.

## ¿Por qué Python para robótica y programación?

1. **Fácil de aprender**: Ideal para principiantes.
2. **Grandes comunidades**: Muchos recursos y bibliotecas.
3. **Robótica**: Bibliotecas como `gpiozero`, `RobotFramework` y `ROS`.
4. **IA y Datos**: `scikit-learn`, `tensorflow`, `pandas` están escritos para Python.""",

        "Variables y Tipos de Datos": """# Variables y Tipos de Datos

## Variables

Una variable es un **nombre simbólico** que referencia un valor almacenado en memoria. En Python, las variables se crean en el momento en que se les asigna un valor.

```python
nombre = "Ana"       # String
edad = 25            # Integer
altura = 1.68        # Float
es_estudiante = True # Boolean
```

## Tipos de datos fundamentales

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `int` | Números enteros | `42`, `-3`, `0` |
| `float` | Números decimales | `3.14`, `-0.5` |
| `str` | Cadenas de texto | `"Hola"`, `'Python'` |
| `bool` | Booleanos | `True`, `False` |
| `NoneType` | Ausencia de valor | `None` |

## Conversión entre tipos

```python
numero = "42"
numero_entero = int(numero)     # "42" → 42
texto = str(3.14)               # 3.14 → "3.14"
```

## Reglas para nombres de variables

- Deben empezar con letra o guión bajo (`_`).
- No pueden empezar con número.
- Sensibles a mayúsculas/minúsculas: `edad` ≠ `Edad`.
- Usa `snake_case` por convención: `mi_variable`.""",

        "Estructuras de Control": """# Estructuras de Control

Las estructuras de control permiten **tomar decisiones** en tu código según condiciones específicas.

## if / elif / else

```python
edad = 18
if edad >= 18:
    print("Eres mayor de edad")
elif edad >= 13:
    print("Eres adolescente")
else:
    print("Eres menor de edad")
```

## Operadores de comparación

| Operador | Significado |
|----------|-------------|
| `==` | Igual a |
| `!=` | Diferente de |
| `<` | Menor que |
| `>` | Mayor que |
| `<=` | Menor o igual |
| `>=` | Mayor o igual |

## Operadores lógicos

```python
edad = 20
tiene_permiso = True

if edad >= 18 and tiene_permiso:
    print("Puedes ingresar")

if not tiene_permiso:
    print("No tienes permiso")
```

## Expresión ternaria

```python
mensaje = "Mayor" if edad >= 18 else "Menor"
```""",

        "Bucles y Repeticiones": """# Bucles y Repeticiones

Los bucles permiten **ejecutar código repetidamente** hasta que se cumpla una condición.

## Bucle `for`

Itera sobre una secuencia (lista, tupla, string, range).

```python
# Iterar sobre un rango
for i in range(5):
    print(f"Vuelta {i + 1}")

# Iterar sobre una lista
colores = ["rojo", "verde", "azul"]
for color in colores:
    print(f"Color: {color}")

# Iterar sobre un string
for letra in "Python":
    print(letra)
```

## Bucle `while`

Se ejecuta mientras una condición sea verdadera.

```python
contador = 0
while contador < 5:
    print(contador)
    contador += 1
```

## Control de bucles

- `break`: Sale del bucle inmediatamente.
- `continue`: Salta a la siguiente iteración.

```python
for i in range(10):
    if i == 3:
        continue  # Salta el 3
    if i == 7:
        break     # Termina en 7
    print(i)      # 0, 1, 2, 4, 5, 6
```""",

        "Funciones": '''# Funciones

Las funciones son **bloques de código reutilizables** que realizan una tarea específica.

## Definir una función

```python
def saludar(nombre):
    """Esta función saluda al usuario"""
    return f"¡Hola, {nombre}!"

# Llamar a la función
mensaje = saludar("Ana")
print(mensaje)  # ¡Hola, Ana!
```

## Parámetros y argumentos

```python
def sumar(a, b):
    return a + b

# Argumentos posicionales
print(sumar(3, 4))  # 7

# Argumentos con nombre
print(sumar(b=5, a=2))  # 7
```

## Parámetros por defecto

```python
def saludar(nombre="Invitado"):
    return f"Hola, {nombre}"

print(saludar())          # Hola, Invitado
print(saludar("Carlos"))  # Hola, Carlos
```

## Ámbito de variables

- **Local**: Dentro de la función.
- **Global**: Fuera de cualquier función.

```python
x = 10  # Variable global

def funcion():
    x = 5  # Variable local
    print(f"Dentro: {x}")

funcion()    # Dentro: 5
print(x)     # 10
```''',

        "Listas y Tuplas": """# Listas y Tuplas

## Listas

Las listas son **colecciones ordenadas y mutables** de elementos.

```python
frutas = ["manzana", "pera", "uva"]
numeros = [1, 2, 3, 4, 5]
mixta = [1, "hola", 3.14, True]
```

### Operaciones con listas

```python
frutas = ["manzana", "pera"]

frutas.append("uva")         # Agregar al final
frutas.insert(1, "naranja")  # Insertar en posición
frutas.remove("pera")        # Eliminar elemento
frutas.pop()                 # Eliminar último
frutas.sort()                # Ordenar
frutas.reverse()             # Invertir
print(len(frutas))           # Longitud
```

### Indexación y slicing

```python
lista = [10, 20, 30, 40, 50]
print(lista[0])     # 10 (primero)
print(lista[-1])    # 50 (último)
print(lista[1:3])   # [20, 30] (slicing)
print(lista[::-1])  # [50, 40, 30, 20, 10] (invertido)
```

## Tuplas

Las tuplas son **colecciones ordenadas pero inmutables**.

```python
coordenadas = (10, 20)
dias_semana = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")

# Las tuplas no se pueden modificar
# coordenadas[0] = 5  # ERROR
```""",

        "Diccionarios y Sets": """# Diccionarios y Sets

## Diccionarios

Los diccionarios almacenan datos en pares **clave-valor**.

```python
persona = {
    "nombre": "Luis",
    "edad": 25,
    "ciudad": "Madrid"
}

print(persona["nombre"])  # Luis
print(persona.get("edad"))  # 25
```

### Operaciones con diccionarios

```python
persona["email"] = "luis@email.com"  # Agregar
persona["edad"] = 26                 # Modificar
del persona["ciudad"]                # Eliminar

for clave, valor in persona.items():
    print(f"{clave}: {valor}")

print(persona.keys())    # dict_keys(['nombre', 'edad', 'email'])
print(persona.values())  # dict_values(['Luis', 26, 'luis@email.com'])
```

## Sets (Conjuntos)

Los sets son **colecciones no ordenadas sin elementos duplicados**.

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)  # Unión: {1, 2, 3, 4, 5, 6}
print(a & b)  # Intersección: {3, 4}
print(a - b)  # Diferencia: {1, 2}
print(a ^ b)  # Diferencia simétrica: {1, 2, 5, 6}
```""",

        "Manejo de Archivos": """# Manejo de Archivos

Python permite **leer y escribir archivos** de manera sencilla.

## Abrir archivos

```python
# Modos de apertura:
# 'r' - lectura (por defecto)
# 'w' - escritura (sobrescribe)
# 'a' - agregar (append)
# 'r+' - lectura y escritura

with open("archivo.txt", "w", encoding="utf-8") as f:
    f.write("Hola, archivo!")
```

## Leer archivos

```python
with open("archivo.txt", "r", encoding="utf-8") as f:
    contenido = f.read()        # Todo el contenido
    linea = f.readline()        # Una línea
    lineas = f.readlines()      # Lista de líneas
```

## Leer CSV

```python
import csv
with open("datos.csv", "r") as f:
    lector = csv.reader(f)
    for fila in lector:
        print(fila)
```

## Buenas prácticas

- Usar `with` (context manager) para cerrar archivos automáticamente.
- Especificar `encoding="utf-8"` para caracteres especiales.
- Manejar excepciones con `try/except`.""",

        "Módulos y Paquetes": """# Módulos y Paquetes

Los módulos permiten **organizar código** en archivos separados y reutilizables.

## Importar módulos

```python
# Importar módulo completo
import math
print(math.sqrt(16))  # 4.0

# Importar funciones específicas
from math import pi, sin
print(pi)  # 3.14159...

# Importar con alias
import math as m
print(m.floor(3.7))  # 3
```

## Módulo vs Paquete

- **Módulo**: Archivo `.py` individual.
- **Paquete**: Carpeta con `__init__.py` que contiene varios módulos.

## Instalar paquetes con pip

```bash
pip install numpy
pip install requests
pip list                    # Listar instalados
pip freeze > requirements.txt  # Exportar dependencias
```

## Módulos útiles de la biblioteca estándar

| Módulo | Uso |
|--------|-----|
| `math` | Funciones matemáticas |
| `random` | Números aleatorios |
| `datetime` | Fechas y horas |
| `json` | Trabajar con JSON |
| `os` | Interacción con el SO |
| `csv` | Leer/escribir CSV |""",

        "Proyecto Final: Robot Autónomo": """# Proyecto Final: Robot Autónomo

En este proyecto final aplicarás **todos los conceptos aprendidos** para programar un robot virtual que navega de forma autónoma.

## Diseño del Robot

Creamos una clase `Robot` con atributos y métodos:

```python
class Robot:
    def __init__(self, nombre):
        self.nombre = nombre
        self.x = 0
        self.y = 0
        self.energia = 100

    def mover(self, dx, dy):
        if self.energia >= 10:
            self.x += dx
            self.y += dy
            self.energia -= 10
            return f"{self.nombre} se movió a ({self.x}, {self.y})"
        return "Sin energía"
```

## Lógica de navegación

El robot usa **sensores virtuales** para detectar obstáculos:

```python
class RobotAutonomo(Robot):
    def __init__(self, nombre):
        super().__init__(nombre)
        self.obstaculos = [(3, 0), (5, 5)]

    def detectar_obstaculo(self, dx, dy):
        nueva_pos = (self.x + dx, self.y + dy)
        return nueva_pos in self.obstaculos

    def navegar_a(self, destino_x, destino_y):
        while (self.x, self.y) != (destino_x, destino_y):
            dx = 1 if destino_x > self.x else -1
            dy = 1 if destino_y > self.y else -1

            if not self.detectar_obstaculo(dx, 0):
                self.mover(dx, 0)
            elif not self.detectar_obstaculo(0, dy):
                self.mover(0, dy)
            else:
                return "¡Atascado!"
        return f"¡Llegué a ({destino_x}, {destino_y})!"
```""",
    }

    updated = 0
    for mod_id, title, current_content in modules:
        new_content = content_map.get(title)
        if new_content:
            cursor.execute(
                "UPDATE modules SET theory_content = %s, lesson_count = %s WHERE id = %s",
                (new_content, str(new_content).count("## ") + 1, mod_id)
            )
            updated += 1

    cursor.execute("""
        UPDATE lessons SET theory_content = sub.full_content
        FROM (
            SELECT l.id,
                CASE
                    WHEN l.title = 'Qué es Python' THEN '# ¿Qué es Python?\n\nPython es un lenguaje de programación creado por Guido van Rossum en 1991. Es conocido por su sintaxis clara y legible.\n\n## ¿Por qué Python?\n\n- **Fácil de aprender**: Ideal para principiantes en programación.\n- **Versátil**: Se usa en web, datos, IA, robótica y más.\n- **Comunidad grande**: Millones de desarrolladores contribuyen.\n\n## Hola Mundo\n\n```python\nprint("Hola, Mundo!")\n```\n\nEl clásico programa de inicio. `print()` es una función que muestra texto en pantalla.'
                    WHEN l.title = 'Instalación y Setup' THEN '# Instalación y Configuración\n\n## Instalar Python\n\n1. Ve a [python.org](https://python.org)\n2. Descarga la última versión (3.x)\n3. Ejecuta el instalador\n4. **Importante**: Marca "Add Python to PATH"\n\n## Verificar instalación\n\nAbre tu terminal y escribe:\n\n```bash\npython --version\n```\n\nDeberías ver algo como: `Python 3.11.0`\n\n## Editor de código\n\nRecomendamos **Visual Studio Code** con la extensión de Python.'
                    WHEN l.title = 'Tu Primer Programa' THEN '# Tu Primer Programa\n\n## Ejercicio 1: ¡Hola, Mundo!\n\nEscribe tu primer programa en Python:\n\n```python\nprint("¡Hola, Mundo!")\n```\n\n### ¿Qué hace?\n\n- `print()` es una función que imprime texto en pantalla.\n- El texto entre comillas se llama **string**.\n\n### Desafío\n\nModifica el programa para que imprima tu nombre.\n\n```python\nprint("Hola, me llamo [tu nombre]")\n```\n\n¡Felicidades! Acabas de escribir tu primer programa en Python.'
                END as full_content
            FROM lessons l
            JOIN modules m ON m.id = l.module_id
            WHERE m.is_global = TRUE
        ) sub
        WHERE lessons.id = sub.id AND sub.full_content IS NOT NULL
    """)
    conn.commit()
    cursor.close()
    conn.close()
    if updated > 0:
        print(f"  [OK] Updated {updated} modules with real educational content")
    else:
        print("  [OK] Module content already up to date")
