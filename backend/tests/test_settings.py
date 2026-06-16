"""Tests for Settings (config) - uses env vars, no DB."""
import os
import pytest


class TestSettings:
    def test_settings_defaults(self, monkeypatch):
        monkeypatch.setenv("SECRET_KEY", "test-key-12345")
        monkeypatch.setenv("POSTGRES_PASSWORD", "test-pw")
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("OLLAMA_URL", "http://localhost:11434")
        # Re-import to pick up env vars
        import importlib
        from config import settings
        importlib.reload(settings)
        from config.settings import settings
        assert settings.app_name == "Robolearn API"
        assert settings.debug is False
        assert settings.secret_key == "test-key-12345"
        assert settings.postgres_host == "localhost"

    def test_settings_env_override(self, monkeypatch):
        monkeypatch.setenv("SECRET_KEY", "custom-key")
        monkeypatch.setenv("POSTGRES_PASSWORD", "custom-pw")
        monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("OLLAMA_URL", "http://ollama:11434")
        monkeypatch.setenv("APP_NAME", "Custom API")
        monkeypatch.setenv("DEBUG", "False")
        monkeypatch.setenv("APP_ENV", "production")
        import importlib
        from config import settings
        importlib.reload(settings)
        from config.settings import settings
        assert settings.app_name == "Custom API"
        assert settings.debug is False
        assert settings.app_env == "production"
