"""Structured models used across the revelation pipeline."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PageSnapshot(BaseModel):
    page_url: str
    timestamp: datetime
    action: str
    locator_strategy: str
    locator_value: str
    hint: str | None = None
    page_source: str


class FailureTrace(BaseModel):
    action: str
    locator_strategy: str
    locator_value: str
    message: str
    page_url: str
    timestamp: datetime
    hint: str | None = None


class RevealedCandidate(BaseModel):
    tag: str
    text: str
    attributes: dict[str, str] = Field(default_factory=dict)
    locator_strategy: str
    locator_value: str
    score: float = 0.0
    reasons: list[str] = Field(default_factory=list)


class LocatorInsight(BaseModel):
    locator_strategy: str
    locator_value: str
    action: str
    hint: str | None = None
    probable_cause: str | None = None
    top_candidates: list[RevealedCandidate] = Field(default_factory=list)


class RevelationReport(BaseModel):
    snapshot: PageSnapshot
    failure: FailureTrace
    insight: LocatorInsight
    saved_files: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
