"""Tests for aletheia.tools.reader."""

from unittest.mock import MagicMock, patch


@patch("aletheia.tools.reader.httpx")
def test_fetch_content_extracts_paragraphs(mock_httpx):
    response = MagicMock()
    response.text = "<html><body><p>Hello world.</p><p>Second paragraph.</p></body></html>"
    response.raise_for_status = MagicMock()
    mock_httpx.get.return_value = response

    from confidence_scorer.tools.reader import fetch_content
    result = fetch_content("https://example.com")

    assert "Hello world." in result
    assert "Second paragraph." in result


@patch("aletheia.tools.reader.httpx")
def test_fetch_content_caps_at_max_chars(mock_httpx):
    response = MagicMock()
    response.text = f"<html><body><p>{'A' * 5000}</p></body></html>"
    response.raise_for_status = MagicMock()
    mock_httpx.get.return_value = response

    from confidence_scorer.tools.reader import MAX_CHARS, fetch_content
    result = fetch_content("https://example.com")

    assert len(result) <= MAX_CHARS


@patch("aletheia.tools.reader.httpx")
def test_fetch_content_returns_empty_on_error(mock_httpx):
    mock_httpx.get.side_effect = Exception("connection refused")

    from confidence_scorer.tools.reader import fetch_content
    result = fetch_content("https://bad-url.example")

    assert result == ""
