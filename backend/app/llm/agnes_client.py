from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.llm.base import BaseLLM


class AgnesClient(BaseLLM):
    def __init__(self):
        self.model = settings.DEFAULT_MODEL
        self._client: ChatOpenAI | None = None

    @property
    def is_configured(self) -> bool:
        return bool(settings.AGNES_API_KEY.strip() and settings.AGNES_BASE_URL.strip())

    def _get_client(self) -> ChatOpenAI:
        if not self.is_configured:
            raise RuntimeError("Agnes LLM is not configured (AGNES_API_KEY/AGNES_BASE_URL)")
        if self._client is None:
            # Defer client creation until the first call so the web service can
            # start and expose health information when no API key is present.
            self._client = ChatOpenAI(
                api_key=settings.AGNES_API_KEY,
                base_url=settings.AGNES_BASE_URL,
                model=self.model,
                timeout=30,
                max_retries=1,
            )
        return self._client

    async def chat(self, messages, **kwargs):
        response = await self._get_client().ainvoke(messages, **kwargs)
        return response.content
