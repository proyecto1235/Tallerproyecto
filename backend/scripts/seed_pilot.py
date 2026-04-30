from infrastructure.adapters.output.postgres.connection import PostgresConnection
from datetime import datetime

def seed():
    PostgresConnection.init_pool()
    with PostgresConnection.get_cursor() as cur:
        # Create a module
        cur.execute("""
            INSERT INTO modules (title, description, teacher_id, order, status, is_published, theory_content, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id;
        """, (
            "Python para Robótica: Nivel 1",
            "Aprende los fundamentos de Python orientados al control y automatización de robots.",
            2, # teacher id
            1,
            "approved",
            True,
            """# Introducción a la Robótica con Python
¡Bienvenido al primer módulo! Aquí aprenderemos a dar las instrucciones básicas a nuestro robot.

## ¿Por qué Python?
Python es un lenguaje muy legible y fácil de aprender, ideal para programar el "cerebro" de nuestro robot.

A continuación, intenta ejecutar tu primer código en los ejercicios de abajo.
"""
        ))
        module_id = cur.fetchone()[0]

        # Insert Exercises
        cur.execute("""
            INSERT INTO exercises (module_id, title, description, theory_content, instructions, difficulty, points, "order", created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            module_id,
            "1. Hola, Robot",
            "Tu primer programa en Python.",
            "Para comunicarte con la consola, usamos la función `print()`.",
            "Escribe `print('Hola Robot')` y ejecuta el código.",
            1,
            10,
            1
        ))

        cur.execute("""
            INSERT INTO exercises (module_id, title, description, theory_content, instructions, difficulty, points, "order", created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            module_id,
            "2. Haciendo saltar al Robot",
            "Comandos de acción directa.",
            "En nuestra librería virtual de robótica, la función `jump()` hace saltar al robot.",
            "Llama a la función `jump()` dos veces seguidas en tu código.",
            2,
            15,
            2
        ))

        # Insert a challenge
        cur.execute("""
            INSERT INTO challenges (title, description, instructions, difficulty, points, teacher_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            "Laberinto de Piedra",
            "Utiliza bucles para hacer que el robot salga del laberinto esquivando los obstáculos de piedra.",
            "El robot debe moverse 5 pasos adelante usando `forward(5)` y luego saltar un muro con `jump()`.",
            3,
            50,
            2
        ))

        cur.connection.commit()
    print("Pilot data seeded successfully.")

if __name__ == '__main__':
    seed()
