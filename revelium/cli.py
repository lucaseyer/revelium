"""Command-line interface for inspecting Revelium reports."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from revelium.models import RevelationReport
from revelium.report import render_report_text

app = typer.Typer(help="Inspect Revelium revelation reports.")


@app.command()
def inspect(report_path: Path) -> None:
    """Load a report JSON file and display it in a friendly format."""

    data = json.loads(report_path.read_text(encoding="utf-8"))
    report = RevelationReport.model_validate(data)
    typer.echo(render_report_text(report))


if __name__ == "__main__":
    app()
