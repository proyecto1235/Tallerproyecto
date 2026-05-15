-- Robolearn Database Schema
-- PostgreSQL tables creation script

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

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================
-- Modules Table
-- ============================================

CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    theory_content TEXT,
    teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'draft',
    "order" INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_global BOOLEAN DEFAULT FALSE,
    difficulty VARCHAR(50) DEFAULT 'Principiante',
    lesson_count INTEGER DEFAULT 0,
    CONSTRAINT valid_status CHECK (status IN ('draft', 'pending_review', 'approved', 'rejected', 'pending_deletion'))
);

CREATE INDEX IF NOT EXISTS idx_modules_teacher_id ON modules(teacher_id);
CREATE INDEX IF NOT EXISTS idx_modules_is_published ON modules(is_published);

-- ============================================
-- Lessons Table (for global module lessons)
-- ============================================

CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    theory_content TEXT,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_lessons_module_id ON lessons(module_id);

-- ============================================
-- Exercises Table (with solution columns)
-- ============================================

CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    theory_content TEXT,
    instructions TEXT,
    difficulty INTEGER CHECK (difficulty >= 1 AND difficulty <= 5),
    points INTEGER DEFAULT 100,
    solution_output TEXT,
    solution_type VARCHAR(20) DEFAULT 'output',
    test_code TEXT,
    "order" INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exercises_module_id ON exercises(module_id);
CREATE INDEX IF NOT EXISTS idx_exercises_lesson_id ON exercises(lesson_id);

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

CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_module_id ON enrollments(module_id);

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

CREATE INDEX IF NOT EXISTS idx_progress_student_id ON progress(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_module_id ON progress(module_id);

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

CREATE INDEX IF NOT EXISTS idx_attempts_student_id ON exercise_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_exercise_id ON exercise_attempts(exercise_id);

-- ============================================
-- Lesson Completions Table
-- ============================================

CREATE TABLE IF NOT EXISTS lesson_completions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, lesson_id)
);

CREATE INDEX IF NOT EXISTS idx_lesson_completions_student ON lesson_completions(student_id);
CREATE INDEX IF NOT EXISTS idx_lesson_completions_module ON lesson_completions(module_id);

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

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON chatbot_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON chatbot_sessions(session_id);

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
-- Challenges Table (with solution columns)
-- ============================================

CREATE TABLE IF NOT EXISTS challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    difficulty INTEGER CHECK (difficulty >= 1 AND difficulty <= 5),
    points INTEGER DEFAULT 100,
    teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    base_code TEXT DEFAULT '',
    solution_code TEXT,
    solution_type VARCHAR(20) DEFAULT 'output',
    solution_output TEXT,
    test_code TEXT,
    deadline TIMESTAMP,
    is_published BOOLEAN DEFAULT FALSE,
    max_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_challenges_teacher_id ON challenges(teacher_id);

-- ============================================
-- Challenge Attempts Table
-- ============================================

CREATE TABLE IF NOT EXISTS challenge_attempts (
    id SERIAL PRIMARY KEY,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    passed BOOLEAN DEFAULT FALSE,
    score NUMERIC(5, 2) DEFAULT 0,
    attempt_count INTEGER DEFAULT 1,
    submitted_code TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(challenge_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_challenge_attempts_challenge ON challenge_attempts(challenge_id);
CREATE INDEX IF NOT EXISTS idx_challenge_attempts_student ON challenge_attempts(student_id);

-- ============================================
-- Achievements Table
-- ============================================

CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(255),
    points INTEGER DEFAULT 0,
    criteria JSONB
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_id)
);

CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id);

-- ============================================
-- Classes Table (teacher-created courses)
-- ============================================

CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    difficulty VARCHAR(50),
    teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cover_image VARCHAR(500),
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_classes_teacher_id ON classes(teacher_id);

-- ============================================
-- Class Modules Table
-- ============================================

CREATE TABLE IF NOT EXISTS class_modules (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    theory_content TEXT,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_class_modules_class_id ON class_modules(class_id);

-- ============================================
-- Class Exercises Table (with solution columns)
-- ============================================

CREATE TABLE IF NOT EXISTS class_exercises (
    id SERIAL PRIMARY KEY,
    class_module_id INTEGER NOT NULL REFERENCES class_modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    exercise_type VARCHAR(50) DEFAULT 'coding',
    difficulty INTEGER DEFAULT 1,
    points INTEGER DEFAULT 10,
    solution_output TEXT,
    solution_type VARCHAR(20) DEFAULT 'output',
    test_code TEXT,
    "order" INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_class_exercises_module ON class_exercises(class_module_id);

-- ============================================
-- Class Enrollments (with teacher approval)
-- ============================================

CREATE TABLE IF NOT EXISTS class_enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    UNIQUE(student_id, class_id),
    CONSTRAINT valid_ce_status CHECK (status IN ('pending', 'approved', 'rejected', 'withdrawn'))
);

CREATE INDEX IF NOT EXISTS idx_ce_student_id ON class_enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_ce_class_id ON class_enrollments(class_id);
