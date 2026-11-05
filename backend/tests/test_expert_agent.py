import pytest

from app.agents.expert_base import ExpertAgent


class FakeLLM:
    def __init__(self, response="专家分析结果"):
        self.response = response
        self.messages = None

    async def chat(self, messages, **kwargs):
        self.messages = messages
        return self.response


@pytest.mark.asyncio
async def test_expert_uses_chat_interface_and_injects_profile():
    llm = FakeLLM()
    expert = ExpertAgent(llm=llm, retriever=None)
    expert.expertise = "职业导师"
    expert.name = "career"

    result = await expert.run(
        "我应该跳槽吗？",
        {"history": [], "profile": {"background": "5 年运营"}},
    )

    assert result["analysis"] == "专家分析结果"
    assert result["expertise"] == "职业导师"
    assert llm.messages[0]["role"] == "user"
    assert "5 年运营" in llm.messages[0]["content"]
    assert not hasattr(llm, "generate")
