"""Google Custom Search — free tier 100 queries/day. Requires GOOGLE_API_KEY + GOOGLE_CSE_ID."""

from confidence_scorer.tools.base import BaseTool, Source


class GoogleSearchTool(BaseTool):
    name = "search_web"
    description = "Search the web using Google Custom Search. Requires GOOGLE_API_KEY and GOOGLE_CSE_ID."

    def search(self, query: str) -> list[Source]:
        # TODO: implement using https://www.googleapis.com/customsearch/v1
        # Params: key=GOOGLE_API_KEY, cx=GOOGLE_CSE_ID, q=query
        raise NotImplementedError("Google Custom Search not yet implemented")
