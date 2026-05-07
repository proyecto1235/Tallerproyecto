-- Robolearn Seed Data
-- Sample data for development and testing

-- ============================================
-- Insert Sample Users
-- ============================================

-- Admin user
INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES (
    'admin@robolearn.com',
    '$2b$12$bGM8zs/InGnD1y8CjoqEgOdxJFEhAjfib2/jZckpnA3p0mhd/fpiW', -- password: admin123
    'Admin User',
    'admin',
    TRUE,
    0,
    0
) ON CONFLICT (email) DO NOTHING;

-- Teacher user
INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES (
    'teacher@robolearn.com',
    '$2b$12$JFpw/eFD6s9cDikL1TJsYeExzr.85GpQUS1rvEqnEvJVJ4w/ZMOsC', -- password: teacher123
    'Professor García',
    'teacher',
    TRUE,
    500,
    15
) ON CONFLICT (email) DO NOTHING;

-- Student users
INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days)
VALUES 
(
    'student1@robolearn.com',
    '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i', -- password: student123
    'Juan Pérez',
    'student',
    TRUE,
    250,
    5
),
(
    'student2@robolearn.com',
    '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i', -- password: student123
    'María López',
    'student',
    TRUE,
    420,
    8
),
(
    'student3@robolearn.com',
    '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i', -- password: student123
    'Carlos Rodríguez',
    'student',
    TRUE,
    180,
    3
)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- Insert Sample Modules
-- ============================================

-- ============================================
-- Insert 10 Global Python Modules (admin-managed, free learning path)
-- ============================================

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Introducción a Python', 'Conoce el lenguaje, escribe tu primer programa y entiende la sintaxis básica.', 'approved', 1, TRUE, TRUE, 'Principiante', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Variables y Tipos de Datos', 'Aprende a almacenar información en variables y a trabajar con números y texto.', 'approved', 2, TRUE, TRUE, 'Principiante', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Estructuras de Control', 'Toma decisiones en tu código con if, elif y else.', 'approved', 3, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Bucles y Repeticiones', 'Domina for y while para automatizar tareas repetitivas.', 'approved', 4, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Funciones', 'Crea bloques de código reutilizables y organiza mejor tus programas.', 'approved', 5, TRUE, TRUE, 'Avanzado', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Listas y Tuplas', 'Trabaja con colecciones de datos y entiende sus diferencias.', 'approved', 6, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Diccionarios y Sets', 'Almacena datos con clave-valor y conjuntos sin duplicados.', 'approved', 7, TRUE, TRUE, 'Intermedio', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Manejo de Archivos', 'Lee y escribe archivos de texto y CSV con Python.', 'approved', 8, TRUE, TRUE, 'Avanzado', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Módulos y Paquetes', 'Organiza tu código en módulos reutilizables y usa pip.', 'approved', 9, TRUE, TRUE, 'Avanzado', 2
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published, is_global, difficulty, lesson_count)
SELECT id, 'Proyecto Final: Robot Autónomo', 'Aplica todo lo aprendido para programar un robot virtual que navega solo.', 'approved', 10, TRUE, TRUE, 'Avanzado', 3
FROM users WHERE email = 'admin@robolearn.com'
ON CONFLICT DO NOTHING;

-- ============================================
-- Insert Sample Exercises
-- ============================================

INSERT INTO exercises (module_id, title, description, instructions, difficulty, points, "order")
SELECT 
    m.id,
    'Hola Mundo',
    'Tu primer programa en Python',
    'Escribe un programa que imprima "¡Hola, Mundo!"',
    1,
    10,
    1
FROM modules m WHERE m.title = 'Introducción a Python'
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, title, description, instructions, difficulty, points, "order")
SELECT 
    m.id,
    'Variables y Tipos',
    'Trabaja con variables en Python',
    'Crea variables de diferentes tipos y realiza operaciones con ellas',
    1,
    15,
    2
FROM modules m WHERE m.title = 'Introducción a Python'
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, title, description, instructions, difficulty, points, "order")
SELECT 
    m.id,
    'Bucles y Condicionales',
    'Control de flujo en Python',
    'Implementa programas usando if/else y bucles for/while',
    2,
    25,
    3
FROM modules m WHERE m.title = 'Introducción a Python'
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, title, description, instructions, difficulty, points, "order")
SELECT 
    m.id,
    'Creando Clases',
    'Tu primera clase en Python',
    'Define una clase con atributos y métodos',
    3,
    40,
    1
FROM modules m WHERE m.title = 'Programación Orientada a Objetos'
ON CONFLICT DO NOTHING;

-- ============================================
-- Insert Sample Enrollments
-- ============================================

INSERT INTO enrollments (student_id, module_id, status, enrolled_at)
SELECT 
    u.id,
    m.id,
    'active',
    CURRENT_TIMESTAMP - INTERVAL '10 days'
FROM users u, modules m
WHERE u.email IN ('student1@robolearn.com', 'student2@robolearn.com', 'student3@robolearn.com')
AND m.title = 'Introducción a Python'
ON CONFLICT DO NOTHING;

INSERT INTO enrollments (student_id, module_id, status, enrolled_at, completed_at)
SELECT 
    u.id,
    m.id,
    'completed',
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP - INTERVAL '2 days'
FROM users u, modules m
WHERE u.email = 'student2@robolearn.com'
AND m.title = 'Programación Orientada a Objetos'
ON CONFLICT DO NOTHING;

-- ============================================
-- Insert Sample Progress
-- ============================================

INSERT INTO progress (student_id, module_id, percentage, completed_exercises, total_exercises, points_earned, is_completed, last_activity)
SELECT 
    u.id,
    m.id,
    45.0,
    2,
    5,
    25,
    FALSE,
    CURRENT_TIMESTAMP - INTERVAL '1 hour'
FROM users u, modules m
WHERE u.email = 'student1@robolearn.com'
AND m.title = 'Introducción a Python'
ON CONFLICT (student_id, module_id) DO NOTHING;

INSERT INTO progress (student_id, module_id, percentage, completed_exercises, total_exercises, points_earned, is_completed, last_activity)
SELECT 
    u.id,
    m.id,
    100.0,
    5,
    5,
    100,
    TRUE,
    CURRENT_TIMESTAMP - INTERVAL '2 days'
FROM users u, modules m
WHERE u.email = 'student2@robolearn.com'
AND m.title = 'Introducción a Python'
ON CONFLICT (student_id, module_id) DO NOTHING;

-- ============================================
-- Insert Sample Exercise Attempts
-- ============================================

INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count)
SELECT 
    u.id,
    e.id,
    TRUE,
    100.0,
    1
FROM users u, exercises e, modules m
WHERE u.email = 'student1@robolearn.com'
AND e.module_id = m.id
AND m.title = 'Introducción a Python'
AND e.title = 'Hola Mundo'
ON CONFLICT DO NOTHING;

-- ============================================
-- Insert More Advanced Modules
-- ============================================

INSERT INTO modules (title, description, teacher_id, status, "order", is_published)
SELECT 
    'Inteligencia Artificial Básica',
    'Aprende los conceptos fundamentales de IA usando Python y librerías sencillas.',
    id,
    'approved',
    5,
    TRUE
FROM users WHERE email = 'teacher@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO modules (title, description, teacher_id, status, "order", is_published)
SELECT 
    'Machine Learning',
    'Introducción a algoritmos de clasificación y regresión.',
    id,
    'pending_review',
    6,
    FALSE
FROM users WHERE email = 'teacher@robolearn.com'
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, title, description, instructions, difficulty, points, "order")
SELECT 
    m.id,
    'Tu primer modelo',
    'Entrena un clasificador',
    'Usa scikit-learn para entrenar un clasificador básico.',
    4,
    50,
    1
FROM modules m WHERE m.title = 'Inteligencia Artificial Básica'
ON CONFLICT DO NOTHING;

-- ============================================
-- Print Summary
-- ============================================

SELECT 'Seed data completed successfully!' as status;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_modules FROM modules;
SELECT COUNT(*) as total_exercises FROM exercises;
