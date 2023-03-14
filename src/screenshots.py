import os
import zipfile
import asyncio
from io import BytesIO
import json
from playwright.async_api import ViewportSize, async_playwright

from settings import settings


async def create_screenshots(thread_url, comments):
    # settings values
    W = 1080
    H = 1920

    screenshots = []
    async with async_playwright() as p:
        print("Launching Headless Browser...")

        # headless=False #to check for chrome view
        browser = await p.chromium.launch(headless=True)
        # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
        # When the dsf is 1, the width of the screenshot is 600 pixels
        # So we need a dsf such that the width of the screenshot is greater than the final resolution of the video
        dsf = (W // 600) + 1

        context = await browser.new_context(
            locale="en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=W, height=H),
            device_scale_factor=dsf,
        )
        cookie_file = open(
            "../assets/cookie-dark-mode.json",
            encoding="utf-8",
        )

        cookies = json.load(cookie_file)
        cookie_file.close()

        await context.add_cookies(cookies)  # load preference cookies

        # Get the thread screenshot
        page = await context.new_page()
        await page.goto(thread_url, timeout=0)
        await page.set_viewport_size(ViewportSize(width=W, height=H))

        screenshots.append(
            await page.locator('[data-test-id="post-content"]').screenshot()
        )

        for i, comment in enumerate(comments):
            if await page.locator('[data-testid="content-gate"]').is_visible():
                await page.locator('[data-testid="content-gate"] button').click()

            await page.goto(f"https://reddit.com{comment.permalink}", timeout=0)

            try:
                screenshots.append(await page.locator(f"#t1_{comment.id}").screenshot())
            except TimeoutError:
                print("TimeoutError: Skipping screenshot...")
                continue

        # close browser instance when we are done using it
        await browser.close()

    print("Screenshots made Successfully.")
    return screenshots


def zip_screenshots(screenshots):
    s = BytesIO()
    with zipfile.ZipFile(s, mode="w", compression=zipfile.ZIP_DEFLATED) as temp_zip:
        i = 0
        for screenshot in screenshots:
            temp_zip.writestr(f"thread_comment_{i}.png", BytesIO(screenshot).read())
            i += 1
    return s.getvalue()


async def main():
    await create_screenshots(settings.default_thread_url)


if __name__ == "__main__":
    asyncio.run(main())
