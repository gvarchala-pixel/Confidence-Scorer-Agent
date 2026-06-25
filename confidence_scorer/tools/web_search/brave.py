"""Brave Search — free tier 2,000 queries/month. Requires BRAVE_API_KEY."""

from confidence_scorer.tools.base import BaseTool, Source


class BraveSearchTool(BaseTool):
    name = "search_web"
    description = "Search the web using Brave Search. Requires BRAVE_API_KEY."

    def search(self, query: str) -> list[Source]:
        # TODO: implement using https://api.search.brave.com/res/v1/web/search
        # Headers: {"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY}
        raise NotImplementedError("Brave Search not yet implemented")
