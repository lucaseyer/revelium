from revelium.analyzer import extract_relevant_candidates
from revelium.snapshot import build_page_snapshot


HTML = """
<html>
  <body>
    <button id="submit-login">Sign in</button>
    <input name="email" aria-label="email field" />
    <div class="layout">
      <a data-testid="help-link">Need help?</a>
    </div>
  </body>
</html>
"""


def test_extract_relevant_candidates_prioritizes_actionable_elements() -> None:
    snapshot = build_page_snapshot(
        page_source=HTML,
        current_url="https://example.com/login",
        action="find",
        locator_strategy="id",
        locator_value="submit-login",
        hint="login button",
    )

    candidates = extract_relevant_candidates(snapshot)

    assert len(candidates) == 3
    assert {candidate.tag for candidate in candidates} == {"button", "input", "a"}
