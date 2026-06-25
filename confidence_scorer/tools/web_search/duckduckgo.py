"""DuckDuckGo web search — no API key required."""

import logging
from ddgs import DDGS

from confidence_scorer.tools.base import BaseTool, Source

logger = logging.getLogger(__name__)

MAX_RESULTS = 5


class DuckDuckGoSearchTool(BaseTool):
    name = "search_web"
    description = "Search the web using DuckDuckGo. No API key required."

    def search(self, query: str) -> list[Source]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=MAX_RESULTS))
            return [
                Source(
                    url=r.get("href", ""),
                    title=r.get("title", ""),
                    content=r.get("body", ""),
                    source_type="web",
                )
                for r in results[:MAX_RESULTS]
            ]
        except Exception as exc:
            logger.warning("DuckDuckGo search failed: %s", exc)
            return []
