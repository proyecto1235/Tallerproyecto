-- ============================================
-- Teacher Data Seed: Poblates módulos del teacher con estudiantes reales
-- Ejecutar DESPUÉS de 003-seed-massive.sql
-- ============================================

-- ============================================
-- 1. Publicar el módulo Machine Learning del teacher
-- ============================================
UPDATE modules SET is_published = TRUE, status = 'approved'
WHERE title = 'Machine Learning' AND teacher_id = (SELECT id FROM users WHERE email = 'teacher@robolearn.com');

-- ============================================
-- 2. Crear lessons y exercises para los módulos del teacher
-- ============================================

-- Lessons para Inteligencia Artificial Básica (necesita tener al menos 1 lesson con exercise)
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Fundamentos de IA', '# Fundamentos de Inteligencia Artificial
La IA permite que las máquinas aprendan de la experiencia...', 1
FROM modules m WHERE m.title = 'Inteligencia Artificial Básica'
AND NOT EXISTS (SELECT 1 FROM lessons l WHERE l.module_id = m.id AND l.title = 'Fundamentos de IA')
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Algoritmos de Búsqueda', '# Algoritmos de Búsqueda
Los algoritmos de búsqueda son fundamentales en IA...', 2
FROM modules m WHERE m.title = 'Inteligencia Artificial Básica'
AND NOT EXISTS (SELECT 1 FROM lessons l WHERE l.module_id = m.id AND l.title = 'Algoritmos de Búsqueda')
ON CONFLICT DO NOTHING;

-- Exercises para Inteligencia Artificial Básica
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Clasificador Simple', 'Implementa un clasificador básico', E'def clasificar(valor):\n    if valor > 0.5:\n        return "positivo"\n    return "negativo"\n\nprint(clasificar(0.8))\nprint(clasificar(0.2))', 3, 25, E'positivo\nnegativo', 'output', 2
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Fundamentos de IA'
WHERE m.title = 'Inteligencia Artificial Básica'
AND NOT EXISTS (SELECT 1 FROM exercises e WHERE e.module_id = m.id AND e.title = 'Clasificador Simple')
ON CONFLICT DO NOTHING;

INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Búsqueda en Lista', 'Implementa búsqueda lineal', E'datos = [3, 7, 1, 9, 4]\ndef buscar(lista, target):\n    for i, v in enumerate(lista):\n        if v == target:\n            return i\n    return -1\n\nprint(buscar(datos, 9))\nprint(buscar(datos, 5))', 3, 25, E'3\n-1', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Algoritmos de Búsqueda'
WHERE m.title = 'Inteligencia Artificial Básica'
AND NOT EXISTS (SELECT 1 FROM exercises e WHERE e.module_id = m.id AND e.title = 'Búsqueda en Lista')
ON CONFLICT DO NOTHING;

-- Lessons para Machine Learning
INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Introducción al ML', '# Machine Learning
El Machine Learning es una rama de la IA...', 1
FROM modules m WHERE m.title = 'Machine Learning'
AND NOT EXISTS (SELECT 1 FROM lessons l WHERE l.module_id = m.id AND l.title = 'Introducción al ML')
ON CONFLICT DO NOTHING;

INSERT INTO lessons (module_id, title, theory_content, "order")
SELECT m.id, 'Regresión Lineal', '# Regresión Lineal
La regresión lineal predice valores numéricos...', 2
FROM modules m WHERE m.title = 'Machine Learning'
AND NOT EXISTS (SELECT 1 FROM lessons l WHERE l.module_id = m.id AND l.title = 'Regresión Lineal')
ON CONFLICT DO NOTHING;

-- Exercises para Machine Learning
INSERT INTO exercises (module_id, lesson_id, title, description, instructions, difficulty, points, solution_output, solution_type, "order")
SELECT m.id, l.id, 'Predicción Simple', 'Implementa una función de predicción lineal', E'def predecir(x, m, b):\n    return m * x + b\n\nprint(predecir(2, 3, 1))\nprint(predecir(5, 2, 0))', 4, 30, E'7\n10', 'output', 1
FROM modules m JOIN lessons l ON l.module_id = m.id AND l.title = 'Regresión Lineal'
WHERE m.title = 'Machine Learning'
AND NOT EXISTS (SELECT 1 FROM exercises e WHERE e.module_id = m.id AND e.title = 'Predicción Simple')
ON CONFLICT DO NOTHING;

-- ============================================
-- 3. Matricular estudiantes en los módulos del teacher
-- ============================================
INSERT INTO enrollments (student_id, module_id, status, enrolled_at)
SELECT u.id, m.id, 'active', CURRENT_TIMESTAMP - (random() * INTERVAL '45 days')
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    ORDER BY random() LIMIT 150
) u
CROSS JOIN (
    SELECT id FROM modules WHERE teacher_id = (SELECT id FROM users WHERE email = 'teacher@robolearn.com')
) m
ON CONFLICT DO NOTHING;

-- Also enroll the 3 demo students
INSERT INTO enrollments (student_id, module_id, status, enrolled_at)
SELECT u.id, m.id, 'active', CURRENT_TIMESTAMP - INTERVAL '5 days'
FROM users u, modules m
WHERE u.email IN ('student1@robolearn.com', 'student2@robolearn.com', 'student3@robolearn.com')
AND m.teacher_id = (SELECT id FROM users WHERE email = 'teacher@robolearn.com')
ON CONFLICT DO NOTHING;

-- ============================================
-- 4. Progress records para teacher modules
-- ============================================
INSERT INTO progress (student_id, module_id, percentage, completed_exercises, total_exercises, points_earned, is_completed, last_activity)
SELECT
    e.student_id,
    e.module_id,
    round((random() * 100)::NUMERIC, 2),
    floor(random() * 5)::INTEGER,
    5,
    floor(random() * 100)::INTEGER,
    random() < 0.15,
    CURRENT_TIMESTAMP - (random() * INTERVAL '7 days')
FROM enrollments e
WHERE e.module_id IN (SELECT id FROM modules WHERE teacher_id = (SELECT id FROM users WHERE email = 'teacher@robolearn.com'))
AND NOT EXISTS (SELECT 1 FROM progress p WHERE p.student_id = e.student_id AND p.module_id = e.module_id)
ON CONFLICT (student_id, module_id) DO NOTHING;

-- ============================================
-- 5. Exercise attempts for teacher exercises (con fechas recientes para weekly_activity)
-- ============================================
INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count, submitted_at)
SELECT
    u.id,
    e.id,
    random() < 0.65,
    round((0.4 + random() * 0.6)::NUMERIC, 2),
    floor(random() * 3 + 1)::INTEGER,
    CURRENT_TIMESTAMP - (random() * INTERVAL '6 days')
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    ORDER BY random() LIMIT 80
) u
CROSS JOIN (
    SELECT e.id FROM exercises e
    JOIN modules m ON m.id = e.module_id
    WHERE m.teacher_id = (SELECT id FROM users WHERE email = 'teacher@robolearn.com')
) e
CROSS JOIN generate_series(1, 1)
ON CONFLICT DO NOTHING;

-- Demo students exercise attempts for teacher exercises
INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count, submitted_at)
SELECT u.id, e.id, TRUE, 100.0, 1, CURRENT_TIMESTAMP - INTERVAL '1 day'
FROM users u, exercises e
JOIN modules m ON m.id = e.module_id
WHERE u.email IN ('student1@robolearn.com', 'student2@robolearn.com')
AND m.teacher_id = (SELECT id FROM users WHERE email = 'teacher@robolearn.com')
AND e.title = 'Tu primer modelo'
ON CONFLICT DO NOTHING;

-- ============================================
-- 6. Class enrollments en las clases del teacher (más datos)
-- ============================================
INSERT INTO class_enrollments (student_id, class_id, status, enrolled_at)
SELECT u.id, c.id, 'approved', CURRENT_TIMESTAMP - (random() * INTERVAL '20 days')
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    ORDER BY random() LIMIT 40
) u
CROSS JOIN (
    SELECT id FROM classes WHERE teacher_id = (SELECT id FROM users WHERE email = 'teacher@robolearn.com')
) c
ON CONFLICT DO NOTHING;

-- ============================================
-- 7. Class exercise attempts (para activity chart)
-- ============================================
INSERT INTO class_exercise_attempts (student_id, class_exercise_id, class_module_id, passed, score, attempt_count)
SELECT
    ce.student_id,
    cl_ex.id,
    cm.id,
    random() < 0.6,
    round((0.3 + random() * 0.7)::NUMERIC, 2),
    floor(random() * 4 + 1)::INTEGER
FROM class_enrollments ce
CROSS JOIN (
    SELECT id FROM class_exercises LIMIT 10
) cl_ex
CROSS JOIN (
    SELECT id FROM class_modules LIMIT 5
) cm
WHERE ce.status = 'approved'
LIMIT 100
ON CONFLICT DO NOTHING;

-- ============================================
-- 8. Verificación
-- ============================================
DO $$
DECLARE
    t_id INTEGER;
    t_students INTEGER;
    t_progress INTEGER;
    t_attempts INTEGER;
BEGIN
    SELECT id INTO t_id FROM users WHERE email = 'teacher@robolearn.com';
    
    SELECT COUNT(DISTINCT e.student_id) INTO t_students
    FROM enrollments e JOIN modules m ON e.module_id = m.id
    WHERE m.teacher_id = t_id;
    
    SELECT COUNT(*) INTO t_progress
    FROM progress p JOIN modules m ON p.module_id = m.id
    WHERE m.teacher_id = t_id;
    
    SELECT COUNT(*) INTO t_attempts
    FROM exercise_attempts ea
    JOIN exercises e ON e.id = ea.exercise_id
    JOIN modules m ON m.id = e.module_id
    WHERE m.teacher_id = t_id;
    
    RAISE NOTICE 'Teacher seed complete: % students, % progress, % attempts',
        t_students, t_progress, t_attempts;
END $$;
