
from urllib.parse import quote_plus, urlparse
from playwright.sync_api import sync_playwright
import webbrowser


def search_youtube(query):
    """Search YouTube and return relevant video results."""

    if not query or not query.strip():
        return {"success": False, "message": "Search query is empty."}

    search_url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query.strip())
    )

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.locator("a#video-title").first.wait_for(timeout=20000)

            results = page.locator("a#video-title").evaluate_all(
                """elements => elements.slice(0, 5).map(el => ({
                    title: (el.getAttribute('title') || el.innerText || '').trim(),
                    url: el.href
                }))"""
            )

            browser.close()

        # Keep only valid YouTube video links
        clean_results = []

        for item in results:
            parsed = urlparse(item["url"])

            if (
                item["title"]
                and parsed.hostname
                and parsed.hostname.endswith("youtube.com")
                and parsed.path == "/watch"
            ):
                clean_results.append(item)

        if not clean_results:
            return {
                "success": False,
                "message": "No YouTube video results were found."
            }

        return {
            "success": True,
            "query": query,
            "results": clean_results
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"YouTube search failed: {str(error)}"
        }


def open_youtube_video(url):
    """Open a validated YouTube video in the default browser."""

    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or parsed.hostname not in ("www.youtube.com", "youtube.com")
        or parsed.path != "/watch"
    ):
        return {
            "success": False,
            "message": "Invalid YouTube video URL."
        }

    try:
        opened = webbrowser.open(url)

        return {
            "success": bool(opened),
            "message": (
                "YouTube video opening requested."
                if opened else "Could not open the video."
            ),
            "url": url
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }
