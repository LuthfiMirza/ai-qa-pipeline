from healing_locator import ElementCandidate, HealingLocator


def test_heals_changed_login_button_selector():
    locator = HealingLocator()
    candidates = [
        ElementCandidate(selector="#submit-login", text="Log in", role="button", test_id="login-submit"),
        ElementCandidate(selector="#cancel", text="Cancel", role="button", test_id="cancel"),
    ]

    healed = locator.find_best_match("#submit", candidates)

    assert healed is not None
    assert healed.selector == "#submit-login"
    assert locator.heal_count == 1


def test_keeps_exact_selector_without_healing():
    locator = HealingLocator()
    candidates = [ElementCandidate(selector="#username", text="Email", role="textbox")]

    healed = locator.find_best_match("#username", candidates)

    assert healed is not None
    assert healed.selector == "#username"
    assert locator.heal_count == 0
