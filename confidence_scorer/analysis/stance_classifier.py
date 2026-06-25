"""Classifies whether each source supports, contradicts, or is neutral on each claim."""

import logging

from confidence_scorer.agent.state import CanonicalClaim, StanceResult
from confidence_scorer.llm.gateway import LLMGateway, default_gateway
from confidence_scorer.tools.base import Source

logger = logging.getLogger(__name__)


def classify_all_stances(
    claims: list[CanonicalClaim], sources: list[Source]
) -> list[CanonicalClaim]:
    """Classify all (claim × source) pairs. Inner LLM loop — not delegated to agent."""
    gateway = default_gateway()
    for claim in claims:
        claim.stances = []
        for source in sources:
            stance = _classify_pair(gateway, claim.text, source)
            claim.stances.append(stance)
    return claims


def _classify_pair(gateway: LLMGateway, claim_text: str, source: Source) -> StanceResult:
    messages = [{"role": "user", "content": (
        f"Claim: {claim_text}\n\n"
        f"Source URL: {source.url}\n"
        f"Source content:\n{source.content}\n\n"
        "Does this source SUPPORT, CONTRADICT, or NOT ADDRESS (neutral) this claim? "
        "Provide a brief verbatim quote from the source (if applicable) and a short reasoning."
    )}]
    for attempt in range(3):
        try:
            result = gateway.structured(messages, StanceResult)
            return StanceResult(
                source_url=source.url,
                stance=result.stance,
                quote=result.quote,
                reasoning=result.reasoning,
            )
        except Exception as exc:
            logger.warning("classify_pair attempt %d for %s failed: %s", attempt + 1, source.url, exc)
    logger.warning("Defaulting to neutral stance for %s", source.url)
    return StanceResult(
        source_url=source.url,
        stance="neutral",
        quote=None,
        reasoning="Could not determine stance from source.",
    )
