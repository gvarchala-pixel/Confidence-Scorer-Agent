"""Academic paper search tool backed by arXiv."""

import logging
import arxiv

from confidence_scorer.tools.base import BaseTool, Source

logger = logging.getLogger(__name__)

MAX_RESULTS = 5


class ArxivSearchTool(BaseTool):
    name = "search_arxiv"
    description = "Search arXiv for academic papers relevant to the query."

    def search(self, query: str) -> list[Source]:
        try:
            client = arxiv.Client()
            search = arxiv.Search(query=query, max_results=MAX_RESULTS)
            results = list(client.results(search))
            return [
                Source(
                    url=r.entry_id,
                    title=r.title,
                    content=r.summary,
                    source_type="arxiv",
                )
                for r in results[:MAX_RESULTS]
            ]
        except Exception as exc:
            logger.warning("arXiv search failed: %s", exc)
            return []
