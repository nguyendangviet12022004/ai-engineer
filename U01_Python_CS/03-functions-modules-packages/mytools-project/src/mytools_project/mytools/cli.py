"""Typer-based command-line interface for the mytools package."""
from __future__ import annotations

import typer

from mytools_project.mytools import compute_stats, load_column

app = typer.Typer(help="Personal utility CLI built for the AI Engineer roadmap.")


@app.command()
def stats(
    file: str = typer.Option(..., "--file", help="Path to the CSV file."),
    col: str = typer.Option(..., "--col", help="Name of the numeric column."),
) -> None:
    """Compute mean, median, and stdev for a numeric column in a CSV file."""
    values = load_column(file, col)
    result = compute_stats(values)
    typer.echo(f"count : {result.count}")
    typer.echo(f"mean  : {result.mean:.4f}")
    typer.echo(f"median: {result.median:.4f}")
    typer.echo(f"stdev : {result.stdev:.4f}")

@app.command()
def hello():
    print("Hello world")

if __name__ == "__main__":
    app()
