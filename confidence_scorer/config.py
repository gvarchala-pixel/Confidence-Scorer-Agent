"""Configuration loaded from environment variables / .env file."""

import os
from dotenv import load_dotenv

from confidence_scorer.llm.models import LLMConfig, LLMProvider

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
# Set LLM_PROVIDER to "ollama", "openai", or "anthropic" in your .env file.
# The matching API key / base URL must also be set.

_provider_str = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_PROVIDER = LLMProvider(_provider_str)

LLM_CONFIG = LLMConfig(
    provider=LLM_PROVIDER,
    model=os.getenv("LLM_MODEL", "llama3.2"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
)

# ── Web search ───────────────────────────────────────────────────────────────
# Set WEB_SEARCH_PROVIDER to: duckduckgo | tavily | brave | google | bing
from confidence_scorer.tools.web_search.providers import WebSearchProvider

WEB_SEARCH_PROVIDER = WebSearchProvider(
    os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo").lower()
)

# Provider API keys — only the one matching WEB_SEARCH_PROVIDER needs to be set
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
BING_API_KEY = os.getenv("BING_API_KEY")
