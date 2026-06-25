"""Tests for aletheia.analysis.confidence — pure math, no mocking needed."""

import pytest

from confidence_scorer.agent.state import CanonicalClaim, StanceResult
from confidence_scorer.analysis.confidence import score_confidence


def _claim_with_stances(supports: int, contradicts: int, neutral: int = 0) -> CanonicalClaim:
    stances = (
        [StanceResult(source_url=f"s{i}", stance="support", reasoning="r") for i in range(supports)]
        + [StanceResult(source_url=f"c{i}", stance="contradict", reasoning="r") for i in range(contradicts)]
        + [StanceResult(source_url=f"n{i}", stance="neutral", reasoning="r") for i in range(neutral)]
    )
    return CanonicalClaim(text="A claim.", stances=stances, confidence=0.0)


def test_no_evidence_gives_half():
    """0 support + 0 contradict → (0+1)/(0+0+2) = 0.5"""
    claim = _claim_with_stances(0, 0)
    [result] = score_confidence([claim])
    assert result.confidence == pytest.approx(0.5)


def test_one_support_no_contradict():
    """1 support + 0 contradict → 2/3 ≈ 0.667"""
    claim = _claim_with_stances(1, 0)
    [result] = score_confidence([claim])
    assert result.confidence == pytest.approx(2 / 3)


def test_five_support_no_contradict():
    """5 support + 0 contradict → 6/7 ≈ 0.857"""
    claim = _claim_with_stances(5, 0)
    [result] = score_confidence([claim])
    assert result.confidence == pytest.approx(6 / 7)


def test_balanced_gives_half():
    """3 support + 3 contradict → 4/8 = 0.5"""
    claim = _claim_with_stances(3, 3)
    [result] = score_confidence([claim])
    assert result.confidence == pytest.approx(0.5)


def test_strong_contradiction():
    """0 support + 5 contradict → 1/7 ≈ 0.143"""
    claim = _claim_with_stances(0, 5)
    [result] = score_confidence([claim])
    assert result.confidence == pytest.approx(1 / 7)


def test_neutral_stances_excluded_from_formula():
    """Neutral stances don't affect the score — same as 1s+0c without neutrals."""
    claim_with_neutral = _claim_with_stances(1, 0, neutral=10)
    claim_without_neutral = _claim_with_stances(1, 0, neutral=0)
    score_confidence([claim_with_neutral])
    score_confidence([claim_without_neutral])
    assert claim_with_neutral.confidence == pytest.approx(claim_without_neutral.confidence)


def test_score_confidence_updates_multiple_claims():
    claims = [
        _claim_with_stances(3, 0),   # high confidence
        _claim_with_stances(0, 3),   # low confidence
    ]
    results = score_confidence(claims)
    assert results[0].confidence > 0.7
    assert results[1].confidence < 0.4


def test_confidence_range_is_valid():
    """Confidence must always be in (0, 1)."""
    for s in range(6):
        for c in range(6):
            claim = _claim_with_stances(s, c)
            score_confidence([claim])
            assert 0.0 < claim.confidence < 1.0
