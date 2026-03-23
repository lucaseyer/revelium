"""Page snapshot capture utilities."""

from __future__ import annotations

from datetime import datetime, timezone

from revelium.models import FailureTrace, PageSnapshot


def build_page_snapshot(
    *,
    page_source: str,
    current_url: str,
    action: str,
    locator_strategy: str,
    locator_value: str,
    hint: str | None,
) -> PageSnapshot:
    """Capture a stable snapshot of the page at failure time."""

    timestamp = datetime.now(timezone.utc)
    return PageSnapshot(
        page_url=current_url,
        timestamp=timestamp,
        action=action,
        locator_strategy=locator_strategy,
        locator_value=locator_value,
        hint=hint,
        page_source=page_source,
    )


def build_failure_trace(snapshot: PageSnapshot, message: str) -> FailureTrace:
    """Create the failure trace associated with a snapshot."""

    return FailureTrace(
        action=snapshot.action,
        locator_strategy=snapshot.locator_strategy,
        locator_value=snapshot.locator_value,
        message=message,
        page_url=snapshot.page_url,
        timestamp=snapshot.timestamp,
        hint=snapshot.hint,
    )
