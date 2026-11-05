import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import chat as chat_module


class FakeMentor:
    def __init__(self, response=None, error=None):
        self.response = response or {}
        self.error = error
        self.calls = []

    async def run(self, message, session_id):
        self.calls.append((message, session_id))
        if self.error:
            raise self.error
        return self.response


@pytest.fixture
def client(monkeypatch):
    app = FastAPI()
    app.include_router(chat_module.router)
    monkeypatch.setattr(
        chat_module,
        "mentor",
        FakeMentor(
            {"mentor_response": "结构化回复", "is_casual": False}
        ),
    )
    return TestClient(app)


def test_chat_returns_expected_fields(client):
    response = client.post(
        "/api/chat",
        json={"message": "我该不该转行？", "session_id": "session-1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session-1",
        "mentor_response": "结构化回复",
        "is_casual": False,
    }


def test_chat_generates_session_id_when_missing(client):
    response = client.post("/api/chat", json={"message": "  你好  "})

    assert response.status_code == 200
    session_id = response.json()["session_id"]
    uuid.UUID(session_id)  # must be a valid generated UUID
    assert chat_module.mentor.calls[0][0] == "你好"


def test_chat_rejects_missing_message(client):
    assert client.post("/api/chat", json={}).status_code == 422


def test_chat_rejects_blank_message(client):
    assert client.post("/api/chat", json={"message": "   "}).status_code == 422


def test_chat_returns_503_when_agent_pipeline_fails(monkeypatch):
    app = FastAPI()
    app.include_router(chat_module.router)
    monkeypatch.setattr(
        chat_module,
        "mentor",
        FakeMentor(error=RuntimeError("internal provider detail")),
    )

    with TestClient(app) as test_client:
        response = test_client.post("/api/chat", json={"message": "分析一下"})

    assert response.status_code == 503
    assert response.json() == {"detail": "导师服务暂时不可用，请稍后重试"}
    assert "provider" not in response.text
