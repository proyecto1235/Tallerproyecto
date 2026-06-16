-- ============================================
-- Robolearn Massive Seed Data (1000+ registros)
-- Para pruebas de carga y estrés
-- ============================================

-- ============================================
-- 1000 Estudiantes adicionales (password: student123)
-- ============================================
INSERT INTO users (email, password_hash, full_name, role, is_active, points, streak_days, public_id, bio)
SELECT
    'student' || (100 + i) || '@robolearn.com',
    '$2b$12$2nB0IaMwEsneWumF2ooVcehZfVCZJutDcQr58zLIfMAD/WgM17x8i',
    CASE floor(random() * 50)
        WHEN 0 THEN 'Mateo García' WHEN 1 THEN 'Valentina López' WHEN 2 THEN 'Santiago Martínez'
        WHEN 3 THEN 'Camila Rodríguez' WHEN 4 THEN 'Benjamín Hernández' WHEN 5 THEN 'Isabella González'
        WHEN 6 THEN 'Sebastián Pérez' WHEN 7 THEN 'Sofía Sánchez' WHEN 8 THEN 'Joaquín Ramírez'
        WHEN 9 THEN 'Emilia Torres' WHEN 10 THEN 'Matías Flores' WHEN 11 THEN 'Luciana Rivera'
        WHEN 12 THEN 'Nicolás Gómez' WHEN 13 THEN 'Martina Díaz' WHEN 14 THEN 'Alejandro Cruz'
        WHEN 15 THEN 'Valeria Morales' WHEN 16 THEN 'Diego Ortiz' WHEN 17 THEN 'Renata Vargas'
        WHEN 18 THEN 'Gabriel Castillo' WHEN 19 THEN 'Antonella Rojas' WHEN 20 THEN 'Emilio Soto'
        WHEN 21 THEN 'Daniela Peña' WHEN 22 THEN 'Lucas Medina' WHEN 23 THEN 'Samantha Guerrero'
        WHEN 24 THEN 'Julián Contreras' WHEN 25 THEN 'Ximena Navarro' WHEN 26 THEN 'Felipe Vega'
        WHEN 27 THEN 'Paulina Delgado' WHEN 28 THEN 'Tomás Mendoza' WHEN 29 THEN 'Carolina Herrera'
        WHEN 30 THEN 'Maximiliano Reyes' WHEN 31 THEN 'Gabriela Silva' WHEN 32 THEN 'Leonardo Guzmán'
        WHEN 33 THEN 'Mariana Aguirre' WHEN 34 THEN 'Fernando Campos' WHEN 35 THEN 'Andrea Fuentes'
        WHEN 36 THEN 'Ignacio Cabrera' WHEN 37 THEN 'Rocío Rivas' WHEN 38 THEN 'Héctor Calvo'
        WHEN 39 THEN 'Macarena Paredes' WHEN 40 THEN 'Pablo Figueroa' WHEN 41 THEN 'Consuelo Molina'
        WHEN 42 THEN 'Rafael Espinoza' WHEN 43 THEN 'Francisca Acosta' WHEN 44 THEN 'Álvaro Benítez'
        WHEN 45 THEN 'Josefa Cárdenas' WHEN 46 THEN 'Vicente Pizarro' WHEN 47 THEN 'Trinidad Sandoval'
        WHEN 48 THEN 'Cristóbal Orellana' WHEN 49 THEN 'Amanda Valencia'
        ELSE 'Estudiante' || (100 + i)
    END,
    'student', TRUE,
    floor(random() * 500)::INTEGER,
    floor(random() * 30)::INTEGER,
    gen_random_uuid()::text,
    CASE floor(random() * 5)
        WHEN 0 THEN 'Estudiante aprendiendo Python desde cero.'
        WHEN 1 THEN 'Apasionado por la tecnología y la robótica.'
        WHEN 2 THEN 'Me gusta resolver problemas con código.'
        WHEN 3 THEN 'Explorando el mundo de la programación.'
        ELSE 'Estudiante de RoboLearn buscando nuevos retos.'
    END
FROM generate_series(1, 1000) i
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- ~ 2000 Exercise Attempts (60% passed, 25% failed, 15% multi-intento)
-- ============================================
INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count)
SELECT
    u.id,
    e.id,
    random() < 0.6,
    round((0.5 + random() * 0.5)::NUMERIC, 2),
    floor(random() * 3 + 1)::INTEGER
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    LIMIT 500
) u
CROSS JOIN (
    SELECT id FROM exercises
    LIMIT 50
) e
CROSS JOIN generate_series(1, 1)
ON CONFLICT DO NOTHING;

-- ============================================
-- 300 Enrollments en módulos globales
-- ============================================
INSERT INTO enrollments (student_id, module_id, status, enrolled_at)
SELECT
    u.id,
    m.id,
    CASE floor(random() * 10)
        WHEN 0 THEN 'pending' WHEN 1 THEN 'withdrawn'
        WHEN 2 THEN 'completed'
        ELSE 'active'
    END,
    CURRENT_TIMESTAMP - (random() * INTERVAL '60 days')
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    ORDER BY random() LIMIT 100
) u
CROSS JOIN (
    SELECT id FROM modules WHERE is_global = TRUE
    ORDER BY random() LIMIT 3
) m
ON CONFLICT DO NOTHING;

-- ============================================
-- 500 Progress records
-- ============================================
INSERT INTO progress (student_id, module_id, percentage, completed_exercises, total_exercises, points_earned, is_completed, last_activity)
SELECT
    u.id,
    m.id,
    round((random() * 100)::NUMERIC, 2),
    floor(random() * 10)::INTEGER,
    10,
    floor(random() * 200)::INTEGER,
    random() < 0.2,
    CURRENT_TIMESTAMP - (random() * INTERVAL '30 days')
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    ORDER BY random() LIMIT 150
) u
CROSS JOIN (
    SELECT id FROM modules WHERE is_global = TRUE
    ORDER BY random() LIMIT 2
) m
ON CONFLICT (student_id, module_id) DO NOTHING;

-- ============================================
-- 100 Enrollments en clases de teacher
-- ============================================
INSERT INTO class_enrollments (student_id, class_id, status, enrolled_at)
SELECT
    u.id,
    c.id,
    CASE floor(random() * 10)
        WHEN 0 THEN 'pending' WHEN 1 THEN 'rejected'
        WHEN 2 THEN 'withdrawn'
        ELSE 'approved'
    END,
    CURRENT_TIMESTAMP - (random() * INTERVAL '30 days')
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    ORDER BY random() LIMIT 50
) u
CROSS JOIN (
    SELECT id FROM classes WHERE is_published = TRUE
) c
ON CONFLICT DO NOTHING;

-- ============================================
-- 300 Class exercise attempts
-- ============================================
INSERT INTO class_exercise_attempts (student_id, class_exercise_id, class_module_id, passed, score, attempt_count)
SELECT
    u.id,
    ce.id,
    cm.id,
    random() < 0.55,
    round((0.3 + random() * 0.7)::NUMERIC, 2),
    floor(random() * 4 + 1)::INTEGER
FROM (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    ORDER BY random() LIMIT 100
) u
CROSS JOIN (
    SELECT id FROM class_exercises
    LIMIT 50
) ce
CROSS JOIN (
    SELECT id FROM class_modules
    LIMIT 10
) cm
CROSS JOIN generate_series(1, 1)
ON CONFLICT DO NOTHING;

-- ============================================
-- 200 Challenge attempts
-- ============================================
INSERT INTO challenge_attempts (challenge_id, student_id, passed, score, attempt_count, submitted_code)
SELECT
    c.id,
    u.id,
    random() < 0.4,
    round((random() * 100)::NUMERIC, 2),
    floor(random() * 5 + 1)::INTEGER,
    CASE floor(random() * 3)
        WHEN 0 THEN 'print("hello")'
        WHEN 1 THEN 'for i in range(5):\n    print(i)'
        ELSE 'def solve():\n    return 42'
    END
FROM (
    SELECT id FROM challenges
    LIMIT 20
) c
CROSS JOIN (
    SELECT id FROM users WHERE role = 'student' AND email LIKE 'student%'
    LIMIT 100
) u
CROSS JOIN generate_series(1, 1)
ON CONFLICT DO NOTHING;

-- ============================================
-- Verificación
-- ============================================
DO $$
DECLARE
    student_count INTEGER;
    attempt_count INTEGER;
    enrollment_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO student_count FROM users WHERE role = 'student';
    SELECT COUNT(*) INTO attempt_count FROM exercise_attempts;
    SELECT COUNT(*) INTO enrollment_count FROM enrollments;
    RAISE NOTICE 'Massive seed complete: % students, % attempts, % enrollments',
        student_count, attempt_count, enrollment_count;
END $$;
