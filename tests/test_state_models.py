"""Tests for CanonicalClaim computed properties in aletheia.agent.state."""

from confidence_scorer.agent.state import CanonicalClaim, StanceResult


def _stance(stance: str, i: int = 0) -> StanceResult:
    return StanceResult(source_url=f"https://s{i}.com", stance=stance, reasoning="r")


def test_supports_property():
    claim = CanonicalClaim(
        text="Claim",
        stances=[_stance("support", 0), _stance("support", 1), _stance("contradict", 2)],
    )
    assert claim.supports == 2


def test_contradicts_property():
    claim = CanonicalClaim(
        text="Claim",
        stances=[_stance("support", 0), _stance("contradict", 1), _stance("contradict", 2)],
    )
    assert claim.contradicts == 2


def test_neutral_property():
    claim = CanonicalClaim(
        text="Claim",
        stances=[_stance("neutral", 0), _stance("neutral", 1), _stance("support", 2)],
    )
    assert claim.neutral == 2


def test_counts_with_no_stances():
    claim = CanonicalClaim(text="Claim", stances=[])
    assert claim.supports == 0
    assert claim.contradicts == 0
    assert claim.neutral == 0


def test_counts_sum_to_total_stances():
    stances = [
        _stance("support", 0), _stance("support", 1),
        _stance("contradict", 2),
        _stance("neutral", 3), _stance("neutral", 4),
    ]
    claim = CanonicalClaim(text="Claim", stances=stances)
    assert claim.supports + claim.contradicts + claim.neutral == len(stances)
