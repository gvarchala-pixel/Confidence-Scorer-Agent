"""Pydantic data models for the LLM client."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMConfig(BaseModel):
    """Everything the gateway needs to instantiate and call any supported LLM."""

    provider: LLMProvider
    model: str
    base_url: Optional[str] = None   # Ollama only — the local server URL
    temperature: float = 0.0         # 0 = deterministic, best for structured extraction
    max_tokens: Optional[int] = None

    @property
    def litellm_model(self) -> str:
        """Return the LiteLLM model identifier for this provider."""
        if self.provider == LLMProvider.OLLAMA:
            return f"ollama/{self.model}"
        if self.provider == LLMProvider.ANTHROPIC:
            return f"anthropic/{self.model}"
        return self.model  # OpenAI models need no prefix
