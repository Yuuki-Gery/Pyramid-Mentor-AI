from app.core.config import settings

from app.llm.base import BaseLLM

from app.llm.agnes_client import AgnesClient
from app.llm.openai_client import OpenAIClient
from app.llm.deepseek_client import DeepSeekClient



def get_llm() -> BaseLLM:


    provider = settings.LLM_PROVIDER.lower()


    if provider == "agnes":

        return AgnesClient()


    if provider == "openai":

        return OpenAIClient()


    if provider == "deepseek":

        return DeepSeekClient()


    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )