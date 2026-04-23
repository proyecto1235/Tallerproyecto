-- Robolearn Database Schema
-- PostgreSQL initialization script

-- ============================================
-- Users Table
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    teacher_request_status VARCHAR(50),
    avatar_url VARCHAR(500),
    points INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_role CHECK (role IN ('student', 'teacher', 'admin')),
    CONSTRAINT valid_status CHECK (teacher_request_status IS NULL OR teacher_request_status IN ('pending', 'approved', 'rejected'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- Modules Table
-- ============================================

CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'draft',
    "order" INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN ('draft', 'pending_review', 'approved', 'rejected', 'pending_deletion'))
);

CREATE INDEX idx_modules_teacher_id ON modules(teacher_id);
CREATE INDEX idx_modules_is_published ON modules(is_published);

-- ============================================
-- Exercises Table
-- ============================================

CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    difficulty INTEGER CHECK (difficulty >= 1 AND difficulty <= 5),
    points INTEGER DEFAULT 100,
    "order" INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exercises_module_id ON exercises(module_id);

-- ============================================
-- Enrollments Table
-- ============================================

CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT valid_enrollment_status CHECK (status IN ('pending', 'active', 'completed', 'withdrawn')),
    UNIQUE(student_id, module_id)
);

CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_module_id ON enrollments(module_id);

-- ============================================
-- Progress Table
-- ============================================

CREATE TABLE IF NOT EXISTS progress (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    percentage NUMERIC(5, 2) DEFAULT 0,
    completed_exercises INTEGER DEFAULT 0,
    total_exercises INTEGER DEFAULT 0,
    points_earned INTEGER DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, module_id)
);

CREATE INDEX idx_progress_student_id ON progress(student_id);
CREATE INDEX idx_progress_module_id ON progress(module_id);

-- ============================================
-- Exercise Attempts Table
-- ============================================

CREATE TABLE IF NOT EXISTS exercise_attempts (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    passed BOOLEAN DEFAULT FALSE,
    score NUMERIC(5, 2),
    attempt_count INTEGER DEFAULT 1,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attempts_student_id ON exercise_attempts(student_id);
CREATE INDEX idx_attempts_exercise_id ON exercise_attempts(exercise_id);

-- ============================================
-- Chatbot Sessions Table
-- ============================================

CREATE TABLE IF NOT EXISTS chatbot_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_sessions_user_id ON chatbot_sessions(user_id);
CREATE INDEX idx_sessions_session_id ON chatbot_sessions(session_id);

-- ============================================
-- View for user statistics
-- ============================================

CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.id,
    u.email,
    u.full_name,
    COUNT(DISTINCT e.id) as total_enrollments,
    COUNT(DISTINCT CASE WHEN e.status = 'completed' THEN e.id END) as completed_modules,
    SUM(COALESCE(p.points_earned, 0)) as total_points,
    AVG(COALESCE(p.percentage, 0)) as avg_progress
FROM users u
LEFT JOIN enrollments e ON u.id = e.student_id
LEFT JOIN progress p ON u.id = p.student_id
GROUP BY u.id, u.email, u.full_name;

-- ============================================
-- Grants (if needed for specific roles)
-- ============================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO robolearn_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO robolearn_user;
