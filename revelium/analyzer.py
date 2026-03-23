"""DOM analysis helpers for revealing alternative candidates."""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from revelium.models import PageSnapshot, RevealedCandidate

PRIORITY_TAGS = {"button", "input", "a"}
PRIORITY_ATTRIBUTES = ("id", "name", "aria-label", "data-testid")


def extract_relevant_candidates(snapshot: PageSnapshot) -> list[RevealedCandidate]:
    """Extract candidates likely to represent the intended target element."""

    soup = BeautifulSoup(snapshot.page_source, "html.parser")
    candidates: list[RevealedCandidate] = []

    for element in soup.find_all(_is_relevant):
        candidates.append(_to_candidate(element, snapshot))

    return candidates


def _is_relevant(element: Tag) -> bool:
    return bool(
        element.name in PRIORITY_TAGS
        or any(element.get(attribute) for attribute in PRIORITY_ATTRIBUTES)
    )


def _to_candidate(element: Tag, snapshot: PageSnapshot) -> RevealedCandidate:
    text = " ".join(element.stripped_strings)
    attributes = {
        key: " ".join(value) if isinstance(value, list) else str(value)
        for key, value in element.attrs.items()
    }

    locator_strategy, locator_value = infer_locator(attributes, element.name)
    return RevealedCandidate(
        tag=element.name or "unknown",
        text=text[:200],
        attributes=attributes,
        locator_strategy=locator_strategy,
        locator_value=locator_value,
    )


def infer_locator(attributes: dict[str, str], tag: str | None) -> tuple[str, str]:
    if attributes.get("data-testid"):
        return "css selector", f"[data-testid='{attributes['data-testid']}']"
    if attributes.get("id"):
        return "id", attributes["id"]
    if attributes.get("name"):
        return "name", attributes["name"]
    if attributes.get("aria-label"):
        return "css selector", f"[aria-label='{attributes['aria-label']}']"
    return "tag name", tag or "unknown"
