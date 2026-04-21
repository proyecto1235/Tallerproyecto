-- Datos iniciales para la plataforma

-- Usuario administrador por defecto (password: admin123)
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@codekids.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Administrador Sistema', 'admin');

-- Logros disponibles
INSERT INTO achievements (name, description, icon, points, criteria) VALUES
('Primer Paso', 'Completa tu primera lección', 'footprints', 10, '{"lessons_completed": 1}'),
('Explorador', 'Completa 5 lecciones', 'compass', 25, '{"lessons_completed": 5}'),
('Estudiante Dedicado', 'Completa 20 lecciones', 'book-open', 50, '{"lessons_completed": 20}'),
('Racha de 7 días', 'Mantén una racha de 7 días', 'flame', 30, '{"streak_days": 7}'),
('Racha de 30 días', 'Mantén una racha de 30 días', 'fire', 100, '{"streak_days": 30}'),
('Primer Ejercicio', 'Resuelve tu primer ejercicio correctamente', 'check-circle', 10, '{"exercises_correct": 1}'),
('Solucionador', 'Resuelve 10 ejercicios correctamente', 'zap', 30, '{"exercises_correct": 10}'),
('Experto', 'Resuelve 50 ejercicios correctamente', 'award', 75, '{"exercises_correct": 50}'),
('Retador', 'Completa tu primer reto semanal', 'trophy', 50, '{"challenges_completed": 1}'),
('Campeón', 'Gana 5 retos semanales', 'crown', 150, '{"challenges_won": 5}'),
('Colaborador', 'Únete a tu primera clase', 'users', 15, '{"classes_joined": 1}'),
('Principiante Python', 'Completa el módulo de introducción a Python', 'code', 40, '{"module_completed": "intro-python"}');

-- Módulos de aprendizaje iniciales
INSERT INTO modules (title, description, difficulty_level, order_index, icon, status) VALUES
('Introducción a Python', 'Aprende los fundamentos de Python desde cero', 1, 1, 'play-circle', 'approved'),
('Variables y Tipos de Datos', 'Descubre cómo almacenar y manipular información', 1, 2, 'box', 'approved'),
('Estructuras de Control', 'Aprende a tomar decisiones con if, elif y else', 2, 3, 'git-branch', 'approved'),
('Bucles y Repeticiones', 'Domina for y while para repetir acciones', 2, 4, 'repeat', 'approved'),
('Funciones', 'Crea bloques de código reutilizables', 3, 5, 'puzzle', 'approved'),
('Listas y Colecciones', 'Organiza datos en estructuras más complejas', 3, 6, 'list', 'approved'),
('Robótica Básica', 'Introducción a la programación de robots', 4, 7, 'cpu', 'approved');

-- Lecciones del primer módulo
INSERT INTO lessons (module_id, title, content, order_index, estimated_minutes, status) VALUES
(1, 'Qué es Python', 'Python es un lenguaje de programación fácil de aprender y muy poderoso. Es usado por empresas como Google, Netflix y NASA.', 1, 10, 'approved'),
(1, 'Tu primer programa', 'Aprende a escribir tu primer programa: print("Hola Mundo")', 2, 15, 'approved'),
(1, 'Comentarios en Python', 'Los comentarios son notas que el programador deja en el código. Python los ignora al ejecutar.', 3, 10, 'approved'),
(2, 'Variables', 'Las variables son como cajas donde guardamos información. nombre = "Juan"', 1, 15, 'approved'),
(2, 'Números enteros y decimales', 'Python puede trabajar con números enteros (int) y decimales (float)', 2, 15, 'approved'),
(2, 'Cadenas de texto', 'Las cadenas (strings) son texto entre comillas. mensaje = "Hola"', 3, 15, 'approved'),
(3, 'La sentencia if', 'If nos permite ejecutar código solo cuando una condición es verdadera', 1, 20, 'approved'),
(3, 'elif y else', 'Añade más condiciones con elif y un caso por defecto con else', 2, 20, 'approved'),
(4, 'El bucle for', 'For repite código un número determinado de veces', 1, 20, 'approved'),
(4, 'El bucle while', 'While repite código mientras una condición sea verdadera', 2, 20, 'approved');

-- Ejercicios iniciales
INSERT INTO exercises (lesson_id, title, description, initial_code, expected_output, points, difficulty, order_index, status) VALUES
(2, 'Hola Mundo', 'Escribe un programa que imprima "Hola Mundo"', '# Escribe tu código aquí\n', 'Hola Mundo', 10, 1, 1, 'approved'),
(2, 'Tu nombre', 'Modifica el programa para que imprima tu nombre', '# Imprime tu nombre\nprint("___")', NULL, 10, 1, 2, 'approved'),
(4, 'Crear una variable', 'Crea una variable llamada "edad" con el valor 12', '# Crea la variable edad\n', NULL, 15, 1, 1, 'approved'),
(5, 'Suma de números', 'Crea dos variables numéricas y muestra su suma', '# Crea dos variables y suma\na = ___\nb = ___\nprint(a + b)', NULL, 15, 1, 1, 'approved'),
(7, 'Mayor de edad', 'Escribe un programa que diga si eres mayor de edad (18+)', 'edad = 15\n# Usa if para verificar\n', NULL, 20, 2, 1, 'approved'),
(9, 'Contar hasta 5', 'Usa un bucle for para imprimir números del 1 al 5', '# Usa for para contar\n', '1\n2\n3\n4\n5', 20, 2, 1, 'approved');
