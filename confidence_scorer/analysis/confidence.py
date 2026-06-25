"""Computes a calibrated confidence score for each claim from its stances."""

from confidence_scorer.agent.state import CanonicalClaim


def score_confidence(claims: list[CanonicalClaim]) -> list[CanonicalClaim]:
    """Set confidence on each claim using Laplace's Rule of Succession / Beta(1,1) posterior mean."""
    for claim in claims:
        s = claim.supports
        c = claim.contradicts
        # Laplace's Rule of Succession / Beta(1,1) posterior mean
        claim.confidence = (s + 1) / (s + c + 2)
        # v2: weight by source_type (arxiv > web) before computing
    return claims
