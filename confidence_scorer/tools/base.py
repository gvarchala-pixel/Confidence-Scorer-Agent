"""Base interfaces shared by all Confidence Scorer search/retrieval tools."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class Source(BaseModel):
    """A single retrieved source document."""

    url: str
    title: str
    content: str
    source_type: str


class BaseTool(ABC):
    """Abstract base class for tools that retrieve `Source` objects."""

    name: str
    description: str

    @abstractmethod
    def search(self, query: str) -> list[Source]:
        """Search for sources relevant to `query`."""
        raise NotImplementedError
