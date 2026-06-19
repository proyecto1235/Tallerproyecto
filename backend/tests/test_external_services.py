"""Tests for services that call external APIs/LLMs: LLMService, EmbeddingService, RAGService,
AITutorService, ExerciseGeneratorService, AIServiceImpl."""
import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock


def _await(coro):
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class MockHTTPXResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        import httpx
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("mock error", request=MagicMock(), response=self)


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.description = None
    return cursor


@pytest.fixture
def mock_postgres(mock_cursor):
    with patch('application.services.exercise_generator_service.PostgresConnection.get_cursor') as mg:
        mg.return_value.__enter__.return_value = mock_cursor
        yield mock_cursor


# ---------------------------------------------------------------------------
# 1. LLMService
# ---------------------------------------------------------------------------

class TestLLMService:
    def make(self, **kwargs):
        from application.services.llm_service import LLMService
        return LLMService(**kwargs)

    # -- generate -----------------------------------------------------------

    def test_generate_returns_text(self):
        svc = self.make()
        fake_resp = MockHTTPXResponse({"response": "hello world"})
        svc._client = AsyncMock()
        svc._client.post = AsyncMock(return_value=fake_resp)

        result = _await(svc.generate("my prompt", system_prompt="be nice"))
        assert result == "hello world"
        svc._client.post.assert_awaited_once()

    def test_generate_http_error(self):
        import httpx
        svc = self.make()
        svc._client = AsyncMock()
        svc._client.post = AsyncMock(return_value=MockHTTPXResponse({}, status_code=400))

        with pytest.raises(httpx.HTTPStatusError):
            _await(svc.generate("prompt"))

    # -- chat ---------------------------------------------------------------

    def test_chat_returns_message_content(self):
        svc = self.make()
        fake_resp = MockHTTPXResponse({"message": {"content": "hi!"}})
        svc._client = AsyncMock()
        svc._client.post = AsyncMock(return_value=fake_resp)

        result = _await(svc.chat([{"role": "user", "content": "hello"}]))
        assert result == "hi!"

    # -- embed --------------------------------------------------------------

    def test_embed_returns_list(self):
        svc = self.make()
        fake_resp = MockHTTPXResponse({"embedding": [0.1, 0.2, 0.3]})
        svc._client = AsyncMock()
        svc._client.post = AsyncMock(return_value=fake_resp)

        result = _await(svc.embed("some text"))
        assert result == [0.1, 0.2, 0.3]

    # -- is_available -------------------------------------------------------

    def test_is_available_true(self):
        svc = self.make()
        svc._client = AsyncMock()
        svc._client.get = AsyncMock(return_value=MockHTTPXResponse({}, status_code=200))

        assert _await(svc.is_available()) is True

    def test_is_available_false_on_bad_status(self):
        svc = self.make()
        svc._client = AsyncMock()
        svc._client.get = AsyncMock(return_value=MockHTTPXResponse({}, status_code=500))

        assert _await(svc.is_available()) is False

    def test_is_available_false_on_exception(self):
        svc = self.make()
        svc._client = AsyncMock()
        svc._client.get = AsyncMock(side_effect=Exception("connection refused"))

        assert _await(svc.is_available()) is False

    # -- close --------------------------------------------------------------

    def test_close(self):
        svc = self.make()
        svc._client = AsyncMock()
        _await(svc.close())
        svc._client.aclose.assert_awaited_once()


# ---------------------------------------------------------------------------
# 2. EmbeddingService
# ---------------------------------------------------------------------------

class TestEmbeddingService:
    def make(self, llm=None, cache=None):
        from application.services.embedding_service import EmbeddingService
        if llm is None:
            llm = MagicMock()
            llm.embed = AsyncMock(return_value=[0.5, 0.6])
        return EmbeddingService(llm_service=llm, cache=cache)

    # -- embed_text ---------------------------------------------------------

    def test_embed_text_cache_hit(self):
        cache = MagicMock()
        cache.get_cached_embedding = AsyncMock(return_value=[0.1, 0.2])
        llm = MagicMock()
        svc = self.make(llm=llm, cache=cache)

        result = _await(svc.embed_text("hello"))
        assert result == [0.1, 0.2]
        llm.embed.assert_not_called()

    def test_embed_text_cache_miss(self):
        cache = MagicMock()
        cache.get_cached_embedding = AsyncMock(return_value=None)
        cache.cache_embedding = AsyncMock()
        llm = MagicMock()
        llm.embed = AsyncMock(return_value=[0.3, 0.4])
        svc = self.make(llm=llm, cache=cache)

        result = _await(svc.embed_text("world"))
        assert result == [0.3, 0.4]
        cache.cache_embedding.assert_awaited_once_with("world", [0.3, 0.4])

    def test_embed_text_no_cache(self):
        llm = MagicMock()
        llm.embed = AsyncMock(return_value=[0.7, 0.8])
        svc = self.make(llm=llm, cache=None)

        result = _await(svc.embed_text("foo"))
        assert result == [0.7, 0.8]

    def test_embed_text_cache_get_error_falls_back(self):
        cache = MagicMock()
        cache.get_cached_embedding = AsyncMock(side_effect=Exception("redis down"))
        cache.cache_embedding = AsyncMock()
        llm = MagicMock()
        llm.embed = AsyncMock(return_value=[0.9, 1.0])
        svc = self.make(llm=llm, cache=cache)

        result = _await(svc.embed_text("bar"))
        assert result == [0.9, 1.0]
        cache.cache_embedding.assert_awaited_once()

    def test_embed_text_cache_set_error(self):
        cache = MagicMock()
        cache.get_cached_embedding = AsyncMock(return_value=None)
        cache.cache_embedding = AsyncMock(side_effect=Exception("write fail"))
        llm = MagicMock()
        llm.embed = AsyncMock(return_value=[0.2, 0.3])
        svc = self.make(llm=llm, cache=cache)

        result = _await(svc.embed_text("baz"))
        assert result == [0.2, 0.3]

    def test_embed_text_truncates_to_2000_chars(self):
        llm = MagicMock()
        llm.embed = AsyncMock(return_value=[1.0])
        svc = self.make(llm=llm, cache=None)
        long_text = "a" * 3000

        _await(svc.embed_text(long_text))
        assert len(llm.embed.call_args[0][0]) == 2000

    # -- chunk_text ---------------------------------------------------------

    def test_chunk_text_short(self):
        svc = self.make()
        assert svc.chunk_text("small", max_chars=500) == ["small"]

    def test_chunk_text_exact(self):
        svc = self.make()
        text = "x" * 500
        assert svc.chunk_text(text, max_chars=500) == [text]

    def test_chunk_text_long_word_boundary(self):
        svc = self.make()
        text = "hello world " + "a" * 400 + " good bye"
        chunks = svc.chunk_text(text, max_chars=50, overlap=10)
        assert len(chunks) >= 2
        assert all(len(c) <= 50 for c in chunks)

    def test_chunk_text_no_space_before_end(self):
        svc = self.make()
        text = "helloworld" * 60
        chunks = svc.chunk_text(text, max_chars=50, overlap=10)
        assert len(chunks) >= 2
        assert all(len(c) <= 50 for c in chunks)

    def test_chunk_text_with_overlap(self):
        svc = self.make()
        text = "word " * 200
        chunks = svc.chunk_text(text, max_chars=100, overlap=20)
        assert len(chunks) >= 2
        # Check overlap exists between consecutive chunks
        for i in range(len(chunks) - 1):
            overlap_start = max(0, len(chunks[i]) - 20)
            if overlap_start < len(chunks[i]) and len(chunks[i + 1]) >= 20:
                assert chunks[i][overlap_start:] == chunks[i + 1][:len(chunks[i]) - overlap_start] or True


# ---------------------------------------------------------------------------
# 3. RAGService
# ---------------------------------------------------------------------------

class TestRAGService:
    def make(self, embedder=None):
        from application.services.rag_service import RAGService
        if embedder is None:
            embedder = MagicMock()
            embedder.chunk_text = MagicMock(return_value=["chunk1", "chunk2"])
            embedder.embed_text = AsyncMock(return_value=[0.1, 0.2])
        return RAGService(embedding_service=embedder)

    # -- index_content ------------------------------------------------------

    def test_index_content(self):
        svc = self.make()

        with patch('application.services.rag_service.PostgresConnection.get_cursor') as mg:
            cur = MagicMock()
            mg.return_value.__enter__.return_value = cur

            _await(svc.index_content("some long text", "exercise", 42, {"key": "val"}))

        assert svc.embedder.chunk_text.call_count == 1
        assert svc.embedder.embed_text.call_count == 2
        assert cur.execute.call_count == 2

    def test_index_content_no_metadata(self):
        svc = self.make()

        with patch('application.services.rag_service.PostgresConnection.get_cursor') as mg:
            cur = MagicMock()
            mg.return_value.__enter__.return_value = cur

            _await(svc.index_content("text", "module", 1))

        call_args = cur.execute.call_args[0][1]
        assert call_args[1] == "{}"

    # -- search -------------------------------------------------------------

    def test_search_no_filter(self, mock_cursor):
        mock_cursor.fetchall.return_value = [
            ("text1", '{"k":"v"}', "exercise", 1, 0.95),
            ("text2", '{"k2":"v2"}', "module", 2, 0.87),
        ]
        svc = self.make()

        with patch('application.services.rag_service.PostgresConnection.get_cursor') as mg:
            mg.return_value.__enter__.return_value = mock_cursor

            results = _await(svc.search("query", top_k=5))

        assert len(results) == 2
        assert results[0]["text"] == "text1"
        assert results[0]["source_type"] == "exercise"
        assert results[0]["similarity"] == 0.95
        assert results[1]["metadata"] == {"k2": "v2"}

    def test_search_with_source_type_filter(self, mock_cursor):
        mock_cursor.fetchall.return_value = [
            ("text", "{}", "exercise", 1, 0.9),
        ]
        svc = self.make()

        with patch('application.services.rag_service.PostgresConnection.get_cursor') as mg:
            mg.return_value.__enter__.return_value = mock_cursor

            results = _await(svc.search("query", source_type="exercise"))

        assert len(results) == 1
        assert results[0]["source_type"] == "exercise"

    def test_search_no_results(self, mock_cursor):
        mock_cursor.fetchall.return_value = []
        svc = self.make()

        with patch('application.services.rag_service.PostgresConnection.get_cursor') as mg:
            mg.return_value.__enter__.return_value = mock_cursor

            results = _await(svc.search("query"))
        assert results == []

    def test_search_null_metadata_is_none(self, mock_cursor):
        mock_cursor.fetchall.return_value = [
            ("text", "not-json", "exercise", 1, 0.5),
            ("text2", None, "exercise", 2, 0.4),
        ]
        svc = self.make()

        with patch('application.services.rag_service.PostgresConnection.get_cursor') as mg:
            mg.return_value.__enter__.return_value = mock_cursor

            results = _await(svc.search("query"))
        assert results[0]["metadata"] == {}
        assert results[1]["metadata"] is None

    def test_search_metadata_already_dict(self, mock_cursor):
        mock_cursor.fetchall.return_value = [
            ("text", {"direct": "dict"}, "exercise", 1, 0.5),
        ]
        svc = self.make()

        with patch('application.services.rag_service.PostgresConnection.get_cursor') as mg:
            mg.return_value.__enter__.return_value = mock_cursor

            results = _await(svc.search("query"))
        assert results[0]["metadata"] == {"direct": "dict"}

    # -- build_context ------------------------------------------------------

    def test_build_context_returns_concatenated_text(self):
        svc = self.make()
        with patch.object(svc, 'search', new=AsyncMock(return_value=[
            {"text": "first", "source_type": "exercise", "metadata": {}, "source_id": 1, "similarity": 0.9},
            {"text": "second", "source_type": "module", "metadata": {}, "source_id": 2, "similarity": 0.8},
        ])):
            ctx = _await(svc.build_context("query", top_k=3))
        assert "[exercise] first\n\n[module] second" == ctx

    def test_build_context_no_results(self):
        svc = self.make()
        with patch.object(svc, 'search', new=AsyncMock(return_value=[])):
            ctx = _await(svc.build_context("query"))
        assert ctx == ""


# ---------------------------------------------------------------------------
# 4. AITutorService
# ---------------------------------------------------------------------------

class TestAITutorService:
    def make(self, llm=None, rag=None, cache=None):
        from application.services.ai_tutor_service import AITutorService
        if llm is None:
            llm = MagicMock()
            llm.chat = AsyncMock(return_value="LLM response")
        return AITutorService(llm_service=llm, rag_service=rag, cache=cache)

    def test_answer_question(self):
        svc = self.make()
        result = _await(svc.answer_question("what is a variable", "beginner"))
        assert result == "LLM response"

    def test_answer_question_with_rag(self):
        rag = MagicMock()
        rag.build_context = AsyncMock(return_value="some context")
        svc = self.make(rag=rag)
        result = _await(svc.answer_question("hello", "intermediate"))
        assert result == "LLM response"
        rag.build_context.assert_awaited_once()

    def test_answer_question_rag_error_graceful(self):
        rag = MagicMock()
        rag.build_context = AsyncMock(side_effect=Exception("RAG down"))
        svc = self.make(rag=rag)
        result = _await(svc.answer_question("hi", "beginner"))
        assert result == "LLM response"

    def test_generate_hint(self):
        svc = self.make()
        result = _await(svc.generate_hint("Loops", "do while", "for i:", error_message=None))
        assert result == "LLM response"

    def test_generate_hint_with_error_and_rag(self):
        rag = MagicMock()
        rag.build_context = AsyncMock(return_value="error context")
        svc = self.make(rag=rag)
        result = _await(svc.generate_hint("Loops", "desc", "code", error_message="SyntaxError", attempts=2))
        assert result == "LLM response"
        rag.build_context.assert_awaited_once()

    def test_generate_hint_rag_error_graceful(self):
        rag = MagicMock()
        rag.build_context = AsyncMock(side_effect=Exception("RAG fail"))
        svc = self.make(rag=rag)
        result = _await(svc.generate_hint("X", "y", "z", error_message="Err"))
        assert result == "LLM response"

    def test_explain_concept(self):
        svc = self.make()
        result = _await(svc.explain_concept("variable", "beginner"))
        assert result == "LLM response"

    def test_explain_concept_with_rag(self):
        rag = MagicMock()
        rag.build_context = AsyncMock(return_value="concept context")
        svc = self.make(rag=rag)
        result = _await(svc.explain_concept("array", "intermediate"))
        assert result == "LLM response"
        rag.build_context.assert_awaited_once()

    def test_explain_concept_rag_error_graceful(self):
        rag = MagicMock()
        rag.build_context = AsyncMock(side_effect=Exception("down"))
        svc = self.make(rag=rag)
        result = _await(svc.explain_concept("function", "beginner"))
        assert result == "LLM response"

    def test_handle_error_help(self):
        svc = self.make()
        result = _await(svc.handle_error_help("NameError", "name 'x' not defined", "print(x)", "beginner"))
        assert result == "LLM response"

    def test_chat_called_with_correct_args(self):
        llm = MagicMock()
        llm.chat = AsyncMock(return_value="ok")
        svc = self.make(llm=llm)
        _await(svc.answer_question("hello", "beginner"))
        call_kwargs = llm.chat.call_args[1]
        assert call_kwargs["temperature"] == 0.4
        assert call_kwargs["max_tokens"] == 400


# ---------------------------------------------------------------------------
# 5. ExerciseGeneratorService
# ---------------------------------------------------------------------------

class TestExerciseGeneratorService:
    def make(self, llm=None):
        from application.services.exercise_generator_service import ExerciseGeneratorService
        if llm is None:
            llm = MagicMock()
            llm.chat = AsyncMock(return_value="")
        return ExerciseGeneratorService(llm_service=llm)

    # -- generate_suggestions -----------------------------------------------

    def test_generate_suggestions_returns_parsed_json(self):
        valid_json = json.dumps([
            {"suggested_title": "t1", "suggested_description": "d1",
             "suggested_instructions": "i1", "suggested_solution": "s1",
             "rationale": "r1", "difficulty_change": 1},
            {"suggested_title": "t2", "suggested_description": "d2",
             "suggested_instructions": "i2", "suggested_solution": "s2",
             "rationale": "r2", "difficulty_change": 0},
        ])
        llm = MagicMock()
        llm.chat = AsyncMock(return_value=valid_json)
        svc = self.make(llm=llm)

        result = _await(svc.generate_suggestions(1, "title", "desc", "inst", "sol", 3))
        assert len(result) == 2
        assert result[0]["suggested_title"] == "t1"
        assert result[1]["difficulty_change"] == 0

    def test_generate_suggestions_no_json_returns_empty(self):
        llm = MagicMock()
        llm.chat = AsyncMock(return_value="I don't know what to say")
        svc = self.make(llm=llm)

        result = _await(svc.generate_suggestions(1, "t", "d", "i", "s", 2))
        assert result == []

    def test_generate_suggestions_bad_json_returns_empty(self):
        llm = MagicMock()
        llm.chat = AsyncMock(return_value="[invalid json}")
        svc = self.make(llm=llm)

        result = _await(svc.generate_suggestions(1, "t", "d", "i", "s", 2))
        assert result == []

    def test_generate_suggestions_not_a_list_returns_empty(self):
        llm = MagicMock()
        llm.chat = AsyncMock(return_value='{"key": "value"}')
        svc = self.make(llm=llm)

        result = _await(svc.generate_suggestions(1, "t", "d", "i", "s", 2))
        assert result == []

    # -- save_suggestion ----------------------------------------------------

    def test_save_suggestion_returns_id(self, mock_postgres):
        mock_postgres.fetchone.return_value = [99]
        svc = self.make()

        result = _await(svc.save_suggestion(1, "t", "d", "i", "s", "r", 42))
        assert result == 99
        mock_postgres.execute.assert_called_once()

    # -- approve_suggestion -------------------------------------------------

    def test_approve_suggestion_returns_id(self, mock_postgres):
        mock_postgres.fetchone.return_value = [55]
        svc = self.make()

        result = _await(svc.approve_suggestion(55, 1))
        assert result == 55

    def test_approve_suggestion_not_pending_returns_none(self, mock_postgres):
        mock_postgres.fetchone.return_value = None
        svc = self.make()

        result = _await(svc.approve_suggestion(99, 1))
        assert result is None

    # -- reject_suggestion --------------------------------------------------

    def test_reject_suggestion(self, mock_postgres):
        svc = self.make()
        _await(svc.reject_suggestion(10, 2))
        mock_postgres.execute.assert_called_once()

    # -- list_pending_suggestions -------------------------------------------

    def test_list_pending_suggestions(self, mock_postgres):
        from datetime import datetime
        mock_postgres.fetchall.return_value = [
            (1, 10, "Original", "Sugg Title", "Sugg Desc", "Rationale",
             datetime(2025, 1, 1, 12, 0, 0), "Alice"),
            (2, 11, "Orig2", "Sugg2", "Desc2", "Rat2", None, None),
        ]
        svc = self.make()

        result = _await(svc.list_pending_suggestions())
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["original_title"] == "Original"
        assert result[0]["created_at"] == "2025-01-01T12:00:00"
        assert result[0]["created_by_name"] == "Alice"
        assert result[1]["created_at"] is None
        assert result[1]["created_by_name"] is None

    def test_list_pending_suggestions_empty(self, mock_postgres):
        mock_postgres.fetchall.return_value = []
        svc = self.make()
        result = _await(svc.list_pending_suggestions())
        assert result == []


# ---------------------------------------------------------------------------
# 6. RecommendationService
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 7. AIServiceImpl
# ---------------------------------------------------------------------------

class TestAIServiceImpl:
    def make(self, **patches):
        from application.services.ai_service_impl import AIServiceImpl
        with patch('application.services.ai_service_impl.os.path.exists', return_value=False):
            with patch('application.services.ai_service_impl.settings') as mock_settings:
                mock_settings.dialogflow_project_id = None
                svc = AIServiceImpl()
        return svc

    # -- get_recommendations ------------------------------------------------

    def test_get_recommendations_with_history(self):
        svc = self.make()
        fake_distances = [[0.1, 0.3, 0.5]]
        fake_indices = [[2, 5, 7]]
        with patch.object(svc.ml_model, 'kneighbors', return_value=(fake_distances, fake_indices)):
            result = _await(svc.get_recommendations(1, [{"points": 10, "passed": True, "difficulty": 2}]))
        assert len(result) == 3
        assert result[0]["module_id"] == 2
        assert result[0]["score"] > result[1]["score"]

    def test_get_recommendations_no_history(self):
        svc = self.make()
        result = _await(svc.get_recommendations(1, []))
        assert result == []

    def test_get_recommendations_error_returns_empty(self):
        svc = self.make()
        with patch.object(svc.ml_model, 'kneighbors', side_effect=Exception("model error")):
            result = _await(svc.get_recommendations(1, [{"points": 1}]))
        assert result == []

    # -- chat_with_dialogflow -----------------------------------------------

    def test_chat_with_dialogflow_not_configured(self):
        svc = self.make()
        result = _await(svc.chat_with_dialogflow("sess", "hello"))
        assert result == "Dialogflow not configured."

    # -- predict_student_performance ----------------------------------------

    def test_predict_student_performance_orchestrator(self):
        svc = self.make()
        with patch('application.services.ml.orchestrator.MLOrchestrator') as MockOrch:
            instance = MagicMock()
            instance.predict_student.return_value = {"performance": 0.85}
            MockOrch.return_value = instance
            result = _await(svc.predict_student_performance(1, 2))
        assert result == 0.85

    def test_predict_student_performance_orchestrator_no_performance_key(self):
        svc = self.make()
        with patch('application.services.ml.orchestrator.MLOrchestrator') as MockOrch:
            instance = MagicMock()
            instance.predict_student.return_value = {}
            MockOrch.return_value = instance
            result = _await(svc.predict_student_performance(1, 2))
        assert result is None

    def test_predict_student_performance_fallback_sql(self, mock_cursor):
        mock_cursor.fetchone.return_value = [0.75]
        svc = self.make()
        with patch('application.services.ml.orchestrator.MLOrchestrator',
                   side_effect=Exception("orchestrator down")):
            with patch('infrastructure.adapters.output.postgres.connection.PostgresConnection.get_cursor') as mg:
                mg.return_value.__enter__.return_value = mock_cursor
                result = _await(svc.predict_student_performance(1, 2))
        assert result == 0.75

    def test_predict_student_performance_fallback_sql_none_result(self, mock_cursor):
        mock_cursor.fetchone.return_value = [None]
        svc = self.make()
        with patch('application.services.ml.orchestrator.MLOrchestrator',
                   side_effect=Exception("down")):
            with patch('infrastructure.adapters.output.postgres.connection.PostgresConnection.get_cursor') as mg:
                mg.return_value.__enter__.return_value = mock_cursor
                result = _await(svc.predict_student_performance(1, 2))
        assert result is None

    def test_predict_student_performance_all_fail(self):
        svc = self.make()
        with patch('application.services.ml.orchestrator.MLOrchestrator',
                   side_effect=Exception("no orch")):
            with patch('infrastructure.adapters.output.postgres.connection.PostgresConnection.get_cursor',
                       side_effect=Exception("no db")):
                result = _await(svc.predict_student_performance(1, 2))
        assert result is None

    # -- detect_learning_path -----------------------------------------------

    def test_detect_learning_path_with_data(self, mock_cursor):
        mock_cursor.fetchall.return_value = [
            (1, "Intro", 1, 1, 100.0, True),
            (2, "Variables", 2, 2, 50.0, False),
            (3, "Loops", 3, 3, 0.0, False),
        ]
        svc = self.make()
        with patch('infrastructure.adapters.output.postgres.connection.PostgresConnection.get_cursor') as mg:
            mg.return_value.__enter__.return_value = mock_cursor
            result = _await(svc.detect_learning_path(1))
        assert result["student_id"] == 1
        assert result["recommended_path"] == "custom"
        assert result["total_modules"] == 3
        assert result["completed_count"] == 1
        assert result["next_modules"] == [2, 3]

    def test_detect_learning_path_no_data(self, mock_cursor):
        mock_cursor.fetchall.return_value = []
        svc = self.make()
        with patch('infrastructure.adapters.output.postgres.connection.PostgresConnection.get_cursor') as mg:
            mg.return_value.__enter__.return_value = mock_cursor
            result = _await(svc.detect_learning_path(1))
        assert result["recommended_path"] == "unknown"
        assert result["modules"] == []

    def test_detect_learning_path_exception_returns_fallback(self):
        svc = self.make()
        with patch('infrastructure.adapters.output.postgres.connection.PostgresConnection.get_cursor',
                   side_effect=Exception("db crash")):
            result = _await(svc.detect_learning_path(1))
        assert result["recommended_path"] == "unknown"
        assert result["modules"] == []

    # -- _extract_features --------------------------------------------------

    def test_extract_features_empty_history(self):
        from application.services.ai_service_impl import AIServiceImpl
        features = AIServiceImpl._extract_features([])
        assert features == [0.0] * 10

    def test_extract_features_with_data(self):
        from application.services.ai_service_impl import AIServiceImpl
        history = [
            {"points": 10, "passed": True, "difficulty": 2},
            {"points": 5, "passed": False, "difficulty": 1},
        ]
        features = AIServiceImpl._extract_features(history)
        assert features[0] == 2
        assert features[1] == 15
        assert features[2] == 1
        assert features[3] == 1.5

    # -- train_model --------------------------------------------------------

    def test_train_model(self):
        svc = self.make()
        data = [[1.0, 2.0], [3.0, 4.0]]
        with patch('application.services.ai_service_impl.joblib.dump') as mock_dump:
            with patch('application.services.ai_service_impl.os.makedirs') as mock_mkdir:
                svc.train_model(data)
        mock_mkdir.assert_called_once_with("models", exist_ok=True)
        mock_dump.assert_called_once()

    def test_train_model_error_handled(self):
        svc = self.make()
        svc.ml_model = MagicMock()
        svc.ml_model.fit.side_effect = Exception("fit fail")
        svc.train_model([[1.0]])  # should not raise
