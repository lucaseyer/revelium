"""Custom Revelium exception types."""

from __future__ import annotations

from revelium.models import RevelationReport


class ReveliumAnalysisError(Exception):
    """Wrap a Selenium failure with the generated revelation report."""

    def __init__(self, message: str, report: RevelationReport):
        super().__init__(message)
        self.report = report
