"""Command-line entry point for Confidence Scorer."""

import argparse
import sys
import os

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="confidence_scorer",
        description="Research agent with calibrated uncertainty.",
    )
    parser.add_argument("query", help="The research question to investigate.")
    parser.add_argument(
        "--model",
        default=None,
        help="Override the Ollama model (default: value in .env or llama3.2).",
    )
    parser.add_argument(
        "--no-human-review",
        action="store_true",
        help="Skip the human review step after searching.",
    )
    args = parser.parse_args()

    if args.model:
        os.environ["OLLAMA_MODEL"] = args.model

    # Import after potential env override so config picks up the new value
    from confidence_scorer.agent.orchestrator import compile_graph

    skip_human = args.no_human_review
    graph = compile_graph(enable_human_review=not skip_human)
    config = {"configurable": {"thread_id": "confidence_scorer-cli"}}

    initial_state = {
        "messages": [],
        "query": args.query,
        "sources": [],
        "raw_claims": [],
        "claims": [],
        "report": None,
        "error": None,
    }

    console.print(f"\n[bold cyan]Confidence Scorer[/bold cyan] — researching: [italic]{args.query}[/italic]\n")

    try:
        if skip_human:
            final = graph.invoke(initial_state, config=config)
        else:
            # Run until the first interrupt (human_node)
            state = graph.invoke(initial_state, config=config)

            # Check if interrupted at human_node
            snapshot = graph.get_state(config)
            if snapshot.next and "human_node" in snapshot.next:
                # Show sources summary
                sources = state.get("sources", [])
                console.print(f"\n[bold]{len(sources)} sources found:[/bold]")
                for i, s in enumerate(sources, 1):
                    console.print(f"  [{s['source_type']}] {i}. {s['title']}")

                console.print(
                    "\nProceed with analysis? "
                    "([green]y[/green]) yes / ([red]n[/red]) no / or type a new query to redirect:"
                )
                user_input = sys.stdin.readline().strip()

                if not user_input or user_input.lower() == "y":
                    graph.update_state(config, {"messages": []}, as_node="human_node")
                elif user_input.lower() == "n":
                    console.print("[yellow]Analysis cancelled.[/yellow]")
                    sys.exit(0)
                else:
                    # Redirect query
                    graph.update_state(
                        config,
                        {
                            "query": user_input,
                            "sources": [],
                            "raw_claims": [],
                            "claims": [],
                        },
                        as_node="human_node",
                    )

                final = graph.invoke(None, config=config)
            else:
                final = state

        if final.get("error"):
            console.print(f"[bold red]Error:[/bold red] {final['error']}")
            sys.exit(1)

        report = final.get("report")
        if report:
            console.print(report)
        else:
            console.print("[yellow]No report was generated.[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
