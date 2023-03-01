import glob
import os
import zipfile
import asyncio
from io import BytesIO
import asyncpraw
from praw.models import MoreComments
import json
from pathlib import Path
from playwright.async_api import ViewportSize, async_playwright

from config import settings


def login():
    try:
        reddit = asyncpraw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret.get_secret_value(),
            user_agent="ThreadTrawler",
        )

        print("Logged in to Reddit successfully!")
        return reddit
    except Exception as e:
        return e


def get_comments(thread_id):
    topn = 10
    comments = []
    for top_level_comment in thread_id.comments:
        if len(comments) == topn:
            break
        if isinstance(top_level_comment, MoreComments):
            continue
        comments.append(top_level_comment)

    chosen_comments = comments
    print(f"{len(chosen_comments)} comments are chosen")
    return chosen_comments


async def make_thread_screenshots(
    reddit_thread, reddit_comments, screenshot_num: int, theme="dark"
):
    # settings values
    W = 1080
    H = 1920

    screenshot_num: int
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
        # set the theme and disable non-essential cookies
        if theme == "dark":
            cookie_file = open(
                Path("../assets/cookie-dark-mode.json"), encoding="utf-8"
            )

        cookies = json.load(cookie_file)
        cookie_file.close()

        await context.add_cookies(cookies)  # load preference cookies

        # Get the thread screenshot
        page = await context.new_page()
        await page.goto("https://www.reddit.com" + reddit_thread.permalink, timeout=0)
        await page.set_viewport_size(ViewportSize(width=W, height=H))

        await page.locator('[data-test-id="post-content"]').screenshot(
            path=Path("../data/thread_previews/title.png")
        )

        for idx, comment in enumerate(reddit_comments):
            if await page.locator('[data-testid="content-gate"]').is_visible():
                await page.locator('[data-testid="content-gate"] button').click()

            await page.goto(f"https://reddit.com{comment.permalink}", timeout=0)

            try:
                await page.locator(f"#t1_{comment.id}").screenshot(
                    path=Path(f"../data/thread_previews/{idx}.png")
                )
            except TimeoutError:
                print("TimeoutError: Skipping screenshot...")
                continue

        # close browser instance when we are done using it
        await browser.close()

    print("Screenshots downloaded Successfully.")


def clean_dir():
    try:
        for file in glob.glob("../data/thread_previews/*.png"):
            os.remove(file)
    except Exception as e:
        print(e)


def zip_images():
    s = BytesIO()
    with zipfile.ZipFile(s, mode="w", compression=zipfile.ZIP_DEFLATED) as temp_zip:
        for screenshot in glob.glob("../data/thread_previews/*.png"):
            fdir, fname = os.path.split(screenshot)
            temp_zip.write(screenshot, fname)
    return s.getvalue()


async def create_screenshots(rt_url):
    clean_dir()
    my_reddit = login()
    thread = await my_reddit.submission(url=rt_url)
    comments = get_comments(thread)
    await make_thread_screenshots(thread, comments, 10)
    return zip_images()


async def main():
    await create_screenshots(
        "https://www.reddit.com/r/StableDiffusion/comments/11ezysg/experimenting_with_darkness_illuminati_diffusion/"
    )


if __name__ == "__main__":
    asyncio.run(main())
