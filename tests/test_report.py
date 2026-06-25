"""Tests for aletheia.output.report — pure Python, no mocking needed."""

from confidence_scorer.agent.state import CanonicalClaim, StanceResult
from confidence_scorer.analysis.confidence import score_confidence
from confidence_scorer.output.report import format_report


def _stance(stance: str, url: str, quote: str | None = None) -> StanceResult:
    return StanceResult(source_url=url, stance=stance, quote=quote, reasoning="r")


def _claim(text: str, stances: list[StanceResult]) -> CanonicalClaim:
    c = CanonicalClaim(text=text, stances=stances)
    score_confidence([c])
    return c


def test_report_contains_query():
    claim = _claim("Coffee reduces diabetes risk.", [_stance("support", "https://a.com")])
    report = format_report([claim], "Does coffee reduce diabetes risk?")
    assert "Does coffee reduce diabetes risk?" in report


def test_report_contains_claim_text():
    claim = _claim("Coffee reduces diabetes risk.", [_stance("support", "https://a.com")])
    report = format_report([claim], "query")
    assert "Coffee reduces diabetes risk." in report


def test_report_contains_source_url():
    claim = _claim("Claim A.", [_stance("support", "https://source.com")])
    report = format_report([claim], "query")
    assert "https://source.com" in report


def test_report_contains_confidence_score():
    claim = _claim("Claim A.", [_stance("support", "https://a.com")])
    report = format_report([claim], "query")
    assert "0." in report  # confidence is always a decimal


def test_report_contains_counts():
    stances = [
        _stance("support", "https://a.com"),
        _stance("support", "https://b.com"),
        _stance("contradict", "https://c.com"),
    ]
    claim = _claim("Claim.", stances)
    report = format_report([claim], "query")
    assert "2 support" in report
    assert "1 contradict" in report


def test_report_includes_quote_when_present():
    stances = [_stance("support", "https://a.com", quote="Coffee definitely helps.")]
    claim = _claim("Claim.", stances)
    report = format_report([claim], "query")
    assert "Coffee definitely helps." in report


def test_report_handles_no_claims():
    report = format_report([], "empty query")
    assert "empty query" in report


def test_report_handles_multiple_claims():
    claims = [
        _claim("Claim A.", [_stance("support", "https://a.com")]),
        _claim("Claim B.", [_stance("contradict", "https://b.com")]),
    ]
    report = format_report(claims, "query")
    assert "Claim A." in report
    assert "Claim B." in report
    assert "Claim 1" in report
    assert "Claim 2" in report
