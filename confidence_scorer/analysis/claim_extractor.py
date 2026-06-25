"""Extracts and consolidates factual claims from retrieved sources."""

import logging
from pydantic import BaseModel

from confidence_scorer.agent.state import CanonicalClaim, RawClaim
from confidence_scorer.llm.gateway import default_gateway
from confidence_scorer.tools.base import Source

logger = logging.getLogger(__name__)


class _RawClaimList(BaseModel):
    claims: list[RawClaim]


class _CanonicalClaimList(BaseModel):
    claims: list[str]


def _sources_text(sources: list[Source]) -> str:
    parts = []
    for i, s in enumerate(sources, 1):
        parts.append(f"[Source {i}] URL: {s.url}\nTitle: {s.title}\n{s.content}")
    return "\n\n---\n\n".join(parts)


def extract_claims(sources: list[Source], query: str) -> list[RawClaim]:
    """Extract all distinct factual claims from sources in a single LLM call."""
    gateway = default_gateway()
    sources_text = _sources_text(sources)
    messages = [{"role": "user", "content": (
        f"Given the research query: '{query}'\n\n"
        "Extract all distinct factual claims made in the following sources. "
        "For each claim, record the exact source URL it came from. "
        "Focus on specific, checkable factual assertions.\n\n"
        f"{sources_text}"
    )}]
    for attempt in range(3):
        try:
            result = gateway.structured(messages, _RawClaimList)
            return result.claims
        except Exception as exc:
            logger.warning("extract_claims attempt %d failed: %s", attempt + 1, exc)
    logger.error("extract_claims failed after 3 attempts")
    return []


def consolidate_claims(raw_claims: list[RawClaim], query: str) -> list[CanonicalClaim]:
    """Group raw claims into 3-5 canonical assertions in a single LLM call."""
    gateway = default_gateway()
    claims_text = "\n".join(f"- {c.text} (from {c.source_url})" for c in raw_claims)
    messages = [{"role": "user", "content": (
        f"Research query: '{query}'\n\n"
        "Group the following extracted claims into 3-5 distinct canonical assertions, "
        "merging near-duplicates into a single representative statement. "
        "Each canonical claim should be a clear, specific, checkable factual assertion.\n\n"
        f"Claims:\n{claims_text}"
    )}]
    for attempt in range(2):
        try:
            result = gateway.structured(messages, _CanonicalClaimList)
            return [
                CanonicalClaim(text=c, stances=[], confidence=0.0)
                for c in result.claims
            ]
        except Exception as exc:
            logger.warning("consolidate_claims attempt %d failed: %s", attempt + 1, exc)
    logger.error("consolidate_claims failed after 2 attempts")
    return []
