"""Tests for aletheia.analysis.stance_classifier."""

from unittest.mock import MagicMock, patch

from confidence_scorer.agent.state import CanonicalClaim, StanceResult
from confidence_scorer.tools.base import Source


def _make_source(url: str, content: str = "Some content.") -> Source:
    return Source(url=url, title="Title", content=content, source_type="web")


def _make_claim(text: str = "Coffee reduces diabetes risk.") -> CanonicalClaim:
    return CanonicalClaim(text=text, stances=[], confidence=0.0)


def _mock_gateway(structured_return=None, structured_side_effect=None):
    gateway = MagicMock()
    if structured_side_effect is not None:
        gateway.structured.side_effect = structured_side_effect
    else:
        gateway.structured.return_value = structured_return
    return gateway


@patch("aletheia.analysis.stance_classifier.default_gateway")
def test_classify_all_stances_populates_stances(mock_default_gateway):
    stub = StanceResult(
        source_url="will-be-overwritten",
        stance="support",
        quote="Coffee lowers glucose.",
        reasoning="The source explicitly supports the claim.",
    )
    mock_default_gateway.return_value = _mock_gateway(structured_return=stub)

    from confidence_scorer.analysis.stance_classifier import classify_all_stances
    claims = [_make_claim()]
    sources = [_make_source("https://example.com/1"), _make_source("https://example.com/2")]

    result = classify_all_stances(claims, sources)

    assert len(result[0].stances) == 2
    assert result[0].stances[0].source_url == "https://example.com/1"
    assert result[0].stances[1].source_url == "https://example.com/2"
    assert result[0].stances[0].stance == "support"


@patch("aletheia.analysis.stance_classifier.default_gateway")
def test_classify_falls_back_to_neutral_on_persistent_failure(mock_default_gateway):
    mock_default_gateway.return_value = _mock_gateway(
        structured_side_effect=RuntimeError("structured output failed")
    )

    from confidence_scorer.analysis.stance_classifier import classify_all_stances
    result = classify_all_stances([_make_claim()], [_make_source("https://example.com/1")])

    assert result[0].stances[0].stance == "neutral"
    assert result[0].stances[0].source_url == "https://example.com/1"


@patch("aletheia.analysis.stance_classifier.default_gateway")
def test_classify_retries_before_fallback(mock_default_gateway):
    good = StanceResult(
        source_url="will-be-overwritten",
        stance="contradict",
        quote=None,
        reasoning="Contradicts.",
    )
    mock_default_gateway.return_value = _mock_gateway(
        structured_side_effect=[RuntimeError("fail"), good]
    )

    from confidence_scorer.analysis.stance_classifier import classify_all_stances
    result = classify_all_stances([_make_claim()], [_make_source("https://example.com/1")])

    assert result[0].stances[0].stance == "contradict"


@patch("aletheia.analysis.stance_classifier.default_gateway")
def test_classify_multiple_claims_and_sources(mock_default_gateway):
    stub = StanceResult(
        source_url="will-be-overwritten", stance="neutral", quote=None, reasoning="n/a"
    )
    gateway = _mock_gateway(structured_return=stub)
    mock_default_gateway.return_value = gateway

    from confidence_scorer.analysis.stance_classifier import classify_all_stances
    claims = [_make_claim("Claim A"), _make_claim("Claim B")]
    sources = [_make_source(f"https://example.com/{i}") for i in range(3)]

    result = classify_all_stances(claims, sources)

    # 2 claims × 3 sources = 6 LLM calls
    assert gateway.structured.call_count == 6
    assert len(result[0].stances) == 3
    assert len(result[1].stances) == 3
