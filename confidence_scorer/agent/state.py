"""Shared state passed between nodes in the LangGraph agent graph."""

from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from confidence_scorer.tools.base import Source


class RawClaim(BaseModel):
    """A factual claim extracted from a single source."""

    text: str
    source_url: str


class StanceResult(BaseModel):
    """How one source relates to one canonical claim."""

    source_url: str
    stance: Literal["support", "contradict", "neutral"]
    quote: Optional[str] = None
    reasoning: str


class CanonicalClaim(BaseModel):
    """A normalised claim with stances from all sources and a confidence score."""

    text: str
    stances: list[StanceResult] = []
    confidence: float = 0.0

    @property
    def supports(self) -> int:
        return sum(1 for s in self.stances if s.stance == "support")

    @property
    def contradicts(self) -> int:
        return sum(1 for s in self.stances if s.stance == "contradict")

    @property
    def neutral(self) -> int:
        return sum(1 for s in self.stances if s.stance == "neutral")


class AgentState(TypedDict):
    """State threaded through the Confidence Scorer agent graph."""

    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    sources: list[Source]
    raw_claims: list[RawClaim]
    claims: list[CanonicalClaim]
    report: Optional[str]
    error: Optional[str]
