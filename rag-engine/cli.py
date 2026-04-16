#!/usr/bin/env python3
"""
cli.py — RAG Engine CLI
Main entry point for all pipeline operations.

Usage:
    python cli.py ingest          # Load, chunk, embed, and store docs
    python cli.py query "question" # Ask a question (retrieval only — Phase 2)
    python cli.py ask "question"   # Full RAG: retrieve + Claude (Phase 3)
    python cli.py stats            # Show what's in the vector store
    python cli.py reset            # Wipe the vector store and start fresh
"""

import sys
import logging
import yaml
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

console = Console()


def load_config(config_path: str = "config.yaml") -> dict:
    """Load and return the config file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_logging(config: dict):
    """Configure logging from config settings."""
    log_cfg = config.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO").upper())

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_cfg.get("log_file", "rag_engine.log")),
        ],
    )


# ============================================================
# Commands
# ============================================================

def cmd_ingest(config: dict):
    """Ingest documents: load → chunk → embed → store."""
    from ingest.pipeline import run_ingest
    from embed.embedder import embed_texts
    from embed.store import store_chunks, get_collection_stats

    console.print(Panel.fit(
        "[bold green]Phase 1: Ingest + Embed[/bold green]\n"
        f"Domain: [cyan]{config['domain']['name']}[/cyan]\n"
        f"Source:  [cyan]{config['domain']['docs_path']}[/cyan]",
        border_style="green",
    ))

    # Load and chunk
    chunks = run_ingest(config)
    if not chunks:
        console.print("[red]No chunks produced. Add docs and try again.[/red]")
        return

    # Embed
    emb_cfg = config["embedding"]
    console.print(f"\n[bold]Embedding {len(chunks)} chunks...[/bold]")
    texts = [c.content for c in chunks]
    embeddings = embed_texts(texts, emb_cfg["model_name"], emb_cfg["device"])

    # Store
    console.print(f"\n[bold]Storing in ChromaDB...[/bold]")
    count = store_chunks(chunks, embeddings, config)

    # Summary
    stats = get_collection_stats(config)
    console.print(Panel.fit(
        f"[bold green]✓ Ingest complete![/bold green]\n"
        f"Documents processed → chunks stored: [cyan]{count}[/cyan]\n"
        f"Total in vector store: [cyan]{stats['total_chunks']}[/cyan]",
        border_style="green",
    ))


def cmd_query(config: dict, question: str):
    """Retrieve relevant chunks for a question (no Claude, just retrieval)."""
    from retrieve.query import retrieve
    from retrieve.prompt import build_debug_prompt

    console.print(Panel.fit(
        f"[bold yellow]Phase 2: Retrieval Test[/bold yellow]\n"
        f"Question: [cyan]{question}[/cyan]",
        border_style="yellow",
    ))

    results = retrieve(question, config)

    if not results:
        console.print("[red]No results found. Is the vector store populated?[/red]")
        console.print("Run: [bold]python cli.py ingest[/bold]")
        return

    # Display results
    table = Table(title="Retrieved Chunks", show_lines=True)
    table.add_column("#", style="bold", width=3)
    table.add_column("Source", style="cyan", width=30)
    table.add_column("Score", style="green", width=8)
    table.add_column("Preview", width=60)

    for i, result in enumerate(results, 1):
        score = result.get("rerank_score", result.get("score", 0))
        preview = result["content"][:150].replace("\n", " ") + "..."
        table.add_row(
            str(i),
            result["metadata"].get("source", "?"),
            f"{score:.3f}",
            preview,
        )

    console.print(table)

    # Show what the prompt would look like
    console.print("\n[dim]--- Debug: Full prompt that would be sent to Claude ---[/dim]")
    debug = build_debug_prompt(question, results)
    console.print(Panel(debug, border_style="dim"))


def cmd_ask(config: dict, question: str):
    """Full RAG pipeline: retrieve context → send to Claude → show answer."""
    from retrieve.query import retrieve
    from retrieve.prompt import build_prompt
    from generate.claude_client import generate_response

    console.print(Panel.fit(
        f"[bold magenta]Full RAG Query[/bold magenta]\n"
        f"Question: [cyan]{question}[/cyan]",
        border_style="magenta",
    ))

    # Retrieve
    console.print("[dim]Retrieving relevant context...[/dim]")
    results = retrieve(question, config)

    if not results:
        console.print("[red]No relevant context found in the knowledge base.[/red]")
        return

    console.print(f"[dim]Found {len(results)} relevant chunks. Asking Claude...[/dim]\n")

    # Build prompt
    system_prompt, user_message = build_prompt(question, results)

    # Generate
    console.print(Panel.fit("[bold]Claude's Response:[/bold]", border_style="magenta"))
    response = generate_response(system_prompt, user_message, config, stream=True)

    # Show sources
    console.print("\n[dim]--- Sources ---[/dim]")
    sources = set()
    for r in results:
        src = r["metadata"].get("source", "unknown")
        score = r.get("rerank_score", r.get("score", 0))
        sources.add(f"  {src} (relevance: {score:.3f})")
    for s in sorted(sources):
        console.print(f"[dim]{s}[/dim]")


def cmd_stats(config: dict):
    """Show vector store statistics."""
    from embed.store import get_collection_stats

    stats = get_collection_stats(config)
    console.print(Panel.fit(
        f"[bold]Vector Store Stats[/bold]\n"
        f"Collection:   [cyan]{stats['collection']}[/cyan]\n"
        f"Total chunks: [cyan]{stats['total_chunks']}[/cyan]\n"
        f"Storage:      [cyan]{stats['persist_dir']}[/cyan]",
        border_style="blue",
    ))


def cmd_reset(config: dict):
    """Reset the vector store (delete all data)."""
    from embed.store import reset_collection

    confirm = input("⚠️  This will delete all stored embeddings. Continue? [y/N] ")
    if confirm.lower() == "y":
        reset_collection(config)
        console.print("[green]✓ Vector store reset.[/green]")
    else:
        console.print("[dim]Cancelled.[/dim]")


# ============================================================
# Main
# ============================================================

USAGE = """
[bold]RAG Engine CLI[/bold]

[cyan]Usage:[/cyan]
  python cli.py ingest             Load, chunk, embed, and store docs
  python cli.py query "question"   Retrieve chunks only (Phase 2 debug)
  python cli.py ask "question"     Full RAG: retrieve + Claude answer
  python cli.py stats              Show vector store info
  python cli.py reset              Wipe the vector store
"""


def main():
    if len(sys.argv) < 2:
        console.print(Panel(USAGE, border_style="cyan"))
        sys.exit(1)

    command = sys.argv[1].lower()
    config = load_config()
    setup_logging(config)

    if command == "ingest":
        cmd_ingest(config)
    elif command == "query":
        if len(sys.argv) < 3:
            console.print("[red]Usage: python cli.py query \"your question\"[/red]")
            sys.exit(1)
        cmd_query(config, " ".join(sys.argv[2:]))
    elif command == "ask":
        if len(sys.argv) < 3:
            console.print("[red]Usage: python cli.py ask \"your question\"[/red]")
            sys.exit(1)
        cmd_ask(config, " ".join(sys.argv[2:]))
    elif command == "stats":
        cmd_stats(config)
    elif command == "reset":
        cmd_reset(config)
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print(Panel(USAGE, border_style="cyan"))
        sys.exit(1)


if __name__ == "__main__":
    main()
