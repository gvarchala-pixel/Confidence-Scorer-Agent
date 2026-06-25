"""Enum of supported web search providers."""

from enum import Enum


class WebSearchProvider(str, Enum):
    DUCKDUCKGO = "duckduckgo"
    TAVILY = "tavily"
    BRAVE = "brave"
    GOOGLE = "google"
    BING = "bing"
