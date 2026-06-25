"""Minimal example of running an Confidence Scorer query.

This is a placeholder until the agent orchestrator is implemented.
"""

from confidence_scorer.agent.state import AgentState


def main() -> None:
    state: AgentState = {
        "query": "Does coffee consumption reduce the risk of type 2 diabetes?",
        "sources": [],
        "claims": [],
        "report": None,
        "error": None,
    }
    print(f"Query: {state['query']}")
    print("Agent pipeline not yet implemented.")


if __name__ == "__main__":
    main()
