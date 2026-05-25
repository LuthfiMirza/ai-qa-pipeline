import pytest
from playwright.sync_api import Page, expect

LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
VALID_USERNAME = "student"
VALID_PASSWORD = "Password123"
INVALID_USERNAME = "wrong_user"
INVALID_PASSWORD = "wrong_password"


@pytest.fixture
def login_page(page: Page):
    page.goto(LOGIN_URL)
    return page


def test_login_page_title(login_page: Page):
    expect(login_page).to_have_title("Test Login | Practice Test Automation")


def test_login_page_has_username_field(login_page: Page):
    expect(login_page.locator("#username")).to_be_visible()


def test_login_page_has_password_field(login_page: Page):
    expect(login_page.locator("#password")).to_be_visible()


def test_login_page_has_submit_button(login_page: Page):
    expect(login_page.locator("#submit")).to_be_visible()


def test_login_success_with_valid_credentials(login_page: Page):
    login_page.locator("#username").fill(VALID_USERNAME)
    login_page.locator("#password").fill(VALID_PASSWORD)
    login_page.locator("#submit").click()

    expect(login_page).to_have_url("https://practicetestautomation.com/logged-in-successfully/")
    expect(login_page.locator("h1")).to_contain_text("Logged In Successfully")
    expect(login_page.locator(".wp-block-button__link")).to_contain_text("Log out")


def test_login_fails_with_invalid_username(login_page: Page):
    login_page.locator("#username").fill(INVALID_USERNAME)
    login_page.locator("#password").fill(VALID_PASSWORD)
    login_page.locator("#submit").click()

    expect(login_page.locator("#error")).to_be_visible()
    expect(login_page.locator("#error")).to_contain_text("Your username is invalid")


def test_login_fails_with_invalid_password(login_page: Page):
    login_page.locator("#username").fill(VALID_USERNAME)
    login_page.locator("#password").fill(INVALID_PASSWORD)
    login_page.locator("#submit").click()

    expect(login_page.locator("#error")).to_be_visible()
    expect(login_page.locator("#error")).to_contain_text("Your password is invalid")


def test_login_fails_with_empty_credentials(login_page: Page):
    login_page.locator("#submit").click()

    expect(login_page.locator("#error")).to_be_visible()


def test_username_field_accepts_text(login_page: Page):
    login_page.locator("#username").fill("sample_user")
    expect(login_page.locator("#username")).to_have_value("sample_user")


def test_password_field_accepts_text(login_page: Page):
    login_page.locator("#password").fill("secret")
    expect(login_page.locator("#password")).to_have_value("secret")
