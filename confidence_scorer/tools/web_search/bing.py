"""Bing Web Search — free tier 1,000 queries/month via Azure. Requires BING_API_KEY."""

from confidence_scorer.tools.base import BaseTool, Source


class BingSearchTool(BaseTool):
    name = "search_web"
    description = "Search the web using Bing. Requires BING_API_KEY."

    def search(self, query: str) -> list[Source]:
        # TODO: implement using https://api.bing.microsoft.com/v7.0/search
        # Headers: {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        raise NotImplementedError("Bing Search not yet implemented")
