-- Robolearn Stored Procedures
-- Funciones y procedimientos almacenados para seguridad y rendimiento

-- ============================================
-- PROCEDURE: sp_upsert_progress
-- Actualiza o inserta progreso de forma atomica
-- ============================================

CREATE OR REPLACE FUNCTION sp_upsert_progress(
    p_student_id INTEGER,
    p_module_id INTEGER,
    p_points_earned INTEGER DEFAULT 0
) RETURNS TABLE(
    progress_id INTEGER,
    percentage NUMERIC,
    completed_exercises INTEGER,
    total_exercises INTEGER,
    is_completed BOOLEAN
) AS $$
DECLARE
    v_total_ex INTEGER;
    v_passed_ex INTEGER;
    v_percentage NUMERIC;
    v_is_complete BOOLEAN;
BEGIN
    SELECT COUNT(*) INTO v_total_ex
    FROM exercises WHERE module_id = p_module_id;

    SELECT COUNT(DISTINCT ea.exercise_id) INTO v_passed_ex
    FROM exercise_attempts ea
    JOIN exercises e ON e.id = ea.exercise_id
    WHERE ea.student_id = p_student_id
      AND e.module_id = p_module_id
      AND ea.passed = TRUE;

    v_percentage := CASE WHEN v_total_ex > 0
        THEN ROUND((v_passed_ex::NUMERIC / v_total_ex) * 100, 2)
        ELSE 0 END;

    v_is_complete := (v_total_ex > 0 AND v_passed_ex >= v_total_ex);

    INSERT INTO progress (student_id, module_id, completed_exercises, total_exercises,
                          points_earned, percentage, is_completed, last_activity)
    VALUES (p_student_id, p_module_id, v_passed_ex, v_total_ex,
            p_points_earned, v_percentage, v_is_complete, NOW())
    ON CONFLICT (student_id, module_id) DO UPDATE SET
        completed_exercises = v_passed_ex,
        total_exercises = v_total_ex,
        points_earned = progress.points_earned + p_points_earned,
        percentage = v_percentage,
        is_completed = v_is_complete,
        last_activity = NOW(),
        updated_at = NOW()
    RETURNING id, percentage, completed_exercises, total_exercises, is_completed;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PROCEDURE: sp_record_exercise_attempt
-- Registra un intento de ejercicio con validacion
-- ============================================

CREATE OR REPLACE FUNCTION sp_record_exercise_attempt(
    p_student_id INTEGER,
    p_exercise_id INTEGER,
    p_passed BOOLEAN,
    p_score NUMERIC,
    p_points_awarded INTEGER DEFAULT 0
) RETURNS TABLE(
    attempt_id INTEGER,
    attempt_count INTEGER,
    total_passed INTEGER
) AS $$
DECLARE
    v_prev_attempts INTEGER;
    v_attempt_count INTEGER;
BEGIN
    SELECT COALESCE(MAX(attempt_count), 0) INTO v_prev_attempts
    FROM exercise_attempts
    WHERE student_id = p_student_id AND exercise_id = p_exercise_id;

    v_attempt_count := v_prev_attempts + 1;

    INSERT INTO exercise_attempts (student_id, exercise_id, passed, score, attempt_count)
    VALUES (p_student_id, p_exercise_id, p_passed, p_score, v_attempt_count);

    IF p_passed AND p_points_awarded > 0 THEN
        UPDATE users SET points = COALESCE(points, 0) + p_points_awarded
        WHERE id = p_student_id;
    END IF;

    RETURN QUERY
    SELECT ea.id, v_attempt_count,
           (SELECT COUNT(*) FROM exercise_attempts
            WHERE student_id = p_student_id AND exercise_id = p_exercise_id AND passed = TRUE)
    FROM exercise_attempts ea
    WHERE ea.student_id = p_student_id AND ea.exercise_id = p_exercise_id
    ORDER BY ea.submitted_at DESC LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_student_progress_summary
-- Resumen completo de progreso de un estudiante
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_student_progress_summary(
    p_student_id INTEGER
) RETURNS TABLE(
    total_modules INTEGER,
    completed_modules INTEGER,
    active_modules INTEGER,
    total_exercises INTEGER,
    completed_exercises INTEGER,
    total_points INTEGER,
    avg_progress NUMERIC,
    current_module VARCHAR,
    streak_days INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM enrollments WHERE student_id = p_student_id)::INTEGER,
        (SELECT COUNT(*) FROM enrollments WHERE student_id = p_student_id AND status = 'completed')::INTEGER,
        (SELECT COUNT(*) FROM enrollments WHERE student_id = p_student_id AND status = 'active')::INTEGER,
        (SELECT COUNT(*) FROM exercises e
         JOIN enrollments en ON en.module_id = e.module_id
         WHERE en.student_id = p_student_id AND en.status IN ('active', 'completed'))::INTEGER,
        (SELECT COUNT(DISTINCT exercise_id) FROM exercise_attempts
         WHERE student_id = p_student_id AND passed = TRUE)::INTEGER,
        (SELECT COALESCE(SUM(points_earned), 0) FROM progress WHERE student_id = p_student_id)::INTEGER,
        COALESCE((SELECT AVG(percentage) FROM progress WHERE student_id = p_student_id), 0),
        COALESCE((SELECT m.title FROM modules m
         JOIN enrollments e ON e.module_id = m.id
         WHERE e.student_id = p_student_id AND e.status = 'active'
         ORDER BY m."order" LIMIT 1), 'Ninguno'),
        COALESCE((SELECT streak_days FROM users WHERE id = p_student_id), 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_teacher_dashboard
-- Dashboard metrics for a teacher
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_teacher_dashboard(
    p_teacher_id INTEGER
) RETURNS TABLE(
    total_students INTEGER,
    total_modules INTEGER,
    avg_progress NUMERIC,
    completion_rate NUMERIC,
    total_enrollments INTEGER,
    course_progress JSON
) AS $$
BEGIN
    RETURN QUERY
    WITH teacher_modules AS (
        SELECT id, title FROM modules WHERE teacher_id = p_teacher_id
    ),
    module_stats AS (
        SELECT m.id, m.title,
               COUNT(DISTINCT e.student_id) as student_count,
               AVG(COALESCE(p.percentage, 0)) as avg_pct,
               COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.student_id END) as completed_count
        FROM teacher_modules m
        LEFT JOIN enrollments e ON e.module_id = m.id AND e.status IN ('active', 'completed')
        LEFT JOIN progress p ON p.student_id = e.student_id AND p.module_id = m.id
        GROUP BY m.id, m.title
    )
    SELECT
        (SELECT COUNT(DISTINCT e.student_id) FROM enrollments e
         JOIN modules m ON e.module_id = m.id WHERE m.teacher_id = p_teacher_id)::INTEGER,
        (SELECT COUNT(*) FROM teacher_modules)::INTEGER,
        COALESCE((SELECT AVG(avg_pct) FROM module_stats), 0),
        CASE WHEN (SELECT SUM(student_count) FROM module_stats) > 0
             THEN ROUND((SELECT SUM(completed_count)::NUMERIC / NULLIF(SUM(student_count), 0) * 100
                         FROM module_stats), 2)
             ELSE 0 END,
        (SELECT COUNT(*) FROM enrollments e
         JOIN modules m ON e.module_id = m.id WHERE m.teacher_id = p_teacher_id)::INTEGER,
        (SELECT COALESCE(json_agg(json_build_object(
            'name', title, 'progress', ROUND(avg_pct, 2)
         ) ORDER BY avg_pct DESC), '[]'::json) FROM module_stats WHERE student_count > 0);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_admin_stats
 -- Dashboard stats for admin panel
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_admin_stats()
RETURNS TABLE(
    total_users INTEGER,
    active_students INTEGER,
    active_teachers INTEGER,
    total_modules INTEGER,
    published_modules INTEGER,
    pending_teachers INTEGER,
    pending_reviews INTEGER,
    total_enrollments INTEGER,
    total_achievements INTEGER,
    total_exercises INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM users)::INTEGER,
        (SELECT COUNT(*) FROM users WHERE role = 'student' AND is_active = TRUE)::INTEGER,
        (SELECT COUNT(*) FROM users WHERE role = 'teacher' AND is_active = TRUE)::INTEGER,
        (SELECT COUNT(*) FROM modules)::INTEGER,
        (SELECT COUNT(*) FROM modules WHERE is_published = TRUE AND status = 'approved')::INTEGER,
        (SELECT COUNT(*) FROM users WHERE teacher_request_status = 'pending')::INTEGER,
        (SELECT COUNT(*) FROM modules WHERE status = 'pending_review')::INTEGER,
        (SELECT COUNT(*) FROM enrollments)::INTEGER,
        (SELECT COUNT(*) FROM user_achievements)::INTEGER,
        (SELECT COUNT(*) FROM exercises)::INTEGER;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_admin_modules
-- Listado completo de modulos para admin (con filtros)
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_admin_modules(
    p_status_filter VARCHAR DEFAULT NULL,
    p_search VARCHAR DEFAULT NULL
) RETURNS TABLE(
    id INTEGER,
    title VARCHAR,
    description TEXT,
    teacher_name VARCHAR,
    status VARCHAR,
    "order" INTEGER,
    is_published BOOLEAN,
    is_global BOOLEAN,
    difficulty VARCHAR,
    lesson_count INTEGER,
    exercise_count INTEGER,
    enrollment_count INTEGER,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT m.id, m.title, m.description,
           u.full_name::VARCHAR,
           m.status, m."order", m.is_published, m.is_global,
           m.difficulty, m.lesson_count,
           (SELECT COUNT(*) FROM exercises WHERE module_id = m.id)::INTEGER,
           (SELECT COUNT(*) FROM enrollments WHERE module_id = m.id)::INTEGER,
           m.created_at
    FROM modules m
    LEFT JOIN users u ON m.teacher_id = u.id
    WHERE (p_status_filter IS NULL OR m.status = p_status_filter)
      AND (p_search IS NULL OR m.title ILIKE '%' || p_search || '%')
    ORDER BY m."order" ASC, m.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_student_alerts
-- Alertas inteligentes para un docente (basado en datos reales)
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_student_alerts(
    p_teacher_id INTEGER
) RETURNS TABLE(
    student_id INTEGER,
    student_name VARCHAR,
    module_id INTEGER,
    module_title VARCHAR,
    alert_type VARCHAR,
    priority VARCHAR,
    message TEXT,
    progress NUMERIC,
    days_enrolled INTEGER,
    progress_velocity NUMERIC,
    avg_velocity NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH teacher_mods AS (
        SELECT id FROM modules WHERE teacher_id = p_teacher_id
    ),
    student_data AS (
        SELECT e.student_id, e.module_id, e.status,
               e.enrolled_at,
               COALESCE(p.percentage, 0) as progress,
               u.full_name,
               EXTRACT(DAY FROM (NOW() - e.enrolled_at))::INTEGER as days_enrolled
        FROM enrollments e
        JOIN users u ON e.id = u.student_id
        LEFT JOIN progress p ON p.student_id = e.student_id AND p.module_id = e.module_id
        WHERE e.module_id IN (SELECT id FROM teacher_mods)
          AND e.status IN ('active', 'completed')
    ),
    module_avgs AS (
        SELECT module_id,
               AVG(progress) as avg_progress,
               AVG(progress / GREATEST(days_enrolled, 1)) as avg_velocity
        FROM student_data
        GROUP BY module_id
    )
    SELECT sd.student_id,
           sd.full_name::VARCHAR,
           sd.module_id,
           m.title::VARCHAR,
           CASE
               WHEN sd.days_enrolled > 7 AND sd.progress < 0.3 * ma.avg_progress THEN 'slow_learner'
               WHEN sd.days_enrolled > 1 AND sd.progress > 2.0 * ma.avg_progress AND sd.progress > 50 THEN 'fast_learner'
               ELSE 'normal'
           END,
           CASE
               WHEN sd.days_enrolled > 7 AND sd.progress < 0.3 * ma.avg_progress THEN 'medium'
               WHEN sd.days_enrolled > 1 AND sd.progress > 2.0 * ma.avg_progress THEN 'low'
               ELSE 'info'
           END,
           CASE
               WHEN sd.days_enrolled > 7 AND sd.progress < 0.3 * ma.avg_progress
                    THEN 'Ritmo lento: ' || sd.full_name || ' tiene progreso bajo'
               WHEN sd.days_enrolled > 1 AND sd.progress > 2.0 * ma.avg_progress
                    THEN 'Avance rapido: ' || sd.full_name || ' completa mas rapido que el promedio'
               ELSE 'Sin alertas'
           END,
           sd.progress, sd.days_enrolled,
           ROUND(sd.progress / GREATEST(sd.days_enrolled, 1), 2),
           ROUND(ma.avg_velocity, 2)
    FROM student_data sd
    JOIN module_avgs ma ON ma.module_id = sd.module_id
    JOIN modules m ON m.id = sd.module_id
    WHERE (sd.days_enrolled > 7 AND sd.progress < 0.3 * ma.avg_progress)
       OR (sd.days_enrolled > 1 AND sd.progress > 2.0 * ma.avg_velocity AND sd.progress > 50);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PROCEDURE: sp_award_points
-- Otorga puntos a un usuario de forma segura
-- ============================================

CREATE OR REPLACE FUNCTION sp_award_points(
    p_user_id INTEGER,
    p_points INTEGER,
    p_reason VARCHAR DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_new_points INTEGER;
BEGIN
    UPDATE users SET points = COALESCE(points, 0) + p_points
    WHERE id = p_user_id
    RETURNING points INTO v_new_points;

    RETURN v_new_points;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PROCEDURE: sp_enroll_student
-- Inscribe a un estudiante en un modulo de forma segura
-- ============================================

CREATE OR REPLACE FUNCTION sp_enroll_student(
    p_student_id INTEGER,
    p_module_id INTEGER
) RETURNS TABLE(
    enrollment_id INTEGER,
    status VARCHAR,
    already_enrolled BOOLEAN
) AS $$
DECLARE
    v_exists INTEGER;
BEGIN
    SELECT id INTO v_exists
    FROM enrollments WHERE student_id = p_student_id AND module_id = p_module_id;

    IF v_exists IS NOT NULL THEN
        RETURN QUERY SELECT v_exists, 'active'::VARCHAR, TRUE::BOOLEAN;
        RETURN;
    END IF;

    INSERT INTO enrollments (student_id, module_id, status)
    VALUES (p_student_id, p_module_id, 'active')
    RETURNING id, 'active'::VARCHAR, FALSE::BOOLEAN;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_weekly_activity
-- Actividad semanal de estudiantes (para dashboard)
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_weekly_activity(
    p_teacher_id INTEGER
) RETURNS TABLE(
    day_name VARCHAR,
    active_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        CASE EXTRACT(DOW FROM ea.submitted_at)
            WHEN 0 THEN 'Dom' WHEN 1 THEN 'Lun' WHEN 2 THEN 'Mar'
            WHEN 3 THEN 'Mie' WHEN 4 THEN 'Jue' WHEN 5 THEN 'Vie'
            WHEN 6 THEN 'Sab'
        END::VARCHAR,
        COUNT(DISTINCT ea.student_id)::INTEGER
    FROM exercise_attempts ea
    JOIN exercises ex ON ex.id = ea.exercise_id
    JOIN modules m ON m.id = ex.module_id
    WHERE m.teacher_id = p_teacher_id
      AND ea.submitted_at >= NOW() - INTERVAL '7 days'
    GROUP BY EXTRACT(DOW FROM ea.submitted_at)
    ORDER BY EXTRACT(DOW FROM ea.submitted_at);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PROCEDURE: sp_check_and_award_achievements
-- Verifica y otorga logros automaticamente
-- ============================================

CREATE OR REPLACE FUNCTION sp_check_and_award_achievements(
    p_user_id INTEGER
) RETURNS TABLE(
    achievement_id INTEGER,
    achievement_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH eligible AS (
        SELECT a.id, a.name, a.points, a.criteria
        FROM achievements a
        WHERE NOT EXISTS (
            SELECT 1 FROM user_achievements ua
            WHERE ua.user_id = p_user_id AND ua.achievement_id = a.id
        )
    )
    SELECT e.id, e.name::VARCHAR
    FROM eligible e
    WHERE
        (e.criteria->>'type' = 'exercise_complete'
         AND (SELECT COUNT(*) FROM exercise_attempts
              WHERE student_id = p_user_id AND passed = TRUE) >= COALESCE((e.criteria->>'count')::INTEGER, 1))
        OR
        (e.criteria->>'type' = 'streak_days'
         AND (SELECT COALESCE(streak_days, 0) FROM users WHERE id = p_user_id) >= COALESCE((e.criteria->>'count')::INTEGER, 7))
        OR
        (e.criteria->>'type' = 'challenge_complete'
         AND (SELECT COUNT(*) FROM challenge_attempts
              WHERE student_id = p_user_id AND passed = TRUE) >= COALESCE((e.criteria->>'count')::INTEGER, 1))
        OR
        (e.criteria->>'type' = 'first_try'
         AND (SELECT COUNT(*) FROM (
              SELECT exercise_id FROM exercise_attempts
              WHERE student_id = p_user_id AND passed = TRUE AND attempt_count = 1
              GROUP BY exercise_id
         ) sub) >= COALESCE((e.criteria->>'count')::INTEGER, 1));

    INSERT INTO user_achievements (user_id, achievement_id)
    SELECT p_user_id, e.id
    FROM (
        SELECT a.id, a.points
        FROM achievements a
        WHERE NOT EXISTS (
            SELECT 1 FROM user_achievements ua
            WHERE ua.user_id = p_user_id AND ua.achievement_id = a.id
        )
        AND (
            (a.criteria->>'type' = 'exercise_complete'
             AND (SELECT COUNT(*) FROM exercise_attempts
                  WHERE student_id = p_user_id AND passed = TRUE) >= COALESCE((a.criteria->>'count')::INTEGER, 1))
            OR
            (a.criteria->>'type' = 'streak_days'
             AND (SELECT COALESCE(streak_days, 0) FROM users WHERE id = p_user_id) >= COALESCE((a.criteria->>'count')::INTEGER, 7))
        )
    ) e
    ON CONFLICT DO NOTHING;

    UPDATE users u SET points = COALESCE(points, 0) + e.points
    FROM (
        SELECT a.id, a.points
        FROM achievements a
        JOIN user_achievements ua ON ua.achievement_id = a.id
        WHERE ua.user_id = p_user_id AND ua.earned_at >= NOW() - INTERVAL '1 minute'
    ) e
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_student_performance_distribution
-- Distribucion de rendimiento para dashboard docente
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_student_performance_distribution(
    p_teacher_id INTEGER
) RETURNS TABLE(
    category VARCHAR,
    value INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH student_progress AS (
        SELECT p.student_id,
               AVG(p.percentage) as avg_pct
        FROM progress p
        JOIN modules m ON m.id = p.module_id
        WHERE m.teacher_id = p_teacher_id
        GROUP BY p.student_id
    )
    SELECT 'Alto (80-100%)'::VARCHAR, COUNT(*)::INTEGER FROM student_progress WHERE avg_pct >= 80
    UNION ALL
    SELECT 'Medio (40-79%)'::VARCHAR, COUNT(*)::INTEGER FROM student_progress WHERE avg_pct >= 40 AND avg_pct < 80
    UNION ALL
    SELECT 'Bajo (0-39%)'::VARCHAR, COUNT(*)::INTEGER FROM student_progress WHERE avg_pct < 40;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_get_module_detail_for_admin
-- Detalle completo de modulo para edicion admin
-- ============================================

CREATE OR REPLACE FUNCTION fn_get_module_detail_for_admin(
    p_module_id INTEGER
) RETURNS TABLE(
    module_id INTEGER,
    title VARCHAR,
    description TEXT,
    theory_content TEXT,
    teacher_id INTEGER,
    teacher_name VARCHAR,
    status VARCHAR,
    "order" INTEGER,
    is_published BOOLEAN,
    is_global BOOLEAN,
    difficulty VARCHAR,
    lesson_count INTEGER,
    created_at TIMESTAMP,
    lessons JSON,
    exercises JSON
) AS $$
BEGIN
    RETURN QUERY
    SELECT m.id, m.title, m.description, m.theory_content,
           m.teacher_id, u.full_name::VARCHAR,
           m.status, m."order", m.is_published, m.is_global,
           m.difficulty, m.lesson_count, m.created_at,
           (SELECT COALESCE(json_agg(json_build_object(
                'id', l.id, 'title', l.title, 'theory_content', l.theory_content, 'order', l."order"
            ) ORDER BY l."order"), '[]'::json)
            FROM lessons l WHERE l.module_id = m.id),
           (SELECT COALESCE(json_agg(json_build_object(
                'id', e.id, 'title', e.title, 'description', e.description,
                'instructions', e.instructions, 'difficulty', e.difficulty,
                'points', e.points, 'order', e."order",
                'solution_output', e.solution_output, 'solution_type', e.solution_type
            ) ORDER BY e."order"), '[]'::json)
            FROM exercises e WHERE e.module_id = m.id)
    FROM modules m
    LEFT JOIN users u ON m.teacher_id = u.id
    WHERE m.id = p_module_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: fn_search_users
 -- Busqueda segura de usuarios (evita inyeccion SQL)
-- ============================================

CREATE OR REPLACE FUNCTION fn_search_users(
    p_search VARCHAR DEFAULT NULL,
    p_role VARCHAR DEFAULT NULL,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0
) RETURNS TABLE(
    id INTEGER,
    email VARCHAR,
    full_name VARCHAR,
    role VARCHAR,
    is_active BOOLEAN,
    points INTEGER,
    streak_days INTEGER,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.email, u.full_name, u.role, u.is_active,
           u.points, u.streak_days, u.created_at
    FROM users u
    WHERE (p_search IS NULL OR u.full_name ILIKE '%' || p_search || '%' OR u.email ILIKE '%' || p_search || '%')
      AND (p_role IS NULL OR u.role = p_role)
    ORDER BY u.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Log de ejecucion
-- ============================================

DO $$
BEGIN
    RAISE NOTICE 'Stored procedures and functions created successfully';
END $$;
