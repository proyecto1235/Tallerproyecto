from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone
import re
import textwrap


class IntelligentTutor:
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self._concept_explanations = self._build_concept_map()
        self._greeting_patterns = ["hola", "buenos días", "buenas tardes", "hey", "saludos", "qué tal", "quiubo"]

    @staticmethod
    def _build_concept_map() -> Dict[str, Dict]:
        return {
            "variable": {
                "beginner": "Una variable es como una caja donde guardas información. Le pones un nombre y dentro puedes poner números, texto, o cualquier dato.",
                "intermediate": "Una variable es un identificador que referencia un espacio en memoria. En Python no necesitas declarar el tipo; se infiere automáticamente.",
                "advanced": "Las variables en Python son referencias a objetos en memoria con tipado dinámico y duck typing. El recolector de basura gestiona su ciclo de vida.",
                "example": "nombre = \"Ana\"\nedad = 15\nprint(f\"{nombre} tiene {edad} años.\")",
                "keywords": ["variable", "asignar", "declarar", "nombre", "valor"],
            },
            "funcion": {
                "beginner": "Una función es como una receta: le das ingredientes (parámetros) y sigue pasos para darte un resultado.",
                "intermediate": "Una función encapsula código reutilizable. Puede recibir argumentos y devolver valores usando 'return'.",
                "advanced": "Las funciones en Python son objetos de primera clase. Soportan closures, decoradores, argumentos *args/**kwargs y anotaciones de tipo.",
                "example": "def saludar(nombre):\n    return f\"Hola {nombre}!\"\n\nprint(saludar(\"Carlos\"))",
                "keywords": ["función", "def", "return", "parámetros", "argumentos"],
            },
            "bucle": {
                "beginner": "Un bucle permite repetir acciones varias veces. Como cuando cuentas del 1 al 10.",
                "intermediate": "Los bucles 'for' iteran sobre secuencias y 'while' se ejecutan mientras se cumpla una condición.",
                "advanced": "Comprensiones de listas y generadores ofrecen formas más eficientes de iterar. 'break' y 'continue' controlan el flujo.",
                "example": "for i in range(5):\n    print(f\"Vuelta {i+1}\")",
                "keywords": ["bucle", "for", "while", "iterar", "repetir"],
            },
            "condicional": {
                "beginner": "Un condicional permite tomar decisiones. Si pasa algo, haz una cosa; si no, haz otra.",
                "intermediate": "if/elif/else evalúan expresiones booleanas para controlar el flujo del programa.",
                "advanced": "Python usa short-circuit evaluation. Las expresiones ternarias permiten condicionales en una línea: 'x if cond else y'.",
                "example": "edad = 16\nif edad >= 18:\n    print(\"Eres mayor de edad\")\nelse:\n    print(\"Eres menor de edad\")",
                "keywords": ["condicional", "si", "if", "else", "elif", "decidir"],
            },
            "lista": {
                "beginner": "Una lista es como una mochila donde puedes guardar varios objetos en orden.",
                "intermediate": "Las listas son colecciones ordenadas y mutables. Soportan indexación, slicing, y métodos como append(), sort().",
                "advanced": "Las listas son arrays dinámicos con complejidad O(1) para acceso por índice. Soportan comprensiones y operaciones con functools.",
                "example": "frutas = [\"manzana\", \"pera\", \"uva\"]\nfrutas.append(\"naranja\")\nprint(frutas[0])",
                "keywords": ["lista", "array", "colección", "append", "elemento"],
            },
            "robotica": {
                "beginner": "En robótica, los robots siguen instrucciones paso a paso. Puedes programarlos para que avancen, giren o salten.",
                "intermediate": "Los robots usan sensores para percibir el entorno y actuadores para moverse. Se programan con secuencias de acciones.",
                "advanced": "La robótica educativa combina hardware (motores, sensores) con software. Se usan algoritmos de control como PID y navegación.",
                "example": "def avanzar(pasos):\n    for i in range(pasos):\n        forward(1)\n\navanzar(5)\njump()",
                "keywords": ["robot", "robótica", "motor", "sensor", "avanzar", "forward", "jump"],
            },
            "python": {
                "beginner": "Python es un lenguaje de programación fácil de leer. Se usa para crear programas, juegos y controlar robots.",
                "intermediate": "Python es un lenguaje interpretado, multiparadigma, con tipado dinámico y una extensa biblioteca estándar.",
                "advanced": "Python es compilado a bytecode para la VM de CPython. Soporta metaclases, descriptores, async/await y GIL.",
                "example": "print(\"Hola, mundo!\")",
                "keywords": ["python", "lenguaje", "programación", "código"],
            },
        }

    def detect_intent(self, message: str) -> Dict[str, Any]:
        msg_lower = message.lower().strip()

        if any(g in msg_lower for g in self._greeting_patterns):
            return {"intent": "greeting", "confidence": 0.9}

        concept_detected = self._detect_concept(message)
        if concept_detected:
            return {"intent": "explain_concept", "concept": concept_detected, "confidence": 0.8}

        if any(w in msg_lower for w in ["pista", "ayuda", "dame una pista", "hint", "no entiendo", "stuck"]):
            return {"intent": "request_hint", "confidence": 0.85}

        if any(w in msg_lower for w in ["ejemplo", "muéstrame", "ejercicio", "practicar", "código"]):
            return {"intent": "request_example", "confidence": 0.75}

        if any(w in msg_lower for w in ["error", "fallo", "no funciona", "bug", "exception", "traceback"]):
            return {"intent": "help_error", "confidence": 0.8}

        if any(w in msg_lower for w in ["gracias", "thanks", "ok", "entendido"]):
            return {"intent": "acknowledge", "confidence": 0.9}

        if any(w in msg_lower for w in ["recomienda", "sugiere", "qué estudio", "qué módulo", "siguiente"]):
            return {"intent": "recommend", "confidence": 0.7}

        return {"intent": "general_chat", "confidence": 0.4}

    def _detect_concept(self, message: str) -> Optional[str]:
        msg_lower = message.lower()
        for concept, info in self._concept_explanations.items():
            for kw in info["keywords"]:
                if kw in msg_lower:
                    return concept
        return None

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

    def _get_adapted_explanation(self, concept: str, level: str, frustration: Optional[str] = None) -> str:
        concept_data = self._concept_explanations.get(concept)
        if not concept_data:
            return "No tengo información sobre ese concepto aún."

        if frustration in ("high", "medium"):
            effective_level = "beginner"
        else:
            effective_level = level

        explanation = concept_data.get(effective_level, concept_data.get("beginner", ""))
        example = concept_data.get("example", "")

        response = explanation
        if example:
            response += f"\n\nEjemplo:\n```python\n{example}\n```"

        if frustration == "high":
            response += "\n\nNo te preocupes, es normal que al principio cueste. Tomalo con calma y practica paso a paso."
        elif frustration == "medium":
            response += "\n\nRecuerda que practicar es la clave. Intenta modificar el ejemplo para entenderlo mejor."

        return response

    def _generate_hint_for_exercise(self, exercise_data: Optional[Dict] = None) -> str:
        hints = [
            "Revisa bien los tipos de datos que estás usando.",
            "Descompón el problema en partes más pequeñas.",
            "Prueba con valores simples primero.",
            "¿Usaste print() para ver valores intermedios?",
            "Verifica la indentación de tu código.",
            "Asegúrate de que los nombres de variables coincidan exactamente.",
            "¿Revisaste los paréntesis y signos de puntuación?",
            "Piensa: ¿qué valor esperas obtener y qué estás obteniendo?",
        ]
        import random
        return random.choice(hints)

    def _should_adapt_to_frustration(self, profile: Optional[Dict]) -> Optional[str]:
        if profile:
            fl = profile.get("frustration_level", 0)
            if fl >= 2:
                return "high"
            elif fl == 1:
                return "medium"
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
        now = datetime.now(timezone.utc)

        if intent_data["intent"] == "greeting":
            name = ""
            if student_profile and student_profile.get("user_id"):
                name = "! "
            return {
                "response": self._greeting_response(level, frustration, name),
                "source": "tutor",
                "intent": "greeting",
                "student_level": level,
            }

        if intent_data["intent"] == "explain_concept":
            concept = intent_data["concept"]
            explanation = self._get_adapted_explanation(concept, level, frustration)
            return {
                "response": explanation,
                "source": "tutor",
                "intent": "explain_concept",
                "concept": concept,
                "student_level": level,
            }

        if intent_data["intent"] == "request_hint":
            hint = self._generate_hint_for_exercise(exercise_data)
            if frustration == "high":
                hint += "\n\n¿Quieres que te muestre un ejemplo similar resuelto?"
            return {
                "response": f"[Sugerencia] {hint}",
                "source": "tutor",
                "intent": "request_hint",
                "student_level": level,
            }

        if intent_data["intent"] == "request_example":
            return {
                "response": self._generate_dynamic_example(level, message),
                "source": "tutor",
                "intent": "request_example",
                "student_level": level,
            }

        if intent_data["intent"] == "help_error":
            return {
                "response": self._handle_error_help(message, level),
                "source": "tutor",
                "intent": "help_error",
                "student_level": level,
            }

        if intent_data["intent"] == "acknowledge":
            return {
                "response": "Me alegra haber sido util! Si tienes mas dudas, aqui estoy.",
                "source": "tutor",
                "intent": "acknowledge",
                "student_level": level,
            }

        if intent_data["intent"] == "recommend":
            return {
                "response": self._recommendation_response(level, student_profile),
                "source": "tutor",
                "intent": "recommend",
                "student_level": level,
            }

        return {
            "response": self._fallback_response(level),
            "source": "tutor",
            "intent": "fallback",
            "student_level": level,
        }

    def _greeting_response(self, level: str, frustration: Optional[str], name_suffix: str) -> str:
        if frustration == "high":
            return "Hola! Veo que estas teniendo dificultades. No te preocupes, estoy aqui para ayudarte. Sobre que tema necesitas apoyo?"
        responses = {
            "beginner": "¡Hola! Soy tu tutor de RoboLearn. Puedo explicarte conceptos de programación y robótica, darte pistas o ayudarte con ejercicios. ¿Por dónde te gusta empezar?",
            "intermediate": "¡Hola! ¿Listo para seguir aprendiendo? Puedo ayudarte con conceptos más avanzados, darte ejemplos o resolver tus dudas de código.",
            "advanced": "¡Hola! Veo que ya tienes experiencia. ¿Necesitas ayuda con algún concepto avanzado o quieres explorar nuevos temas?",
        }
        return responses.get(level, responses["beginner"])

    def _fallback_response(self, level: str) -> str:
        responses = {
            "beginner": "Interesante pregunta! ¿Podrías contarme más sobre qué necesitas? Puedo explicarte conceptos, darte ejemplos, o ayudarte con ejercicios.",
            "intermediate": "Entiendo tu consulta. ¿Puedes ser más específico? Puedo ayudarte con programación, robótica, o ejercicios prácticos.",
            "advanced": "Buena pregunta! Dime más detalles para darte una respuesta más precisa. ¿Es sobre algún concepto específico?",
        }
        return responses.get(level, responses["beginner"])

    def _generate_dynamic_example(self, level: str, message: str) -> str:
        concept = self._detect_concept(message)
        if concept and concept in self._concept_explanations:
            return f"Aquí tienes un ejemplo de {concept}:\n\n```python\n{self._concept_explanations[concept]['example']}\n```"
        examples = {
            "beginner": "Ejemplo básico:\n```python\n# Variables y print\nnombre = \"RoboLearn\"\nprint(f\"Bienvenido a {nombre}!\")\n```",
            "intermediate": "Ejemplo con función:\n```python\ndef calcular_promedio(notas):\n    return sum(notas) / len(notas)\n\nnotas = [85, 90, 78, 92]\nprint(f\"Promedio: {calcular_promedio(notas)}\")\n```",
            "advanced": "Ejemplo avanzado:\n```python\n# List comprehension con condicional\npares = [x for x in range(20) if x % 2 == 0]\ncuadrados = {x: x**2 for x in pares}\nprint(cuadrados)\n```",
        }
        return examples.get(level, examples["beginner"])

    def _handle_error_help(self, message: str, level: str) -> str:
        error_patterns = [
            (r"name.*not defined|NameError", "Esto significa que usaste una variable que no existe. Revisa que el nombre esté bien escrito y que la hayas definido antes de usarla."),
            (r"SyntaxError|invalid syntax", "Hay un error de sintaxis. Revisa que todos los paréntesis estén cerrados, los dos puntos estén donde deben, y la indentación sea correcta."),
            (r"TypeError", "Error de tipo: estás usando un tipo de dato incorrecto. Por ejemplo, sumar texto con números sin convertirlos."),
            (r"IndexError|list index out of range", "Estás intentando acceder a una posición que no existe en la lista. Recuerda que los índices empiezan en 0."),
            (r"ValueError", "Error de valor: la función recibió un valor correcto pero inapropiado. Revisa los argumentos que estás pasando."),
            (r"IndentationError", "Error de indentación. En Python, los espacios al inicio de línea son importantes. Asegúrate de que el código esté bien alineado."),
            (r"KeyError", "Estás intentando acceder a una clave que no existe en el diccionario. Verifica que la clave esté escrita correctamente."),
            (r"AttributeError", "Estás intentando usar un método o atributo que no existe en ese objeto. Revisa el tipo del objeto y sus métodos disponibles."),
        ]
        for pattern, explanation in error_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return f"[Depuracion] {explanation}\n\nQuieres que te muestre un ejemplo de como solucionarlo?"
        return "Veo que tienes un error. ¿Puedes mostrarme el código o el mensaje de error completo? Puedo ayudarte a depurarlo paso a paso."

    def _recommendation_response(self, level: str, profile: Optional[Dict]) -> str:
        recs = {
            "beginner": "Te recomiendo empezar con los módulos de Variables y Tipos de Datos, luego Condicionales y Bucles. Son la base para todo lo demás.",
            "intermediate": "Continúa con Funciones y Listas. Luego puedes explorar los conceptos de robótica básica para aplicar lo aprendido.",
            "advanced": "Prueba con los desafíos de programación y proyectos de robótica avanzada. También puedes revisar los ejercicios de clases personalizadas.",
        }
        return recs.get(level, recs["beginner"])

    async def generate_hint(self, exercise_id: int, exercise_data: Optional[Dict], student_profile: Optional[Dict]) -> str:
        level = self._detect_student_level(student_profile)
        frustration = self._should_adapt_to_frustration(student_profile)

        if level == "beginner" or frustration == "high":
            hints = [
                "Divide el problema en partes pequeñas.",
                "Primero resuelve un caso simple y luego generaliza.",
                "¿Qué información te dan? ¿Qué necesitas calcular?",
                "Escribe en papel los pasos antes de codificar.",
            ]
        elif level == "intermediate":
            hints = [
                "¿Hay una función nativa de Python que pueda ayudarte?",
                "Considera usar un bucle o comprensión de lista.",
                "¿Puedes reutilizar lo que ya escribiste?",
                "Prueba con casos borde para verificar tu lógica.",
            ]
        else:
            hints = [
                "¿Puedes resolverlo con una función recursiva?",
                "Optimiza usando algoritmos eficientes.",
                "Considera el costo computacional de tu solución.",
                "¿Hay una biblioteca estándar que facilite esto?",
            ]

        import random
        hint = random.choice(hints)
        if frustration == "high":
            hint += "\n\nTomalo con calma. Si quieres, puedo guiarte paso a paso para resolverlo."
        return hint

    async def get_student_level(self, profile: Optional[Dict]) -> str:
        return self._detect_student_level(profile)
