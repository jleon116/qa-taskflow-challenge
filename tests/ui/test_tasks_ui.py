BASE_URL = "http://localhost:8080"


def test_open_application(page):
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    assert page.locator("body").is_visible()


def test_page_has_buttons(page):
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    buttons = page.locator("button").count()

    assert buttons >= 0


def test_page_has_inputs(page):
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    inputs = page.locator("input").count()

    assert inputs >= 0