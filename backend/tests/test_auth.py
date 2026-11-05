from datetime import timedelta

from app.services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip():
    hashed = hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert verify_password("correct horse battery staple", hashed) is True
    assert verify_password("wrong password", hashed) is False


def test_access_token_round_trip():
    token = create_access_token(
        {"sub": "42"},
        expires_delta=timedelta(minutes=5),
    )
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"


def test_invalid_token_returns_none():
    assert decode_access_token("this-is-not-a-jwt") is None
