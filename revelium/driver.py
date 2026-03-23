"""Public Selenium driver wrapper for Revelium."""

from __future__ import annotations

import logging
from typing import Any

from selenium.common.exceptions import NoSuchElementException, WebDriverException

from revelium.config import ReveliumConfig
from revelium.engine import RevelationEngine
from revelium.report import save_report
from revelium.snapshot import build_page_snapshot


class ReveliumDriver:
    """Thin Selenium wrapper that reveals failure context before re-raising."""

    def __init__(self, webdriver: Any, config: ReveliumConfig | None = None):
        self.webdriver = webdriver
        self.config = config or ReveliumConfig()
        self.engine = RevelationEngine()
        self.logger = logging.getLogger("revelium")
        self._configure_logger()

    def find(self, by: str, value: str, hint: str | None = None) -> Any:
        return self._locate(by, value, hint=hint, action="find")

    def click(self, by: str, value: str, hint: str | None = None) -> None:
        element = self._locate(by, value, hint=hint, action="click")
        try:
            element.click()
        except WebDriverException as error:
            self._reveal_failure("click", by, value, hint, error)
            raise

    def type(self, by: str, value: str, text: str, hint: str | None = None) -> None:
        element = self._locate(by, value, hint=hint, action="type")
        try:
            element.clear()
            element.send_keys(text)
        except WebDriverException as error:
            self._reveal_failure("type", by, value, hint, error)
            raise

    def _locate(self, by: str, value: str, hint: str | None, action: str) -> Any:
        try:
            return self.webdriver.find_element(by, value)
        except NoSuchElementException as error:
            self._reveal_failure(action, by, value, hint, error)
            raise

    def _reveal_failure(
        self,
        action: str,
        by: str,
        value: str,
        hint: str | None,
        error: Exception,
    ) -> None:
        self.logger.error("[Revelium] Action failed: %s %s=%s", action, by, value)
        snapshot = build_page_snapshot(
            page_source=self.webdriver.page_source,
            current_url=self.webdriver.current_url,
            action=action,
            locator_strategy=by,
            locator_value=value,
            hint=hint,
        )
        report = self.engine.reveal(snapshot, str(error))
        saved_files = save_report(report, self.config)
        report.saved_files.update(saved_files)

        self.logger.error(
            "[Revelium] Revealed %s candidate elements",
            len(report.insight.top_candidates),
        )
        if report.insight.top_candidates:
            top = report.insight.top_candidates[0]
            self.logger.error(
                "[Revelium] Top candidate: %s=%s (score: %.2f)",
                top.locator_strategy,
                top.locator_value,
                top.score,
            )
        if report.insight.probable_cause:
            self.logger.error("[Revelium] Likely cause: %s", report.insight.probable_cause)

    def _configure_logger(self) -> None:
        if self.logger.handlers:
            return

        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(self.config.log_level)
