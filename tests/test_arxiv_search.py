"""Tests for aletheia.tools.arxiv_search."""

from unittest.mock import MagicMock, patch

from confidence_scorer.tools.base import Source


def _make_arxiv_result(i: int):
    r = MagicMock()
    r.entry_id = f"https://arxiv.org/abs/2401.{i:05d}"
    r.title = f"Paper {i}"
    r.summary = f"Abstract {i}"
    return r


@patch("aletheia.tools.arxiv_search.arxiv")
def test_search_returns_sources(mock_arxiv):
    mock_client = MagicMock()
    mock_arxiv.Client.return_value = mock_client
    mock_arxiv.Search.return_value = MagicMock()
    mock_client.results.return_value = [_make_arxiv_result(1), _make_arxiv_result(2)]

    from confidence_scorer.tools.arxiv_search import ArxivSearchTool
    tool = ArxivSearchTool()
    results = tool.search("quantum computing")

    assert len(results) == 2
    assert all(isinstance(r, Source) for r in results)
    assert results[0].source_type == "arxiv"
    assert results[0].url == "https://arxiv.org/abs/2401.00001"
    assert results[0].content == "Abstract 1"


@patch("aletheia.tools.arxiv_search.arxiv")
def test_search_caps_at_five_results(mock_arxiv):
    mock_client = MagicMock()
    mock_arxiv.Client.return_value = mock_client
    mock_arxiv.Search.return_value = MagicMock()
    mock_client.results.return_value = [_make_arxiv_result(i) for i in range(10)]

    from confidence_scorer.tools.arxiv_search import ArxivSearchTool
    tool = ArxivSearchTool()
    results = tool.search("test")

    assert len(results) == 5


@patch("aletheia.tools.arxiv_search.arxiv")
def test_search_returns_empty_on_error(mock_arxiv):
    mock_client = MagicMock()
    mock_arxiv.Client.return_value = mock_client
    mock_arxiv.Search.return_value = MagicMock()
    mock_client.results.side_effect = RuntimeError("network error")

    from confidence_scorer.tools.arxiv_search import ArxivSearchTool
    tool = ArxivSearchTool()
    results = tool.search("test")

    assert results == []
