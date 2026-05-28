from typing import Optional
from application.services.llm_service import LLMService
from infrastructure.adapters.output.postgres.connection import PostgresConnection

EXERCISE_GEN_SYSTEM_PROMPT = """Eres un asistente de creación de ejercicios de programación para una plataforma educativa.

NO debes crear ejercicios automáticamente. SOLO debes SUGERIR modificaciones y variantes.

Para cada ejercicio original, sugiere EXACTAMENTE 3 variantes que:
1. Sean progresivamente más difíciles
2. Mantengan el mismo concepto pero con una variación interesante
3. Sean diferentes entre sí en enfoque (una más práctica, otra más teórica, otra más creativa)

Para cada variante proporciona:
- Título breve
- Descripción (1-2 oraciones)
- Instrucciones detalladas
- Solución esperada (solo para el sistema, no para el estudiante)
- Justificación pedagógica (por qué esta variante es útil)

Responde en español. Formatea como JSON válido."""


class ExerciseGeneratorService:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate_suggestions(self, exercise_id: int, title: str, description: str, instructions: str, solution: str, difficulty: int) -> list[dict]:
        prompt = f"""Ejercicio original:
ID: {exercise_id}
Título: {title}
Descripción: {description}
Instrucciones: {instructions}
Solución: {solution}
Dificultad actual: {difficulty}/5

Genera 3 sugerencias de modificación/variante para este ejercicio en formato JSON.

Formato requerido (lista de objetos):
[
  {{
    "suggested_title": "título",
    "suggested_description": "descripción",
    "suggested_instructions": "instrucciones detalladas",
    "suggested_solution": "solución esperada",
    "rationale": "justificación pedagógica",
    "difficulty_change": +1 o 0 o -1
  }}
]

Asegúrate de que las instrucciones sean completas y la solución sea correcta."""
        response = await self.llm.chat([
            {"role": "system", "content": EXERCISE_GEN_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ], temperature=0.5, max_tokens=1500)

        import json
        import re

        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                suggestions = json.loads(json_match.group())
                if isinstance(suggestions, list):
                    return suggestions
            except json.JSONDecodeError:
                pass

        return []

    async def save_suggestion(self, original_exercise_id: int, suggested_title: str, suggested_description: str, suggested_instructions: str, suggested_solution: str, rationale: str, created_by: int):
        with PostgresConnection.get_cursor() as cur:
            cur.execute("""
                INSERT INTO exercise_suggestions
                    (original_exercise_id, suggested_title, suggested_description,
                     suggested_instructions, suggested_solution, rationale, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (original_exercise_id, suggested_title, suggested_description,
                  suggested_instructions, suggested_solution, rationale, created_by))
            return cur.fetchone()[0]

    async def approve_suggestion(self, suggestion_id: int, reviewed_by: int) -> Optional[int]:
        with PostgresConnection.get_cursor() as cur:
            cur.execute("""
                UPDATE exercise_suggestions
                SET status = 'approved', reviewed_at = NOW(), reviewed_by = %s
                WHERE id = %s AND status = 'pending'
                RETURNING id
            """, (reviewed_by, suggestion_id))
            row = cur.fetchone()
            return row[0] if row else None

    async def reject_suggestion(self, suggestion_id: int, reviewed_by: int):
        with PostgresConnection.get_cursor() as cur:
            cur.execute("""
                UPDATE exercise_suggestions
                SET status = 'rejected', reviewed_at = NOW(), reviewed_by = %s
                WHERE id = %s
            """, (reviewed_by, suggestion_id))

    async def list_pending_suggestions(self) -> list[dict]:
        with PostgresConnection.get_cursor() as cur:
            cur.execute("""
                SELECT es.id, es.original_exercise_id, e.title as original_title,
                       es.suggested_title, es.suggested_description, es.rationale,
                       es.created_at, u.full_name as created_by_name
                FROM exercise_suggestions es
                LEFT JOIN exercises e ON e.id = es.original_exercise_id
                LEFT JOIN users u ON u.id = es.created_by
                WHERE es.status = 'pending'
                ORDER BY es.created_at DESC
            """)
            return [
                {
                    "id": r[0], "original_exercise_id": r[1], "original_title": r[2],
                    "suggested_title": r[3], "suggested_description": r[4],
                    "rationale": r[5], "created_at": r[6].isoformat() if r[6] else None,
                    "created_by_name": r[7],
                }
                for r in cur.fetchall()
            ]
