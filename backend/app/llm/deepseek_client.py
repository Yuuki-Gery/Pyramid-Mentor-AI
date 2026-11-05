from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.llm.base import BaseLLM


class DeepSeekClient(BaseLLM):
    def __init__(self):
        self._client: ChatOpenAI | None = None

    @property
    def is_configured(self) -> bool:
        return bool(settings.DEEPSEEK_API_KEY.strip())

    def _get_client(self) -> ChatOpenAI:
        if not self.is_configured:
            raise RuntimeError("DeepSeek LLM is not configured (DEEPSEEK_API_KEY)")
        if self._client is None:
            self._client = ChatOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                model="deepseek-chat",
                timeout=30,
                max_retries=1,
            )
        return self._client

    async def chat(self, messages, **kwargs):
        response = await self._get_client().ainvoke(messages, **kwargs)
        return response.content
