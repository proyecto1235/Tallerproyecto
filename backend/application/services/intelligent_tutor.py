from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

EMERGENCY_RESPONSE = "Lo siento, no pude procesar tu consulta en este momento. Inténtalo de nuevo."


class IntelligentTutor:
    def __init__(self, orchestrator=None, llm_tutor=None):
        self.orchestrator = orchestrator
        self.llm_tutor = llm_tutor

    def detect_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower().strip()
        greetings = ["hola", "buenos días", "buenas tardes", "hey", "saludos", "qué tal", "quiubo"]
        if any(g in msg_lower for g in greetings):
            return {"intent": "greeting", "confidence": 0.9}
        if any(w in msg_lower for w in ["pista", "ayuda", "dame una pista", "hint", "no entiendo", "stuck"]):
            return {"intent": "request_hint", "confidence": 0.85}
        if any(w in msg_lower for w in ["ejemplo", "muéstrame", "código"]):
            return {"intent": "request_example", "confidence": 0.75}
        if any(w in msg_lower for w in ["error", "fallo", "no funciona", "bug", "exception", "traceback"]):
            return {"intent": "help_error", "confidence": 0.8}
        if any(w in msg_lower for w in ["gracias", "thanks", "ok", "entendido"]):
            return {"intent": "acknowledge", "confidence": 0.9}
        if any(w in msg_lower for w in ["recomienda", "sugiere", "qué estudio", "qué módulo", "siguiente"]):
            return {"intent": "recommend", "confidence": 0.7}
        return {"intent": "general_chat", "confidence": 0.4}

    def _detect_student_level(self, profile: Optional[Dict]) -> str:
        if not profile:
            return "beginner"
        perf = profile.get("performance_score", 0)
        passed = profile.get("passed_exercises_30d", 0)
        if perf > 0.7 and passed > 20:
            return "advanced"
        elif perf > 0.4 and passed > 5:
            return "intermediate"
        return "beginner"

    def _should_adapt_to_frustration(self, profile: Optional[Dict]) -> Optional[str]:
        if profile:
            fl = profile.get("frustration_level", 0)
            if fl >= 2:
                return "high"
            elif fl == 1:
                return "medium"
        return None

    async def _call_llm(self, prompt: str) -> Optional[str]:
        if not self.llm_tutor:
            return None
        try:
            resp = await self.llm_tutor.answer_question(message=prompt, student_level="beginner")
            if resp and len(resp) > 10:
                return resp
        except Exception as e:
            logger.warning(f"[IntelligentTutor] Error llamando a LLM: {e}")
        return None

    async def generate_response(
        self,
        message: str,
        student_profile: Optional[Dict] = None,
        exercise_data: Optional[Dict] = None,
        dialogflow_result: Optional[str] = None,
    ) -> Dict[str, Any]:
        intent_data = self.detect_intent(message)
        level = self._detect_student_level(student_profile)
        frustration = self._should_adapt_to_frustration(student_profile)

        prompt_map = {
            "greeting": (
                f"Eres un tutor de programación de RoboLearn. "
                f"Saluda al estudiante (nivel {level}) de forma amigable y pregúntale "
                f"en qué tema necesita ayuda. Responde en español."
            ),
            "request_hint": (
                f"Eres un tutor de programación de RoboLearn. "
                f"El estudiante (nivel {level}) te pide una pista. "
                f"{'Se nota frustrado, sé paciente y alentador.' if frustration == 'high' else ''}"
                f"Dale una pista específica pero sin dar la solución completa. Responde en español."
            ),
            "request_example": (
                f"Eres un tutor de programación de RoboLearn. "
                f"El estudiante (nivel {level}) te pide un ejemplo de código. "
                f"Proporciona un ejemplo claro con explicación. Responde en español."
            ),
            "help_error": (
                f"Eres un tutor de programación de RoboLearn. "
                f"El estudiante (nivel {level}) tiene un error. Mensaje: '{message}'. "
                f"Ayúdale a entender y resolver el error. Responde en español."
            ),
            "acknowledge": (
                f"Eres un tutor de programación de RoboLearn. "
                f"El estudiante agradece o confirma. Responde de forma breve y amigable "
                f"ofreciendo ayuda adicional. Responde en español."
            ),
            "recommend": (
                f"Eres un tutor de programación de RoboLearn. "
                f"El estudiante (nivel {level}) pide recomendaciones de qué estudiar. "
                f"Sugiere temas o módulos adecuados a su nivel. Responde en español."
            ),
            "general_chat": (
                f"Eres un tutor de programación de RoboLearn. "
                f"El estudiante (nivel {level}) pregunta: '{message}'. "
                f"Responde de forma clara y educativa en español."
            ),
        }

        prompt = prompt_map.get(intent_data["intent"], prompt_map["general_chat"])
        response_text = await self._call_llm(prompt)

        if not response_text:
            response_text = EMERGENCY_RESPONSE

        return {
            "response": response_text,
            "source": "tutor",
            "intent": intent_data["intent"],
            "student_level": level,
        }

    async def generate_hint(self, exercise_id: int, exercise_data: Optional[Dict], student_profile: Optional[Dict]) -> str:
        level = self._detect_student_level(student_profile)
        prompt = (
            f"Eres un tutor de programación de RoboLearn. "
            f"El estudiante (nivel {level}) necesita una pista para un ejercicio. "
            f"Ejercicio: {exercise_data}. "
            f"Proporciona una pista útil sin dar la solución completa. Responde en español."
        )
        response = await self._call_llm(prompt)
        return response or EMERGENCY_RESPONSE

    async def get_student_level(self, profile: Optional[Dict]) -> str:
        return self._detect_student_level(profile)
