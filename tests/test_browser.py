import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    expect,
    sync_playwright,
)

BUILD = Path(__file__).resolve().parents[1] / "build"


class BrowserTest(unittest.TestCase):
    server: ThreadingHTTPServer
    thread: threading.Thread
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page

    @classmethod
    def setUpClass(cls) -> None:
        if not (BUILD / "site/index.html").is_file():
            raise RuntimeError("Build the site before running browser tests.")
        # Serve from a subdirectory to match a GitHub project Pages URL.
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=BUILD)
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.addClassCleanup(cls.server.server_close)
        cls.addClassCleanup(cls.thread.join, 5)
        cls.addClassCleanup(cls.server.shutdown)
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)
        cls.browser = cls.playwright.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    def setUp(self) -> None:
        self.context = self.browser.new_context()
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}/site/"

    def test_calculates_and_draws_both_quadrature_rules(self) -> None:
        self.page.goto(self.base_url)
        calculate = self.page.get_by_role("button", name="Integrate")
        expect(calculate).to_be_enabled(timeout=45_000)
        midpoint, trapezoid = (
            self.page.locator("#midpoint"),
            self.page.locator("#trapezoid"),
        )
        expect(midpoint).to_have_text("2.500798")
        expect(trapezoid).to_have_text("2.497933")
        plot = self.page.locator("#plot")
        initial = plot.evaluate("(canvas) => canvas.toDataURL()")

        self.page.get_by_label("Show on plot").select_option("trapezoids")
        self.assertNotEqual(plot.evaluate("(canvas) => canvas.toDataURL()"), initial)
        self.page.get_by_role("spinbutton", name="Panels").fill("1")
        calculate.click()
        expect(midpoint).to_have_text("6.000000")
        expect(trapezoid).to_have_text("0.066654")
        self.page.get_by_label("Start x").fill("3")
        self.page.get_by_label("End x").fill("-3")
        calculate.click()
        expect(midpoint).to_have_text("-6.000000")
        expect(trapezoid).to_have_text("-0.066654")

        self.page.get_by_label("Scale b").fill("0")
        calculate.click()
        expect(self.page.get_by_role("alert")).to_contain_text("nonzero value")
        self.page.get_by_label("Scale b").fill("2")
        calculate.click()
        expect(self.page.get_by_role("alert")).to_be_hidden()
        expect(self.page.get_by_role("status")).to_have_text("Calculated.")
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.wait_for_function("""() => {
            const plot = document.querySelector("#plot");
            const width = plot.getBoundingClientRect().width;
            return plot.width === Math.round(width * devicePixelRatio);
        }""")
        self.assertTrue(
            self.page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        )

    def test_runtime_failure_shows_retry(self) -> None:
        self.page.route("**/vendor/pyodide.js", lambda route: route.abort())
        self.page.goto(self.base_url)
        expect(self.page.get_by_role("alert")).to_contain_text("Python could not load")
        expect(self.page.get_by_role("button", name="Reload")).to_be_visible()
