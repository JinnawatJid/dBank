from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:3000")

        # Fill in the input field
        page.fill("input[type='text']", "Can you check the top root causes for issues based on recent data?")

        # Click the send button (you might need to adjust the selector)
        page.click("button:has-text('Send')")

        # Wait for the AI response to appear
        time.sleep(15)  # Wait for API call to complete

        page.screenshot(path="e2e_screenshot_flash2.png")
        browser.close()

if __name__ == "__main__":
    run()
