"""Tavily web search — best result quality, requires TAVILY_API_KEY."""

import logging
from tavily import TavilyClient

from confidence_scorer.config import TAVILY_API_KEY
from confidence_scorer.tools.base import BaseTool, Source

logger = logging.getLogger(__name__)

MAX_RESULTS = 5


class TavilySearchTool(BaseTool):
    name = "search_web"
    description = "Search the web using Tavily. Requires TAVILY_API_KEY."

    def __init__(self) -> None:
        if not TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is not set — switch to duckduckgo or add the key")
        self._client = TavilyClient(api_key=TAVILY_API_KEY)

    def search(self, query: str) -> list[Source]:
        try:
            response = self._client.search(query=query, max_results=MAX_RESULTS)
            return [
                Source(
                    url=r.get("url", ""),
                    title=r.get("title", ""),
                    content=r.get("content", ""),
                    source_type="web",
                )
                for r in response.get("results", [])[:MAX_RESULTS]
            ]
        except Exception as exc:
            logger.warning("Tavily search failed: %s", exc)
            return []
