"""LLM provider abstraction layer."""

from abc import ABC, abstractmethod
from typing import Optional

from django.conf import settings

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL = settings.OPENAI_MODEL
LLM_PROVIDER = settings.LLM_PROVIDER


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_model(self) -> BaseChatModel:
        """Get the language model instance."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize OpenAI provider.

        Args:
            model: Model name (default: from Config)
            api_key: OpenAI API key (default: from Config)
            temperature: Sampling temperature
        """
        self.model = model or OPENAI_MODEL
        self.api_key = api_key or OPENAI_API_KEY
        self.temperature = temperature

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    def get_model(self) -> BaseChatModel:
        """Get OpenAI model instance."""
        return ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature,
        )


def get_llm_provider(provider_name: Optional[str] = None, temperature: float = 0.7) -> LLMProvider:
    provider = provider_name or LLM_PROVIDER

    if provider == "openai":
        return OpenAIProvider(temperature=temperature)
    else:
        raise ValueError(f"Invalid provider: {provider}. Must be one of: openai")


def get_chat_model(provider_name: Optional[str] = None, temperature: float = 0.7) -> BaseChatModel:
    provider = get_llm_provider(provider_name, temperature)
    return provider.get_model()
