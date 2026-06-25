"""Tests for aletheia.analysis.claim_extractor."""

from unittest.mock import MagicMock, patch

from confidence_scorer.agent.state import CanonicalClaim, RawClaim
from confidence_scorer.tools.base import Source


def _make_source(i: int) -> Source:
    return Source(
        url=f"https://example.com/{i}",
        title=f"Source {i}",
        content=f"Coffee reduces diabetes risk by {i * 10}%.",
        source_type="web",
    )


def _make_raw_claim(i: int) -> RawClaim:
    return RawClaim(
        text=f"Coffee reduces diabetes risk by {i * 10}%.",
        source_url=f"https://example.com/{i}",
    )


def _mock_gateway(structured_return=None, structured_side_effect=None):
    """Return a mock LLMGateway whose .structured() is pre-configured."""
    gateway = MagicMock()
    if structured_side_effect is not None:
        gateway.structured.side_effect = structured_side_effect
    else:
        gateway.structured.return_value = structured_return
    return gateway


@patch("aletheia.analysis.claim_extractor.default_gateway")
def test_extract_claims_happy_path(mock_default_gateway):
    from confidence_scorer.analysis.claim_extractor import _RawClaimList
    expected = _RawClaimList(claims=[
        RawClaim(text="Coffee lowers blood sugar.", source_url="https://example.com/1"),
        RawClaim(text="Caffeine improves insulin sensitivity.", source_url="https://example.com/2"),
    ])
    mock_default_gateway.return_value = _mock_gateway(structured_return=expected)

    from confidence_scorer.analysis.claim_extractor import extract_claims
    result = extract_claims([_make_source(1), _make_source(2)], "Does coffee reduce diabetes risk?")

    assert len(result) == 2
    assert all(isinstance(c, RawClaim) for c in result)
    assert result[0].text == "Coffee lowers blood sugar."


@patch("aletheia.analysis.claim_extractor.default_gateway")
def test_extract_claims_retries_on_failure(mock_default_gateway):
    from confidence_scorer.analysis.claim_extractor import _RawClaimList
    success = _RawClaimList(claims=[RawClaim(text="Claim A.", source_url="https://example.com/1")])
    gateway = _mock_gateway(structured_side_effect=[
        RuntimeError("timeout"),
        RuntimeError("timeout"),
        success,
    ])
    mock_default_gateway.return_value = gateway

    from confidence_scorer.analysis.claim_extractor import extract_claims
    result = extract_claims([_make_source(1)], "query")

    assert len(result) == 1
    assert gateway.structured.call_count == 3


@patch("aletheia.analysis.claim_extractor.default_gateway")
def test_extract_claims_returns_empty_after_all_retries_fail(mock_default_gateway):
    gateway = _mock_gateway(structured_side_effect=RuntimeError("persistent error"))
    mock_default_gateway.return_value = gateway

    from confidence_scorer.analysis.claim_extractor import extract_claims
    result = extract_claims([_make_source(1)], "query")

    assert result == []


@patch("aletheia.analysis.claim_extractor.default_gateway")
def test_consolidate_claims_returns_canonical_with_empty_stances(mock_default_gateway):
    from confidence_scorer.analysis.claim_extractor import _CanonicalClaimList
    expected = _CanonicalClaimList(claims=["Coffee is associated with lower diabetes risk."])
    mock_default_gateway.return_value = _mock_gateway(structured_return=expected)

    from confidence_scorer.analysis.claim_extractor import consolidate_claims
    result = consolidate_claims([_make_raw_claim(1), _make_raw_claim(2)], "query")

    assert len(result) == 1
    assert isinstance(result[0], CanonicalClaim)
    assert result[0].stances == []
    assert result[0].confidence == 0.0


@patch("aletheia.analysis.claim_extractor.default_gateway")
def test_consolidate_claims_returns_empty_after_retries(mock_default_gateway):
    gateway = _mock_gateway(structured_side_effect=RuntimeError("fail"))
    mock_default_gateway.return_value = gateway

    from confidence_scorer.analysis.claim_extractor import consolidate_claims
    result = consolidate_claims([_make_raw_claim(1)], "query")

    assert result == []
