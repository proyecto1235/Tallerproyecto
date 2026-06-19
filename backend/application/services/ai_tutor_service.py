import logging
from typing import Optional
from application.services.llm_service import LLMService
from application.services.rag_service import RAGService
from infrastructure.adapters.output.redis.cache import AICache

logger = logging.getLogger(__name__)

TUTOR_SYSTEM_PROMPT = """Eres un tutor de programación de RoboLearn, una plataforma educativa para niños y jóvenes.
Siempre responde en español, con lenguaje claro, motivador y apropiado para la edad del estudiante.

REGLAS ESTRICTAS:
1. NUNCA des la solución completa al ejercicio. Da pistas, explica conceptos, señala errores.
2. Si el estudiante pide la respuesta directamente, redirige amablemente a intentarlo por sí mismo.
3. Usa analogías del mundo real para explicar conceptos difíciles.
4. Si el estudiante está frustrado, sé especialmente alentador y sugiere tomar un descanso.
5. Mantén las respuestas concisas (máximo 3 párrafos).
6. Cuando expliques un error, di QUÉ significa y CÓMO depurarlo, no la solución.
7. Si no sabes la respuesta, admite que no lo sabes y sugiere consultar al profesor."""

HINT_SYSTEM_PROMPT = """Eres un asistente de hints para ejercicios de programación.
NUNCA escribas el código completo. Da pistas progresivas.

Niveles de hint:
- Nivel 1: Señala el concepto que necesita repasar.
- Nivel 2: Da una pista sobre qué línea o parte del código revisar.
- Nivel 3: Describe el algoritmo sin escribir código.
- Nivel 4: Muestra un ejemplo similar pero no igual.

Siempre empieza por el nivel más bajo y sube solo si el estudiante lo pide."""


class AITutorService:
    def __init__(self, llm_service: LLMService, rag_service: Optional[RAGService] = None, cache: Optional[AICache] = None):
        self.llm = llm_service
        self.rag = rag_service
        self.cache = cache

    async def answer_question(self, message: str, student_level: str = "beginner", student_context: dict = None) -> str:
        rag_context = ""
        if self.rag:
            try:
                rag_context = await self.rag.build_context(message)
            except Exception as e:
                logger.warning(f"RAG no disponible para answer_question: {e}")

        context_str = ""
        if rag_context:
            context_str = f"\n\nContexto educativo disponible:\n{rag_context}"

        system = TUTOR_SYSTEM_PROMPT + f"\nNivel del estudiante: {student_level}." + context_str

        response = await self.llm.chat([
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ], temperature=0.4, max_tokens=400)

        return response

    async def generate_hint(self, exercise_title: str, exercise_desc: str, student_code: str, error_message: str = None, attempts: int = 1, student_level: str = "beginner") -> str:
        rag_context = ""
        if self.rag and error_message:
            try:
                rag_context = await self.rag.build_context(error_message, top_k=2)
            except Exception as e:
                logger.warning(f"RAG no disponible para hint: {e}")

        prompt = f"""El estudiante está resolviendo este ejercicio:
Título: {exercise_title}
Descripción: {exercise_desc}

Su código actual:
```python
{student_code}
```

{"El error que tiene es: " + error_message if error_message else "El código no produce el resultado esperado."}
Ha intentado {attempts} veces.
Nivel: {student_level}.
"""

        if rag_context:
            prompt += f"\nContexto de errores similares:\n{rag_context}"

        response = await self.llm.chat([
            {"role": "system", "content": HINT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ], temperature=0.3, max_tokens=300)

        return response

    async def explain_concept(self, concept: str, student_level: str = "beginner") -> str:
        rag_context = ""
        if self.rag:
            try:
                rag_context = await self.rag.build_context(concept, top_k=3)
            except Exception as e:
                logger.warning(f"RAG no disponible para explain_concept: {e}")

        context_str = ""
        if rag_context:
            context_str = f"\n\nMaterial de referencia:\n{rag_context}"

        prompt = f"""Explica el concepto de "{concept}" en programación a un estudiante de nivel {student_level}.

Requisitos:
- Usa una analogía del mundo real
- Da un ejemplo simple que NO sea la solución de ningún ejercicio existente
- Si el nivel es beginner, NO uses jerga técnica sin explicarla
- Máximo 2 párrafos""" + context_str

        response = await self.llm.chat([
            {"role": "system", "content": TUTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ], temperature=0.4, max_tokens=400)

        return response

    async def handle_error_help(self, error_type: str, error_message: str, student_code: str, student_level: str = "beginner") -> str:
        prompt = f"""El estudiante obtuvo este error:
Tipo: {error_type}
Mensaje: {error_message}

Código:
```python
{student_code}
```

Nivel: {student_level}

Explica:
1. Qué significa este error en términos simples
2. Qué partes del código revisar
3. Cómo depurar este tipo de error
4. NO des la solución escrita

Si es un error común, da una pista específica para resolverlo sin escribir el código."""
        response = await self.llm.chat([
            {"role": "system", "content": TUTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ], temperature=0.3, max_tokens=350)

        return response
