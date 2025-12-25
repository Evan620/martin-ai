#!/usr/bin/env python
"""
Interactive CLI for testing semantic search.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from src.knowledge.knowledge_base import KnowledgeBase

console = Console()

def search_loop():
    """Interactive search loop."""
    console.print(Panel.fit(
        "[bold green]ECOWAS Summit Knowledge Base - Interactive Search[/bold green]\n"
        "Type your query and press Enter.\n"
        "Type 'exit', 'quit', or 'q' to stop.",
        title="Welcome"
    ))

    try:
        # Initialize KB
        with console.status("[bold blue]Initializing knowledge base...[/bold blue]"):
            kb = KnowledgeBase()
            kb.initialize()
            # Verify connection by getting stats
            stats = kb.get_stats()
            vector_count = stats.get('total_vector_count', 0)
        
        console.print(f"[green]✓ Connected to Knowledge Base ({vector_count} vectors loaded)[/green]\n")

        while True:
            # Get user input
            query = console.input("[bold yellow]Query > [/bold yellow]").strip()
            
            if query.lower() in ('exit', 'quit', 'q'):
                console.print("[blue]Goodbye![/blue]")
                break
            
            if not query:
                continue

            # Perform search
            with console.status(f"[bold blue]Searching for: '{query}'...[/bold blue]"):
                results = kb.search(query, top_k=10)

            if not results:
                console.print("[red]No results found.[/red]")
                continue

            # Display results
            console.print(f"\n[bold]Found {len(results)} results:[/bold]\n")
            
            for i, res in enumerate(results, 1):
                score = res['score']
                source = Path(res['metadata']['source']).name
                content = res['content']
                sector = res['metadata'].get('sector', 'N/A')
                
                # Create a panel for each result
                header = f"Result #{i} | Score: {score:.4f} | Source: {source} | Sector: {sector}"
                console.print(Panel(
                    Markdown(content),
                    title=header,
                    border_style="green" if score > 0.7 else "blue"
                ))
            
            console.print("\n" + "-"*50 + "\n")

    except KeyboardInterrupt:
        console.print("\n[blue]Goodbye![/blue]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    search_loop()
