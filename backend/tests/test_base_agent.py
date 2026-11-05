import pytest

from app.agents.base_agent import BaseAgent


@pytest.fixture
def agent():
    return BaseAgent(llm=None)


def test_clean_json_plain_object(agent):
    assert agent.clean_json('{"answer": 42}') == {"answer": 42}


def test_clean_json_markdown_fence(agent):
    text = '```json\n{"problem_definition": "核心问题"}\n```'
    assert agent.clean_json(text) == {"problem_definition": "核心问题"}


def test_clean_json_with_explanation_around_it(agent):
    text = '以下是分析结果：\n{"goal": "验证"}\n希望有帮助。'
    assert agent.clean_json(text) == {"goal": "验证"}


def test_clean_json_invalid_returns_empty_dict(agent):
    assert agent.clean_json("{not valid json") == {}


def test_clean_json_empty_returns_empty_dict(agent):
    assert agent.clean_json("") == {}
    assert agent.clean_json(None) == {}


def test_fill_json_adds_only_missing_fields(agent):
    data = {"goal": "existing"}
    result = agent.fill_json(data, {"goal": "default", "skills": []})
    assert result == {"goal": "existing", "skills": []}


@pytest.mark.asyncio
async def test_safe_llm_call_returns_empty_string_on_provider_error(agent):
    class BrokenLLM:
        async def chat(self, messages):
            raise RuntimeError("provider unavailable")

    agent.llm = BrokenLLM()
    assert await agent.safe_llm_call("hello") == ""
