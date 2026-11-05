from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    async def chat(self, messages, **kwargs):
        """Send messages to the configured language model."""
        raise NotImplementedError

    @property
    def is_configured(self) -> bool:
        """Whether the provider has enough configuration to make a call."""
        return True
