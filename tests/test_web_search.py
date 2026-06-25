"""Tests for aletheia.tools.web_search — DuckDuckGo, Tavily, and the factory."""

import pytest
from unittest.mock import MagicMock, patch

from confidence_scorer.tools.base import Source


# ── DuckDuckGo ────────────────────────────────────────────────────────────────

@patch("aletheia.tools.web_search.duckduckgo.DDGS")
def test_ddg_returns_sources(mock_ddgs_cls):
    mock_ddgs = MagicMock()
    mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
    mock_ddgs.text.return_value = [
        {"href": "https://example.com/1", "title": "Article 1", "body": "Content 1"},
        {"href": "https://example.com/2", "title": "Article 2", "body": "Content 2"},
    ]

    from confidence_scorer.tools.web_search.duckduckgo import DuckDuckGoSearchTool
    results = DuckDuckGoSearchTool().search("coffee and diabetes")

    assert len(results) == 2
    assert all(isinstance(r, Source) for r in results)
    assert results[0].url == "https://example.com/1"
    assert results[0].source_type == "web"


@patch("aletheia.tools.web_search.duckduckgo.DDGS")
def test_ddg_caps_at_five_results(mock_ddgs_cls):
    mock_ddgs = MagicMock()
    mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
    mock_ddgs.text.return_value = [
        {"href": f"https://example.com/{i}", "title": f"A{i}", "body": f"C{i}"}
        for i in range(10)
    ]

    from confidence_scorer.tools.web_search.duckduckgo import DuckDuckGoSearchTool
    results = DuckDuckGoSearchTool().search("test")

    assert len(results) == 5


@patch("aletheia.tools.web_search.duckduckgo.DDGS")
def test_ddg_returns_empty_on_error(mock_ddgs_cls):
    mock_ddgs_cls.return_value.__enter__.side_effect = RuntimeError("blocked")

    from confidence_scorer.tools.web_search.duckduckgo import DuckDuckGoSearchTool
    results = DuckDuckGoSearchTool().search("test")

    assert results == []


# ── Tavily ────────────────────────────────────────────────────────────────────

@patch("aletheia.tools.web_search.tavily.TAVILY_API_KEY", "fake-key")
@patch("aletheia.tools.web_search.tavily.TavilyClient")
def test_tavily_returns_sources(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.search.return_value = {"results": [
        {"url": "https://example.com/1", "title": "Article 1", "content": "Content 1"},
        {"url": "https://example.com/2", "title": "Article 2", "content": "Content 2"},
    ]}

    from confidence_scorer.tools.web_search.tavily import TavilySearchTool
    results = TavilySearchTool().search("coffee and diabetes")

    assert len(results) == 2
    assert results[0].source_type == "web"
    mock_client.search.assert_called_once_with(query="coffee and diabetes", max_results=5)


@patch("aletheia.tools.web_search.tavily.TAVILY_API_KEY", None)
def test_tavily_raises_without_api_key():
    from confidence_scorer.tools.web_search.tavily import TavilySearchTool
    with pytest.raises(ValueError, match="TAVILY_API_KEY"):
        TavilySearchTool()


@patch("aletheia.tools.web_search.tavily.TAVILY_API_KEY", "fake-key")
@patch("aletheia.tools.web_search.tavily.TavilyClient")
def test_tavily_returns_empty_on_api_error(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.search.side_effect = RuntimeError("API error")

    from confidence_scorer.tools.web_search.tavily import TavilySearchTool
    results = TavilySearchTool().search("test")

    assert results == []


# ── Factory ───────────────────────────────────────────────────────────────────

@patch("aletheia.tools.web_search.providers.WebSearchProvider")
def test_factory_returns_duckduckgo_by_default(mock_provider):
    from confidence_scorer.tools.web_search.providers import WebSearchProvider
    with patch("aletheia.config.WEB_SEARCH_PROVIDER", WebSearchProvider.DUCKDUCKGO):
        from confidence_scorer.tools.web_search import get_web_search_tool
        from confidence_scorer.tools.web_search.duckduckgo import DuckDuckGoSearchTool
        tool = get_web_search_tool()
        assert isinstance(tool, DuckDuckGoSearchTool)


@patch("aletheia.tools.web_search.tavily.TAVILY_API_KEY", "fake-key")
@patch("aletheia.tools.web_search.tavily.TavilyClient")
def test_factory_returns_tavily_when_configured(mock_client_cls):
    from confidence_scorer.tools.web_search.providers import WebSearchProvider
    with patch("aletheia.config.WEB_SEARCH_PROVIDER", WebSearchProvider.TAVILY):
        from confidence_scorer.tools.web_search import get_web_search_tool
        from confidence_scorer.tools.web_search.tavily import TavilySearchTool
        tool = get_web_search_tool()
        assert isinstance(tool, TavilySearchTool)
