import json

from revelium.config import ReveliumConfig
from revelium.engine import RevelationEngine
from revelium.report import render_report_text, save_report
from revelium.snapshot import build_page_snapshot


HTML = """
<html>
  <body>
    <button data-testid="login-submit">Sign in</button>
    <button id="cancel-login">Cancel</button>
  </body>
</html>
"""


def test_report_generation_and_persistence(tmp_path) -> None:
    snapshot = build_page_snapshot(
        page_source=HTML,
        current_url="https://example.com/login",
        action="click",
        locator_strategy="id",
        locator_value="submit-login",
        hint="login button",
    )

    report = RevelationEngine().reveal(snapshot, "Unable to locate element")
    saved_files = save_report(
        report,
        ReveliumConfig(report_dir=str(tmp_path), save_dom_on_failure=True, save_json_report=True),
    )
    report.saved_files.update(saved_files)

    report_files = list(tmp_path.glob("*.json"))
    dom_files = list(tmp_path.glob("*.html"))

    assert len(report.insight.top_candidates) >= 1
    assert report.insight.probable_cause is not None
    assert len(report_files) == 1
    assert len(dom_files) == 1

    payload = json.loads(report_files[0].read_text(encoding="utf-8"))
    assert payload["insight"]["top_candidates"][0]["score"] >= 0

    output = render_report_text(report)
    assert "Revelium Report" in output
