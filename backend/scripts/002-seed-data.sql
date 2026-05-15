-- Robolearn Seed Data
-- Sample data for development and testing

-- ============================================
-- SEED DATA
-- ============================================

-- Users
INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES ('admin@robolearn.com', '$2b$12$bGM8zs/InGnD1y8CjoqEgOdxJFEhAjfib2/jZckpnA3p0mhd/fpiW', 'Admin User', 'admin', TRUE, 0, 0)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES ('teacher@robolearn.com', '$2b$12$JFpw/eFD6s9cDikL1TJsYeExzr.85GpQUS1rvEqnEvJVJ4w/ZMOsC', 'Professor García', 'teacher', TRUE, 500, 15)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES ('student1@robolearn.com', '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i', 'Juan Pérez', 'student', TRUE, 250, 5)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES ('student2@robolearn.com', '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i', 'María López', 'student', TRUE, 420, 8)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES ('student3@robolearn.com', '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i', 'Carlos Rodríguez', 'student', TRUE, 180, 3)
ON CONFLICT (email) DO NOTHING;

-- Global Modules (10 Python modules)
INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Introducción a Python', 'Conoce el lenguaje, escribe tu primer programa y entiende la sintaxis básica.', id, 'approved', 1, TRUE, TRUE, 'Principiante', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Variables y Tipos de Datos', 'Aprende a almacenar información en variables y a trabajar con números y texto.', id, 'approved', 2, TRUE, TRUE, 'Principiante', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Estructuras de Control', 'Toma decisiones en tu código con if, elif y else.', id, 'approved', 3, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Bucles y Repeticiones', 'Domina for y while para automatizar tareas repetitivas.', id, 'approved', 4, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Funciones', 'Crea bloques de código reutilizables y organiza mejor tus programas.', id, 'approved', 5, TRUE, TRUE, 'Avanzado', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Listas y Tuplas', 'Trabaja con colecciones de datos y entiende sus diferencias.', id, 'approved', 6, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Diccionarios y Sets', 'Almacena datos con clave-valor y conjuntos sin duplicados.', id, 'approved', 7, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Manejo de Archivos', 'Lee y escribe archivos de texto y CSV con Python.', id, 'approved', 8, TRUE, TRUE, 'Avanzado', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Módulos y Paquetes', 'Organiza tu código en módulos reutilizables y usa pip.', id, 'approved', 9, TRUE, TRUE, 'Avanzado', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT 'Proyecto Final: Robot Autónomo', 'Aplica todo lo aprendido para programar un robot virtual que navega solo.', id, 'approved', 10, TRUE, TRUE, 'Avanzado', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

-- Teacher module
INSERT INTO modules (title, description, teacher_id, status, "order", is_published)
SELECT 'Inteligencia Artificial Básica', 'Aprende los conceptos fundamentales de IA usando Python y librerías sencillas.', id, 'approved', 5, TRUE
FROM users WHERE email = 'teacher@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published)
SELECT 'Machine Learning', 'Introducción a algoritmos de clasificación y regresión.', id, 'pending_review', 6, FALSE
FROM users WHERE email = 'teacher@robolearn.com'
ON CONFLICT DO NOTHING;

-- Lessons for Module 1: Introducción a Python
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Qué es Python', '# Introducción a Python

Python es un lenguaje de programación...', 1
FROM modules m WHERE m.title = 'Introducción a Python' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Instalación y Setup', '# Instalando Python

Veamos cómo instalar Python...', 2
FROM modules m WHERE m.title = 'Introducción a Python' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Tu Primer Programa', '# Hola Mundo

Escribe tu primer programa...', 3
FROM modules m WHERE m.title = 'Introducción a Python' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 2: Variables y Tipos de Datos
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Variables', '# Variables en Python

Las variables almacenan datos...', 1
FROM modules m WHERE m.title = 'Variables y Tipos de Datos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Tipos de Datos', '# Tipos de Datos

Python tiene varios tipos...', 2
FROM modules m WHERE m.title = 'Variables y Tipos de Datos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Operaciones Básicas', '# Operaciones

Suma, resta, multiplicación...', 3
FROM modules m WHERE m.title = 'Variables y Tipos de Datos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 3: Estructuras de Control
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Condicionales', '# if, elif, else

Toma decisiones...', 1
FROM modules m WHERE m.title = 'Estructuras de Control' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Operadores Lógicos', '# and, or, not

Combina condiciones...', 2
FROM modules m WHERE m.title = 'Estructuras de Control' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 4: Bucles y Repeticiones
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Bucle For', '# El bucle for

Itera sobre secuencias...', 1
FROM modules m WHERE m.title = 'Bucles y Repeticiones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Bucle While', '# El bucle while

Repite mientras...', 2
FROM modules m WHERE m.title = 'Bucles y Repeticiones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 5: Funciones
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Definiendo Funciones', '# def

Crea tus propias funciones...', 1
FROM modules m WHERE m.title = 'Funciones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Parámetros y Retorno', '# Argumentos

Pasa datos a funciones...', 2
FROM modules m WHERE m.title = 'Funciones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Ámbito de Variables', '# Scope

Variable local vs global...', 3
FROM modules m WHERE m.title = 'Funciones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 6: Listas y Tuplas
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Listas', '# Listas

Colecciones ordenadas...', 1
FROM modules m WHERE m.title = 'Listas y Tuplas' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Tuplas', '# Tuplas

Colecciones inmutables...', 2
FROM modules m WHERE m.title = 'Listas y Tuplas' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 7: Diccionarios y Sets
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Diccionarios', '# Diccionarios

Pares clave-valor...', 1
FROM modules m WHERE m.title = 'Diccionarios y Sets' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Sets', '# Sets

Conjuntos sin duplicados...', 2
FROM modules m WHERE m.title = 'Diccionarios y Sets' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 8: Manejo de Archivos
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Lectura de Archivos', '# Leer archivos

open() y read()...', 1
FROM modules m WHERE m.title = 'Manejo de Archivos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Escritura de Archivos', '# Escribir archivos

write() y append()...', 2
FROM modules m WHERE m.title = 'Manejo de Archivos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 9: Módulos y Paquetes
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Importando Módulos', '# import

Reutiliza código...', 1
FROM modules m WHERE m.title = 'Módulos y Paquetes' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Paquetes con pip', '# pip

Instala paquetes...', 2
FROM modules m WHERE m.title = 'Módulos y Paquetes' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Lessons for Module 10: Proyecto Final
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Diseño del Robot', '# Diseño

Planifica tu robot...', 1
FROM modules m WHERE m.title = 'Proyecto Final: Robot Autónomo' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Lógica de Navegación', '# Navegación

Algoritmos de movimiento...', 2
FROM modules m WHERE m.title = 'Proyecto Final: Robot Autónomo' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Integración Final', '# Integración

Une todo el código...', 3
FROM modules m WHERE m.title = 'Proyecto Final: Robot Autónomo' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 1 (Introducción a Python)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Hola Mundo', 'Tu primer programa en Python', 'print("¡Hola, Mundo!")', 1, 10, '¡Hola, Mundo!', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Tu Primer Programa'
WHERE m.title = 'Introducción a Python' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Mi Nombre', 'Imprime tu nombre', 'nombre = "Ana"\nprint("Hola, " + nombre)', 1, 10, 'Hola, Ana', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Tu Primer Programa'
WHERE m.title = 'Introducción a Python' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 2 (Variables y Tipos de Datos)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Crear Variable', 'Crea y usa variables', 'x = 10\ny = 5\nprint(x + y)', 1, 10, '15', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Variables'
WHERE m.title = 'Variables y Tipos de Datos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Tipos en acción', 'Identifica tipos', 'print(type(42))\nprint(type(3.14))\nprint(type("hola"))', 1, 10, '<class ''int''>\n<class ''float''>\n<class ''str''>', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Tipos de Datos'
WHERE m.title = 'Variables y Tipos de Datos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Operaciones', 'Operaciones básicas', 'a = 10\nb = 3\nprint(a + b)\nprint(a - b)\nprint(a * b)', 1, 10, '13\n7\n30', 'output', 3
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Operaciones Básicas'
WHERE m.title = 'Variables y Tipos de Datos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 3 (Estructuras de Control)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Mayor de Edad', 'Condicional básico', 'edad = 18\nif edad >= 18:\n    print("Mayor de edad")\nelse:\n    print("Menor de edad")', 2, 15, 'Mayor de edad', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Condicionales'
WHERE m.title = 'Estructuras de Control' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Nota Final', 'Lógica con if/elif', 'nota = 85\nif nota >= 90:\n    print("Sobresaliente")\nelif nota >= 70:\n    print("Notable")\nelse:\n    print("Necesitas mejorar")', 2, 15, 'Notable', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Condicionales'
WHERE m.title = 'Estructuras de Control' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 4 (Bucles y Repeticiones)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Contar hasta 5', 'Bucle for básico', 'for i in range(1, 6):\n    print(i)', 2, 15, '1\n2\n3\n4\n5', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Bucle For'
WHERE m.title = 'Bucles y Repeticiones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Suma Acumulativa', 'Bucle while', 'total = 0\ni = 1\nwhile i <= 5:\n    total += i\n    i += 1\nprint(total)', 2, 15, '15', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Bucle While'
WHERE m.title = 'Bucles y Repeticiones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 5 (Funciones)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Primera Función', 'Define una función', 'def saludo():\n    return "Hola desde mi función"\n\nprint(saludo())', 3, 20, 'Hola desde mi función', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Definiendo Funciones'
WHERE m.title = 'Funciones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Sumar dos números', 'Función con parámetros', 'def sumar(a, b):\n    return a + b\n\nprint(sumar(3, 4))', 3, 20, '7', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Parámetros y Retorno'
WHERE m.title = 'Funciones' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 6 (Listas y Tuplas)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Mi primera lista', 'Trabaja con listas', 'frutas = ["manzana", "pera", "uva"]\nprint(frutas[0])\nprint(len(frutas))', 2, 15, 'manzana\n3', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Listas'
WHERE m.title = 'Listas y Tuplas' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Tupla fija', 'Tuplas inmutables', 'coord = (10, 20)\nprint(coord[0])\nprint(coord[1])', 2, 15, '10\n20', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Tuplas'
WHERE m.title = 'Listas y Tuplas' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 7 (Diccionarios y Sets)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Mi diccionario', 'Usa diccionarios', 'persona = {"nombre": "Luis", "edad": 25}\nprint(persona["nombre"])', 3, 20, 'Luis', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Diccionarios'
WHERE m.title = 'Diccionarios y Sets' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Operaciones con Sets', 'Usa conjuntos', 'a = {1, 2, 3}\nb = {3, 4, 5}\nprint(a | b)', 3, 20, '{1, 2, 3, 4, 5}', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Sets'
WHERE m.title = 'Diccionarios y Sets' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 8 (Manejo de Archivos)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Escribir archivo', 'Escribe en un archivo', 'with open("test.txt", "w") as f:\n    f.write("Hola archivo")\nprint("Archivo creado")', 3, 20, 'Archivo creado', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Escritura de Archivos'
WHERE m.title = 'Manejo de Archivos' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 9 (Módulos y Paquetes)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Usar math', 'Importa un módulo', 'import math\nprint(math.sqrt(16))', 3, 20, '4.0', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Importando Módulos'
WHERE m.title = 'Módulos y Paquetes' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Exercises for Module 10 (Proyecto Final)
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Clase Robot', 'Diseña la clase Robot', 'class Robot:\n    def __init__(self, nombre):\n        self.nombre = nombre\n    def saludar(self):\n        return f"Soy {self.nombre}"\n\nr = Robot("Robo")\nprint(r.saludar())', 5, 50, 'Soy Robo', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Diseño del Robot'
WHERE m.title = 'Proyecto Final: Robot Autónomo' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Movimiento', 'Lógica de movimiento', 'class Robot:\n    def __init__(self):\n        self.x = 0\n    def mover(self):\n        self.x += 1\n        return self.x\n\nr = Robot()\nprint(r.mover())\nprint(r.mover())', 5, 50, '1\n2', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Lógica de Navegación'
WHERE m.title = 'Proyecto Final: Robot Autónomo' AND m.is_global = TRUE
ON CONFLICT DO NOTHING;

-- Enrollments
INSERT INTO enrollments (student_id, module_id, status, enrolled_at)
SELECT u.id, m.id, 'active', CURRENT_TIMESTAMP - INTERVAL '10 days'
FROM users u, modules m
WHERE u.email IN ('student1@robolearn.com', 'student2@robolearn.com', 'student3@robolearn.com')
AND m.title = 'Introducción a Python'
ON CONFLICT DO NOTHING;

INSERT INTO enrollments (student_id, module_id, status, enrolled_at, completed_at)
SELECT u.id, m.id, 'completed', CURRENT_TIMESTAMP - INTERVAL '30 days', CURRENT_TIMESTAMP - INTERVAL '2 days'
FROM users u, modules m
WHERE u.email = 'student2@robolearn.com'
AND m.title = 'Variables y Tipos de Datos'
ON CONFLICT DO NOTHING;

-- Progress
INSERT INTO progress (student_id, module_id, percentage, completed_exercises, total_exercises, points_earned, is_completed, last_activity)
SELECT u.id, m.id, 45.0, 2, 5, 25, FALSE, CURRENT_TIMESTAMP - INTERVAL '1 hour'
FROM users u, modules m
WHERE u.email = 'student1@robolearn.com'
AND m.title = 'Introducción a Python'
ON CONFLICT (student_id, module_id) DO NOTHING;

INSERT INTO progress (student_id, module_id, percentage, completed_exercises, total_exercises, points_earned, is_completed, last_activity)
SELECT u.id, m.id, 100.0, 5, 5, 100, TRUE, CURRENT_TIMESTAMP - INTERVAL '2 days'
FROM users u, modules m
WHERE u.email = 'student2@robolearn.com'
AND m.title = 'Introducción a Python'
ON CONFLICT (student_id, module_id) DO NOTHING;

-- Exercise Attempts
INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count)
SELECT u.id, e.id, TRUE, 100.0, 1
FROM users u, exercises e, modules m
WHERE u.email = 'student1@robolearn.com'
AND e.module_id = m.id
AND m.title = 'Introducción a Python'
AND e.title = 'Hola Mundo'
ON CONFLICT DO NOTHING;

-- Teacher module exercise
INSERT INTO exercises (module_id, title, description, instructions, difficulty, points, "order")
SELECT m.id, 'Tu primer modelo', 'Entrena un clasificador', 'Usa scikit-learn para entrenar un clasificador básico.', 4, 50, 1
FROM modules m WHERE m.title = 'Inteligencia Artificial Básica'
ON CONFLICT DO NOTHING;

-- ============================================
-- Seed Achievement Definitions
-- ============================================
INSERT INTO achievements (name, description, icon, points, criteria) VALUES
('Primer Código', 'Escribiste tu primera línea de código en Robolearn.', 'star', 10, '{"type": "exercise_complete", "count": 1}'),
('Cinturón Blanco', 'Completaste el Módulo 1 de Fundamentos.', 'medal', 50, '{"type": "module_complete", "module_order": 1}'),
('Cinturón Amarillo', 'Completaste el Módulo 2 de Variables.', 'medal', 50, '{"type": "module_complete", "module_order": 2}'),
('Cinturón Naranja', 'Completaste el Módulo 3 de Estructuras de Control.', 'medal', 50, '{"type": "module_complete", "module_order": 3}'),
('Cinturón Verde', 'Completaste el Módulo 4 de Bucles.', 'medal', 50, '{"type": "module_complete", "module_order": 4}'),
('Cinturón Azul', 'Completaste el Módulo 5 de Funciones.', 'medal', 50, '{"type": "module_complete", "module_order": 5}'),
('Cinturón Marrón', 'Completaste el Módulo 6 de Listas y Tuplas.', 'medal', 50, '{"type": "module_complete", "module_order": 6}'),
('Cinturón Rojo', 'Completaste el Módulo 7 de Diccionarios y Sets.', 'medal', 50, '{"type": "module_complete", "module_order": 7}'),
('Cinturón Negro', 'Completaste el Módulo 8 de Archivos.', 'medal', 50, '{"type": "module_complete", "module_order": 8}'),
('Maestro Módulos', 'Completaste el Módulo 9 de Módulos y Paquetes.', 'medal', 50, '{"type": "module_complete", "module_order": 9}'),
('Robot Master', 'Completaste el Proyecto Final: Robot Autónomo.', 'trophy', 100, '{"type": "module_complete", "module_order": 10}'),
('Cazador de Bugs', 'Encontraste y corregiste 10 errores en tus ejercicios.', 'target', 30, '{"type": "exercise_fail_then_pass", "count": 10}'),
('Racha de 7 Días', 'Estudiaste 7 días seguidos sin fallar.', 'flame', 40, '{"type": "streak_days", "count": 7}'),
('Racha de 30 Días', 'Estudiaste 30 días seguidos sin fallar.', 'flame', 100, '{"type": "streak_days", "count": 30}'),
('Experto en Variables', 'Obtuviste puntuación perfecta en todos los ejercicios de variables.', 'zap', 30, '{"type": "module_perfect", "module_order": 2}'),
('Retador Nocturno', 'Completaste tu primer reto de programación.', 'award', 40, '{"type": "challenge_complete", "count": 1}'),
('Maestro del Reto', 'Completaste 5 retos de programación.', 'trophy', 80, '{"type": "challenge_complete", "count": 5}'),
('Estudiante Destacado', 'Completaste una clase de un docente con éxito.', 'shield', 60, '{"type": "class_complete", "count": 1}'),
('Perfect Score', 'Resolviste un ejercicio al primer intento sin errores.', 'award', 20, '{"type": "first_try", "count": 1}'),
('Matriculado', 'Te matriculaste en tu primera clase con un docente.', 'star', 15, '{"type": "class_enroll", "count": 1}')
ON CONFLICT DO NOTHING;
