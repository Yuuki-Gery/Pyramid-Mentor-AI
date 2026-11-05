import pytest
from pydantic import ValidationError

from app.core.config import DEV_JWT_SECRET_KEY, Settings


def make_settings(**overrides):
    values = {
        "ENVIRONMENT": "development",
        "JWT_SECRET_KEY": "",
        "CORS_ALLOW_ORIGINS": "http://localhost:8000",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def test_development_uses_explicit_insecure_fallback():
    settings = make_settings()
    assert settings.JWT_SECRET_KEY == DEV_JWT_SECRET_KEY
    assert settings.is_production is False


def test_development_reads_explicit_secret():
    settings = make_settings(JWT_SECRET_KEY="my-local-development-secret-123456")
    assert settings.JWT_SECRET_KEY == "my-local-development-secret-123456"


def test_production_without_secret_fails_closed():
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        make_settings(ENVIRONMENT="production", JWT_SECRET_KEY="")


def test_production_rejects_development_fallback():
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        make_settings(ENVIRONMENT="production", JWT_SECRET_KEY=DEV_JWT_SECRET_KEY)


def test_production_accepts_strong_secret():
    secret = "a" * 48
    settings = make_settings(ENVIRONMENT="production", JWT_SECRET_KEY=secret)
    assert settings.is_production is True
    assert settings.JWT_SECRET_KEY == secret


def test_cors_origins_are_parsed_and_trimmed():
    settings = make_settings(
        CORS_ALLOW_ORIGINS="http://localhost:3000, https://example.com"
    )
    assert settings.cors_origins == [
        "http://localhost:3000",
        "https://example.com",
    ]


def test_wildcard_cors_origin_is_rejected():
    with pytest.raises(ValidationError, match="通配符"):
        make_settings(CORS_ALLOW_ORIGINS="*")
