"""Core revelation engine orchestrating analysis and scoring."""

from __future__ import annotations

from revelium.analyzer import extract_relevant_candidates
from revelium.models import LocatorInsight, PageSnapshot, RevelationReport
from revelium.report import infer_probable_cause
from revelium.scorer import score_candidates
from revelium.snapshot import build_failure_trace


class RevelationEngine:
    """Run local analysis for a Selenium locator failure."""

    def reveal(self, snapshot: PageSnapshot, error_message: str) -> RevelationReport:
        candidates = extract_relevant_candidates(snapshot)
        scored = score_candidates(snapshot, candidates)
        top_candidates = sorted(scored, key=lambda item: item.score, reverse=True)[:3]

        insight = LocatorInsight(
            locator_strategy=snapshot.locator_strategy,
            locator_value=snapshot.locator_value,
            action=snapshot.action,
            hint=snapshot.hint,
            probable_cause=infer_probable_cause(snapshot, top_candidates),
            top_candidates=top_candidates,
        )

        return RevelationReport(
            snapshot=snapshot,
            failure=build_failure_trace(snapshot, error_message),
            insight=insight,
        )
