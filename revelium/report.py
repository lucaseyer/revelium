"""Report serialization and human-facing report helpers."""

from __future__ import annotations

import json
from pathlib import Path

from revelium.config import ReveliumConfig
from revelium.models import PageSnapshot, RevelationReport, RevealedCandidate


def save_report(report: RevelationReport, config: ReveliumConfig) -> dict[str, str]:
    """Persist report artifacts locally and return created file paths."""

    output_files: dict[str, str] = {}
    report_dir = config.report_path
    report_dir.mkdir(parents=True, exist_ok=True)

    slug = _build_slug(report.snapshot)

    if config.save_dom_on_failure:
        dom_path = report_dir / f"{slug}.html"
        dom_path.write_text(report.snapshot.page_source, encoding="utf-8")
        output_files["dom_snapshot"] = str(dom_path)

    if config.save_json_report:
        report_path = report_dir / f"{slug}.json"
        output_files["report_json"] = str(report_path)
        payload = report.model_copy(update={"saved_files": output_files})
        report_path.write_text(
            json.dumps(payload.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )

    return output_files


def infer_probable_cause(
    snapshot: PageSnapshot,
    candidates: list[RevealedCandidate],
) -> str | None:
    """Infer a small, readable failure cause from the scored candidates."""

    if not candidates:
        return "No relevant alternative elements were revealed in the current DOM"

    best = candidates[0]
    if best.score >= 0.7:
        return (
            f"Original {snapshot.locator_strategy} is no longer present, but a similar "
            f"{best.tag} remains in the DOM"
        )
    if best.score >= 0.35:
        return "The page still contains related elements, but their structure or attributes appear to have drifted"
    return "Relevant page structure was revealed, but no strong replacement candidate was found"


def render_report_text(report: RevelationReport) -> str:
    """Render a concise CLI-friendly representation."""

    lines = [
        "Revelium Report",
        f"Action: {report.snapshot.action}",
        f"Locator: {report.snapshot.locator_strategy}={report.snapshot.locator_value}",
        f"Hint: {report.snapshot.hint or '-'}",
        f"URL: {report.snapshot.page_url}",
        f"Timestamp: {report.snapshot.timestamp.isoformat()}",
        f"Probable cause: {report.insight.probable_cause or '-'}",
        "Top candidates:",
    ]

    for index, candidate in enumerate(report.insight.top_candidates, start=1):
        lines.append(
            f"{index}. {candidate.locator_strategy}={candidate.locator_value} "
            f"[score={candidate.score:.2f}]"
        )
        lines.append(f"   tag={candidate.tag} text={candidate.text or '-'}")
        if candidate.reasons:
            lines.append(f"   reasons={'; '.join(candidate.reasons)}")

    return "\n".join(lines)


def _build_slug(snapshot: PageSnapshot) -> str:
    timestamp = snapshot.timestamp.strftime("%Y%m%dT%H%M%S")
    strategy = snapshot.locator_strategy.lower().replace(" ", "-")
    locator = _safe_name(snapshot.locator_value)
    return f"{timestamp}_{snapshot.action}_{strategy}_{locator}"


def _safe_name(value: str) -> str:
    return "".join(char if char.isalnum() else "-" for char in value.lower()).strip("-")[:60]
