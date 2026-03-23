"""Configuration primitives for Revelium."""

from pathlib import Path

from pydantic import BaseModel, field_validator


class ReveliumConfig(BaseModel):
    """Runtime configuration for report generation and logging."""

    report_dir: str = "revelium_reports"
    save_dom_on_failure: bool = True
    save_json_report: bool = True
    log_level: str = "INFO"

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def report_path(self) -> Path:
        return Path(self.report_dir)
