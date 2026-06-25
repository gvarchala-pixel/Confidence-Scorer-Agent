"""Fetch and extract readable text from a URL."""

import logging
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MAX_CHARS = 2000


def fetch_content(url: str) -> str:
    """Fetch a page and return up to MAX_CHARS of plain text from <p> tags."""
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(separator=" ", strip=True) for p in paragraphs)
        return text[:MAX_CHARS]
    except Exception as exc:
        logger.warning("fetch_content failed for %s: %s", url, exc)
        return ""
