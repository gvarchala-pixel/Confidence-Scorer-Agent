"""LangGraph graph definition that wires together the Confidence Scorer agent nodes."""

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from confidence_scorer.agent.state import AgentState
from confidence_scorer.agent.nodes import agent_node, detect_stage, human_node, input_node, tools_node


def _route_agent(state: AgentState) -> str:
    """Decide where to go after agent_node."""
    if state.get("error"):
        return END
    if state.get("report"):
        return END

    last = state["messages"][-1] if state.get("messages") else None
    if last and hasattr(last, "tool_calls") and last.tool_calls:
        return "tools_node"

    stage = detect_stage(state)
    if stage == 6:
        return END

    # No tool call produced — nudge the agent by returning to it
    return "agent_node"


def _should_interrupt_for_human(state: AgentState) -> str:
    """After input_node / after search: check if human review is needed."""
    sources = state.get("sources", [])
    raw_claims = state.get("raw_claims", [])
    if sources and not raw_claims:
        return "human_node"
    return "agent_node"


def build_graph(enable_human_review: bool = True) -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("input_node", input_node)
    builder.add_node("agent_node", agent_node)
    builder.add_node("tools_node", tools_node)
    if enable_human_review:
        builder.add_node("human_node", human_node)

    builder.add_edge(START, "input_node")
    builder.add_edge("input_node", "agent_node")
    builder.add_conditional_edges("agent_node", _route_agent, ["tools_node", "agent_node", END])
    # tools_node uses Command(goto="agent_node") internally

    if enable_human_review:
        # After each search tool result, check if we should pause for human review.
        # We route via the agent → tools → back to agent; inject human check in tools routing.
        builder.add_edge("human_node", "agent_node")

    return builder


def compile_graph(enable_human_review: bool = True):
    """Compile and return the runnable graph."""
    builder = build_graph(enable_human_review=enable_human_review)
    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_node"] if enable_human_review else [],
    )


def run(query: str, skip_human_review: bool = False) -> AgentState:
    """Run the full Confidence Scorer pipeline on a query and return the final state."""
    graph = compile_graph(enable_human_review=not skip_human_review)
    config = {"configurable": {"thread_id": "confidence_scorer-run"}}
    initial_state: AgentState = {
        "messages": [],
        "query": query,
        "sources": [],
        "raw_claims": [],
        "claims": [],
        "report": None,
        "error": None,
    }
    final_state = graph.invoke(initial_state, config=config)
    return final_state
