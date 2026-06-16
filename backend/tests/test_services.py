"""Tests for pure-logic services: IntelligentTutor, SandboxService."""
import pytest
import asyncio


def _await(coro):
    return asyncio.run(coro)


class TestSandboxService:
    def make(self):
        from application.services.sandbox_service import SandboxService
        return SandboxService()

    def test_validate_dangerous(self):
        s = self.make()
        assert s.validate_code("import os") is not None
        assert s.validate_code("eval('x')") is not None

    def test_validate_syntax_error(self):
        err = self.make().validate_code("print(")
        assert err is not None and ("sintaxis" in err.lower() or "SyntaxError" in err)

    def test_validate_clean(self):
        assert self.make().validate_code("print('hello')") is None

    def test_execute_code_validation_error(self):
        r = _await(self.make().execute_code("import os"))
        assert r["validation_error"] is True and r["exit_code"] == -1

    def test_execute_code_success(self, monkeypatch):
        s = self.make()
        async def fake_exec(self, code):
            return {"stdout": "42\n", "stderr": "", "exit_code": 0, "timed_out": False}
        monkeypatch.setattr(s, "executor", type("Fake", (), {"execute": fake_exec})())
        r = _await(s.execute_code("print(42)"))
        assert r["stdout"] == "42\n"

    def test_compare_output_match(self, monkeypatch):
        s = self.make()
        async def fake_exec(self, code):
            return {"stdout": "hello\n", "stderr": "", "exit_code": 0, "timed_out": False}
        monkeypatch.setattr(s, "executor", type("Fake", (), {"execute": fake_exec})())
        r = _await(s.execute_and_compare("print('hello')", "hello"))
        assert r["passed"] is True and r["score"] == 100.0

    def test_compare_output_no_match(self, monkeypatch):
        s = self.make()
        async def fake_exec(self, code):
            return {"stdout": "bye\n", "stderr": "", "exit_code": 0, "timed_out": False}
        monkeypatch.setattr(s, "executor", type("Fake", (), {"execute": fake_exec})())
        r = _await(s.execute_and_compare("print('bye')", "hello"))
        assert r["passed"] is False and r["score"] == 0.0

    def test_compare_validation_error(self):
        r = _await(self.make().execute_and_compare("import os", "x"))
        assert r["passed"] is False and r["score"] == 0

    def test_compare_timeout(self, monkeypatch):
        s = self.make()
        async def fake_exec(self, code):
            return {"stdout": "", "stderr": "timeout", "exit_code": -1, "timed_out": True}
        monkeypatch.setattr(s, "executor", type("Fake", (), {"execute": fake_exec})())
        r = _await(s.execute_and_compare("print(1)", "1"))
        assert r["passed"] is False and r["score"] == 0

    def test_compare_exit_code_nonzero(self, monkeypatch):
        s = self.make()
        async def fake_exec(self, code):
            return {"stdout": "", "stderr": "err", "exit_code": 1, "timed_out": False}
        monkeypatch.setattr(s, "executor", type("Fake", (), {"execute": fake_exec})())
        assert _await(s.execute_and_compare("bad code", "out"))["passed"] is False

    def test_compare_test_type(self, monkeypatch):
        s = self.make()
        async def fake_exec(self, code):
            return {"stdout": "ok\n", "stderr": "", "exit_code": 0, "timed_out": False}
        monkeypatch.setattr(s, "executor", type("Fake", (), {"execute": fake_exec})())
        r = _await(s.execute_and_compare("code", "", solution_type="test", test_code="assert True"))
        assert r["passed"] is True


class TestIntelligentTutor:
    def make(self):
        from application.services.intelligent_tutor import IntelligentTutor
        return IntelligentTutor()

    def test_detect_intent_greeting(self):
        t = self.make()
        assert t.detect_intent("hola!")["intent"] == "greeting"
        assert t.detect_intent("buenos días")["intent"] == "greeting"

    def test_detect_intent_concept(self):
        assert self.make().detect_intent("explica variable")["intent"] == "explain_concept"

    def test_detect_intent_hint(self):
        assert self.make().detect_intent("dame una pista")["intent"] == "request_hint"

    def test_detect_intent_example(self):
        assert self.make().detect_intent("muéstrame un ejemplo")["intent"] == "request_example"

    def test_detect_intent_error(self):
        assert self.make().detect_intent("tengo un error")["intent"] == "help_error"

    def test_detect_intent_acknowledge(self):
        assert self.make().detect_intent("gracias")["intent"] == "acknowledge"

    def test_detect_intent_recommend(self):
        assert self.make().detect_intent("qué estudio")["intent"] == "recommend"

    def test_detect_intent_fallback(self):
        assert self.make().detect_intent("cómo se hace un cohete")["intent"] == "general_chat"

    def test_detect_concept(self):
        assert self.make()._detect_concept("enséñame variable") == "variable"
        assert self.make()._detect_concept("qué es un for") == "bucle"

    def test_level_beginner(self):
        t = self.make()
        assert t._detect_student_level(None) == "beginner"
        assert t._detect_student_level({"performance_score": 0.3}) == "beginner"

    def test_level_intermediate(self):
        assert self.make()._detect_student_level({"performance_score": 0.5, "passed_exercises_30d": 10}) == "intermediate"

    def test_level_advanced(self):
        assert self.make()._detect_student_level({"performance_score": 0.8, "passed_exercises_30d": 30}) == "advanced"

    def test_adapted_explanation_unknown(self):
        assert "No tengo información" in self.make()._get_adapted_explanation("xyz", "beginner")

    def test_adapted_explanation_frustration(self):
        r = self.make()._get_adapted_explanation("variable", "advanced", "high")
        assert "Una variable" in r

    def test_generate_response_greeting(self):
        r = _await(self.make().generate_response("hola", {"user_id": 1, "performance_score": 0.5, "passed_exercises_30d": 10}))
        assert r["intent"] == "greeting"

    def test_generate_response_explain(self):
        r = _await(self.make().generate_response("qué es variable", {"performance_score": 0.5}))
        assert r["intent"] == "explain_concept"

    def test_generate_response_hint(self):
        r = _await(self.make().generate_response("dame una pista", {"performance_score": 0.3}))
        assert r["intent"] == "request_hint"

    def test_generate_response_example(self):
        r = _await(self.make().generate_response("muéstrame un ejemplo", {"performance_score": 0.3}))
        assert r["intent"] == "request_example"

    def test_generate_response_error_help(self):
        r = _await(self.make().generate_response("NameError", {"performance_score": 0.3}))
        assert r["intent"] == "help_error"

    def test_generate_response_acknowledge(self):
        r = _await(self.make().generate_response("gracias", {"performance_score": 0.3}))
        assert r["intent"] == "acknowledge"

    def test_generate_response_recommend(self):
        r = _await(self.make().generate_response("qué estudio", {"performance_score": 0.3}))
        assert r["intent"] == "recommend"

    def test_generate_response_fallback(self):
        r = _await(self.make().generate_response("cómo se crea un agujero", {"performance_score": 0.3}))
        assert r["intent"] == "fallback"

    def test_generate_hint(self):
        h = _await(self.make().generate_hint(1, None, {"performance_score": 0.3}))
        assert isinstance(h, str) and len(h) > 0

    def test_generate_hint_intermediate(self):
        h = _await(self.make().generate_hint(1, None, {"performance_score": 0.5, "passed_exercises_30d": 10}))
        assert isinstance(h, str)

    def test_generate_hint_advanced(self):
        h = _await(self.make().generate_hint(1, None, {"performance_score": 0.8, "passed_exercises_30d": 30}))
        assert isinstance(h, str)

    def test_get_student_level(self):
        assert _await(self.make().get_student_level({"performance_score": 0.8, "passed_exercises_30d": 30})) == "advanced"

    def test_should_adapt_to_frustration(self):
        t = self.make()
        assert t._should_adapt_to_frustration({"frustration_level": 2}) == "high"
        assert t._should_adapt_to_frustration({"frustration_level": 1}) == "medium"
        assert t._should_adapt_to_frustration({"frustration_level": 0}) is None
        assert t._should_adapt_to_frustration(None) is None

    def test_handle_error_help(self):
        assert "Depuracion" in self.make()._handle_error_help("NameError: name 'x' not defined", "beginner")

    def test_handle_error_help_unknown(self):
        r = self.make()._handle_error_help("xyz unknown", "beginner")
        assert "No tengo" not in r

    def test_greeting_frustrated(self):
        assert "dificultades" in self.make()._greeting_response("beginner", "high", "")

    def test_greeting_by_level(self):
        t = self.make()
        assert "tutor" in t._greeting_response("beginner", None, "")
        assert "avanzados" in t._greeting_response("intermediate", None, "")
        assert "experiencia" in t._greeting_response("advanced", None, "")

    def test_fallback_by_level(self):
        t = self.make()
        assert "Interesante" in t._fallback_response("beginner")
        assert "Entiendo" in t._fallback_response("intermediate")
        assert "Buena pregunta" in t._fallback_response("advanced")

    def test_recommendation_response(self):
        t = self.make()
        assert "Variables" in t._recommendation_response("beginner", None)
        assert "Funciones" in t._recommendation_response("intermediate", None)
        assert "desafíos" in t._recommendation_response("advanced", None)
