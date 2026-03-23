from revelium.models import RevealedCandidate
from revelium.scorer import score_candidate
from revelium.snapshot import build_page_snapshot


def test_score_candidate_rewards_locator_and_hint_overlap() -> None:
    snapshot = build_page_snapshot(
        page_source="<button data-testid='login-submit'>Log in</button>",
        current_url="https://example.com/login",
        action="click",
        locator_strategy="id",
        locator_value="submit-login",
        hint="login button",
    )
    candidate = RevealedCandidate(
        tag="button",
        text="Log in",
        attributes={"data-testid": "login-submit", "aria-label": "login button"},
        locator_strategy="css selector",
        locator_value="[data-testid='login-submit']",
    )

    score, reasons = score_candidate(snapshot, candidate)

    assert score > 0.4
    assert any("hint" in reason or "locator" in reason for reason in reasons)
