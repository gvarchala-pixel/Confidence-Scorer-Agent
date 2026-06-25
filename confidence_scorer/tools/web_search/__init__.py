"""Web search package — pick a provider via WEB_SEARCH_PROVIDER in .env."""

from confidence_scorer.tools.base import BaseTool


def get_web_search_tool() -> BaseTool:
    """Return the configured web search tool. Change WEB_SEARCH_PROVIDER to swap."""
    from confidence_scorer.config import WEB_SEARCH_PROVIDER
    from confidence_scorer.tools.web_search.providers import WebSearchProvider

    if WEB_SEARCH_PROVIDER == WebSearchProvider.DUCKDUCKGO:
        from confidence_scorer.tools.web_search.duckduckgo import DuckDuckGoSearchTool
        return DuckDuckGoSearchTool()

    if WEB_SEARCH_PROVIDER == WebSearchProvider.TAVILY:
        from confidence_scorer.tools.web_search.tavily import TavilySearchTool
        return TavilySearchTool()

    if WEB_SEARCH_PROVIDER == WebSearchProvider.BRAVE:
        from confidence_scorer.tools.web_search.brave import BraveSearchTool
        return BraveSearchTool()

    if WEB_SEARCH_PROVIDER == WebSearchProvider.GOOGLE:
        from confidence_scorer.tools.web_search.google import GoogleSearchTool
        return GoogleSearchTool()

    if WEB_SEARCH_PROVIDER == WebSearchProvider.BING:
        from confidence_scorer.tools.web_search.bing import BingSearchTool
        return BingSearchTool()

    raise ValueError(f"Unknown WEB_SEARCH_PROVIDER: {WEB_SEARCH_PROVIDER}")
