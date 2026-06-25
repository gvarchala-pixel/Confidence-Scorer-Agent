"""Node functions for the Confidence Scorer LangGraph agent graph."""

import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.types import Command, interrupt

from confidence_scorer.agent.state import AgentState
from confidence_scorer.analysis.claim_extractor import consolidate_claims, extract_claims
from confidence_scorer.analysis.confidence import score_confidence
from confidence_scorer.analysis.stance_classifier import classify_all_stances
from confidence_scorer.output.report import format_report
from confidence_scorer.tools.arxiv_search import ArxivSearchTool
from confidence_scorer.tools.web_search import get_web_search_tool

logger = logging.getLogger(__name__)


def detect_stage(state: AgentState) -> int:
    """Determine the current pipeline stage from state fields."""
    if not state.get("sources"):
        return 0
    if not state.get("raw_claims"):
        return 1
    if not state.get("claims"):
        return 2
    # Check if stances have been classified (any claim with stances populated)
    claims = state.get("claims", [])
    if not any(c.stances for c in claims):
        return 3
    # Check if confidence has been scored (any claim with non-zero confidence)
    if not any(c.confidence > 0.0 for c in claims):
        return 4
    if not state.get("report"):
        return 5
    return 6  # done


# --- Nodes ---

def input_node(state: AgentState) -> dict:
    """Validate the query."""
    query = state.get("query", "").strip()
    if not query:
        return {"error": "Query must not be empty.", "messages": []}
    return {"messages": [HumanMessage(content=f"Research this question: {query}")]}


def agent_node(state: AgentState) -> dict:
    """Pick the next pipeline step from state."""
    if state.get("error"):
        return {}

    stage = detect_stage(state)
    if stage == 6:
        return {}

    # Map stage → (tool_name, args). Stage 0 runs both searches in one shot.
    stage_to_tool = {
        0: ("search_all",          {"query": state["query"]}),
        1: ("extract_claims",      {}),
        2: ("consolidate_claims",  {}),
        3: ("classify_all_stances",{}),
        4: ("score_confidence",    {}),
        5: ("format_report",       {}),
    }
    tool_name, tool_args = stage_to_tool[stage]

    return {"messages": [AIMessage(
        content="",
        tool_calls=[{
            "id": f"call_{stage}",
            "name": tool_name,
            "args": tool_args,
            "type": "tool_call",
        }],
    )]}


def tools_node(state: AgentState) -> Command:
    """Dispatch the tool call requested by the agent and update structured state."""
    last_message = state["messages"][-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return Command(update={})

    tool_call = last_message.tool_calls[0]
    tool_name: str = tool_call["name"]
    tool_args: dict = tool_call.get("args", {})
    tool_call_id: str = tool_call["id"]

    update: dict[str, Any] = {}
    result_text = ""

    try:
        if tool_name == "search_all":
            query = tool_args.get("query", state["query"])
            web = get_web_search_tool().search(query)
            arxiv = ArxivSearchTool().search(query)
            all_sources = web + arxiv
            update["sources"] = all_sources
            result_text = f"Found {len(web)} web + {len(arxiv)} arXiv sources ({len(all_sources)} total)."
            logger.info(result_text)

        elif tool_name == "extract_claims":
            raw = extract_claims(state["sources"], state["query"])
            update["raw_claims"] = raw
            result_text = f"Extracted {len(raw)} raw claims."

        elif tool_name == "consolidate_claims":
            canonical = consolidate_claims(state["raw_claims"], state["query"])
            update["claims"] = canonical
            result_text = f"Consolidated into {len(canonical)} canonical claims."

        elif tool_name == "classify_all_stances":
            updated_claims = classify_all_stances(
                list(state["claims"]), list(state["sources"])
            )
            update["claims"] = updated_claims
            result_text = "Stance classification complete."

        elif tool_name == "score_confidence":
            scored = score_confidence(list(state["claims"]))
            update["claims"] = scored
            result_text = "Confidence scoring complete."

        elif tool_name == "format_report":
            report = format_report(state["claims"], state["query"])
            update["report"] = report
            result_text = report

        else:
            result_text = f"Unknown tool: {tool_name}"

    except Exception as exc:
        logger.exception("Tool %s failed", tool_name)
        result_text = f"Tool {tool_name} failed: {exc}"
        update["error"] = result_text

    update["messages"] = [ToolMessage(content=result_text, tool_call_id=tool_call_id)]
    return Command(update=update, goto="agent_node")


def human_node(state: AgentState) -> dict:
    """Interrupt to show found sources and ask user to confirm before analysis."""
    sources = state.get("sources", [])
    summary_lines = [f"\n{len(sources)} sources found:"]
    for i, s in enumerate(sources, 1):
        summary_lines.append(f"  [{s.source_type}] {i}. {s.title} — {s.url}")
    summary = "\n".join(summary_lines)

    user_response: str = interrupt(
        summary + "\n\nProceed with analysis? (y/n or enter a new query to redirect): "
    )

    user_response = user_response.strip().lower()
    if user_response == "n":
        return {"error": "User cancelled analysis.", "messages": [
            HumanMessage(content="User chose not to proceed.")
        ]}
    elif user_response == "y" or not user_response:
        return {"messages": [HumanMessage(content="Proceed with analysis.")]}
    else:
        # Treat as a redirect query
        return {
            "query": user_response,
            "sources": [],
            "raw_claims": [],
            "claims": [],
            "messages": [HumanMessage(content=f"New query: {user_response}")],
        }
