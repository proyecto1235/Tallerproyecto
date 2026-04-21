-- Plataforma de Aprendizaje de Programación y Robótica
-- Script de creación de tablas principales

-- Enum para roles de usuario
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');

-- Enum para estado de solicitud de docente
CREATE TYPE teacher_request_status AS ENUM ('pending', 'approved', 'rejected');

-- Enum para estado de contenido
CREATE TYPE content_status AS ENUM ('draft', 'pending_review', 'approved', 'rejected');

-- Enum para estado de inscripción
CREATE TYPE enrollment_status AS ENUM ('pending', 'approved', 'rejected', 'withdrawn');

-- Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'student',
    avatar_url TEXT,
    points INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de solicitudes de docente
CREATE TABLE teacher_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    reason TEXT,
    experience TEXT,
    status teacher_request_status DEFAULT 'pending',
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de módulos de aprendizaje
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level INTEGER DEFAULT 1,
    order_index INTEGER NOT NULL,
    parent_module_id INTEGER REFERENCES modules(id),
    icon VARCHAR(50),
    created_by INTEGER REFERENCES users(id),
    status content_status DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de lecciones
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    order_index INTEGER NOT NULL,
    estimated_minutes INTEGER DEFAULT 15,
    status content_status DEFAULT 'draft',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ejercicios
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    initial_code TEXT,
    expected_output TEXT,
    test_cases JSONB,
    hints JSONB,
    points INTEGER DEFAULT 10,
    difficulty INTEGER DEFAULT 1,
    order_index INTEGER NOT NULL,
    status content_status DEFAULT 'draft',
    created_by INTEGER REFERENCES users(id),
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de clases (grupos de docentes)
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    code VARCHAR(10) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_students INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de inscripciones a clases
CREATE TABLE class_enrollments (
    id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status enrollment_status DEFAULT 'pending',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at TIMESTAMP,
    UNIQUE(class_id, student_id)
);

-- Tabla de progreso de usuario
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    time_spent_seconds INTEGER DEFAULT 0,
    UNIQUE(user_id, lesson_id)
);

-- Tabla de intentos de ejercicios
CREATE TABLE exercise_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE CASCADE,
    submitted_code TEXT,
    is_correct BOOLEAN,
    execution_time_ms INTEGER,
    error_message TEXT,
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de retos semanales
CREATE TABLE weekly_challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    points_reward INTEGER DEFAULT 100,
    badge_reward VARCHAR(100),
    exercise_ids JSONB,
    created_by INTEGER REFERENCES users(id),
    status content_status DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de participación en retos
CREATE TABLE challenge_participations (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER REFERENCES weekly_challenges(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(challenge_id, user_id)
);

-- Tabla de logros/medallas
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    points INTEGER DEFAULT 50,
    criteria JSONB
);

-- Tabla de logros de usuarios
CREATE TABLE user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_id)
);

-- Tabla de alertas de IA para docentes
CREATE TABLE ai_alerts (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    topic VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de contenido generado por IA (pendiente de revisión)
CREATE TABLE ai_generated_content (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content JSONB NOT NULL,
    status content_status DEFAULT 'pending_review',
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_class_enrollments_student ON class_enrollments(student_id);
CREATE INDEX idx_class_enrollments_class ON class_enrollments(class_id);
CREATE INDEX idx_user_progress_user ON user_progress(user_id);
CREATE INDEX idx_exercise_attempts_user ON exercise_attempts(user_id);
CREATE INDEX idx_exercise_attempts_exercise ON exercise_attempts(exercise_id);
CREATE INDEX idx_ai_alerts_teacher ON ai_alerts(teacher_id);
CREATE INDEX idx_ai_alerts_unread ON ai_alerts(teacher_id, is_read) WHERE is_read = FALSE;
