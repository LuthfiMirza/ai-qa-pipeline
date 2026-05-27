import pytest

try:
    from playwright.sync_api import Page, expect
except ModuleNotFoundError:
    Page = object
    expect = None
    pytestmark = pytest.mark.skip(reason="playwright is not installed")
else:
    pytestmark = pytest.mark.ui

LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
VALID_USERNAME = "student"
VALID_PASSWORD = "Password123"
INVALID_USERNAME = "wrong_user"
INVALID_PASSWORD = "wrong_password"


def open_login_page(page: Page) -> None:
    page.goto(LOGIN_URL)


def test_login_page_title(page: Page):
    open_login_page(page)
    expect(page).to_have_title("Test Login | Practice Test Automation")


def test_login_page_has_username_field(page: Page):
    open_login_page(page)
    expect(page.locator("#username")).to_be_visible()


def test_login_page_has_password_field(page: Page):
    open_login_page(page)
    expect(page.locator("#password")).to_be_visible()


def test_login_page_has_submit_button(page: Page):
    open_login_page(page)
    expect(page.locator("#submit")).to_be_visible()


def test_login_success_with_valid_credentials(page: Page):
    open_login_page(page)
    page.locator("#username").fill(VALID_USERNAME)
    page.locator("#password").fill(VALID_PASSWORD)
    page.locator("#submit").click()

    expect(page).to_have_url("https://practicetestautomation.com/logged-in-successfully/")
    expect(page.locator("h1")).to_contain_text("Logged In Successfully")
    expect(page.locator(".wp-block-button__link")).to_contain_text("Log out")


def test_login_fails_with_invalid_username(page: Page):
    open_login_page(page)
    page.locator("#username").fill(INVALID_USERNAME)
    page.locator("#password").fill(VALID_PASSWORD)
    page.locator("#submit").click()

    expect(page.locator("#error")).to_be_visible()
    expect(page.locator("#error")).to_contain_text("Your username is invalid")


def test_login_fails_with_invalid_password(page: Page):
    open_login_page(page)
    page.locator("#username").fill(VALID_USERNAME)
    page.locator("#password").fill(INVALID_PASSWORD)
    page.locator("#submit").click()

    expect(page.locator("#error")).to_be_visible()
    expect(page.locator("#error")).to_contain_text("Your password is invalid")


def test_login_fails_with_empty_credentials(page: Page):
    open_login_page(page)
    page.locator("#submit").click()

    expect(page.locator("#error")).to_be_visible()


def test_username_field_accepts_text(page: Page):
    open_login_page(page)
    page.locator("#username").fill("sample_user")
    expect(page.locator("#username")).to_have_value("sample_user")


def test_password_field_accepts_text(page: Page):
    open_login_page(page)
    page.locator("#password").fill("secret")
    expect(page.locator("#password")).to_have_value("secret")
