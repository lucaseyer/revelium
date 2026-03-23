"""Heuristic scoring for revealed candidates."""

from __future__ import annotations

import re
from collections.abc import Iterable

from revelium.models import PageSnapshot, RevealedCandidate

ATTRIBUTE_WEIGHTS = {
    "id": 0.22,
    "name": 0.18,
    "aria-label": 0.18,
    "data-testid": 0.2,
}
TAG_WEIGHTS = {
    "id": {"button": 0.08, "input": 0.08, "a": 0.05},
    "name": {"input": 0.08, "button": 0.05},
    "css selector": {"button": 0.06, "input": 0.06, "a": 0.05},
}
TEXT_WEIGHT = 0.18
LOCATOR_TOKEN_WEIGHT = 0.14
HINT_WEIGHT = 0.18


def score_candidates(
    snapshot: PageSnapshot,
    candidates: Iterable[RevealedCandidate],
) -> list[RevealedCandidate]:
    """Score candidates from 0 to 1, attaching short reasons."""

    scored: list[RevealedCandidate] = []
    for candidate in candidates:
        score, reasons = score_candidate(snapshot, candidate)
        scored.append(candidate.model_copy(update={"score": score, "reasons": reasons}))
    return scored


def score_candidate(
    snapshot: PageSnapshot,
    candidate: RevealedCandidate,
) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []

    expected_tags = TAG_WEIGHTS.get(snapshot.locator_strategy.lower(), {})
    tag_bonus = expected_tags.get(candidate.tag, 0.0)
    if tag_bonus:
        score += tag_bonus
        reasons.append(f"tag `{candidate.tag}` matches expected interaction pattern")

    locator_value = snapshot.locator_value.lower()
    candidate_text = candidate.text.lower()
    attrs = {key.lower(): value.lower() for key, value in candidate.attributes.items()}

    for attribute, weight in ATTRIBUTE_WEIGHTS.items():
        value = attrs.get(attribute)
        if not value:
            continue
        if locator_value == value:
            score += weight
            reasons.append(f"{attribute} exactly matches locator value")
        elif locator_value in value or value in locator_value:
            score += weight * 0.75
            reasons.append(f"{attribute} partially matches locator value")

    if candidate_text and _shares_token(locator_value, candidate_text):
        score += TEXT_WEIGHT
        reasons.append("visible text overlaps with locator value")

    if _shares_token(locator_value, " ".join(attrs.values())):
        score += LOCATOR_TOKEN_WEIGHT
        reasons.append("candidate attributes share tokens with original locator")

    if snapshot.hint and _shares_token(snapshot.hint.lower(), " ".join([candidate_text, *attrs.values()])):
        score += HINT_WEIGHT
        reasons.append("candidate aligns with the provided hint")

    return min(round(score, 4), 1.0), reasons


def _shares_token(left: str, right: str) -> bool:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    return bool(left_tokens & right_tokens)


def _tokenize(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", value.lower()) if len(token) > 1}
