"""Formats the final research report using rich."""

from io import StringIO
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text

from confidence_scorer.agent.state import CanonicalClaim


def format_report(claims: list[CanonicalClaim], query: str) -> str:
    """Render a colour-coded report and return it as a string."""
    buf = StringIO()
    console = Console(file=buf, highlight=False)

    total_sources = max((len(c.stances) for c in claims), default=0)
    console.print(f"\n[bold cyan]Research Query:[/bold cyan] {query}")
    console.print(f"[dim]Sources analysed: {total_sources} | Claims found: {len(claims)}[/dim]\n")

    for i, claim in enumerate(claims, 1):
        console.rule(f"[bold]Claim {i}[/bold]")
        console.print(f"[bold white]{claim.text}[/bold white]\n")

        # Confidence badge
        score = claim.confidence
        if score >= 0.7:
            score_style = "bold green"
        elif score >= 0.4:
            score_style = "bold yellow"
        else:
            score_style = "bold red"

        counts = (
            f"[green]{claim.supports} support[/green] · "
            f"[red]{claim.contradicts} contradict[/red] · "
            f"[dim]{claim.neutral} neutral[/dim]"
        )
        console.print(
            f"  Confidence: [{score_style}]{score:.2f}[/{score_style}]   {counts}\n"
        )

        # Supporting quotes
        supporting = [s for s in claim.stances if s.stance == "support"]
        if supporting:
            console.print("  [green]Supporting sources:[/green]")
            for s in supporting:
                quote = f'  "{s.quote}"' if s.quote else ""
                console.print(f"    [green]▸[/green] {s.source_url}")
                if quote:
                    console.print(f"      [green dim italic]{quote}[/green dim italic]")

        # Contradicting quotes
        contradicting = [s for s in claim.stances if s.stance == "contradict"]
        if contradicting:
            console.print("  [red]Contradicting sources:[/red]")
            for s in contradicting:
                quote = f'  "{s.quote}"' if s.quote else ""
                console.print(f"    [red]▸[/red] {s.source_url}")
                if quote:
                    console.print(f"      [red dim italic]{quote}[/red dim italic]")

        # Neutral sources
        neutral = [s for s in claim.stances if s.stance == "neutral"]
        if neutral:
            console.print("  [dim]Neutral / not addressed:[/dim]")
            for s in neutral:
                console.print(f"    [dim]▸ {s.source_url}[/dim]")

        console.print()

    return buf.getvalue()
