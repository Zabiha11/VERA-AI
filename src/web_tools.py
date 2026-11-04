
from urllib.parse import quote_plus, urlparse, urljoin
from ipaddress import ip_address
from playwright.sync_api import sync_playwright
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# URL VALIDATION
# --------------------------------------------------

def is_public_web_url(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        host = parsed.hostname

        if not host:
            return False

        if host.lower() in ("localhost",):
            return False

        try:
            address = ip_address(host)
            if not address.is_global:
                return False
        except ValueError:
            if "." not in host:
                return False

        return True

    except Exception:
        return False


# --------------------------------------------------
# TOOL 1: WEB SEARCH
# --------------------------------------------------


def search_web(query):

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "success": False,
            "message": "Tavily API key is not configured."
        }

    if not query or not query.strip():
        return {
            "success": False,
            "message": "Search query is empty."
        }

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query.strip(),
                "search_depth": "basic",
                "max_results": 7,
                "include_answer": False
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        results = []

        for item in data.get("results", []):
            url = item.get("url", "")

            if not is_public_web_url(url):
                continue

            results.append({
                "title": item.get("title", ""),
                "url": url,
                "snippet": item.get("content", "")[:1000]
            })

        return {
            "success": bool(results),
            "query": query,
            "results": results,
            "message": (
                "Search completed."
                if results else "No search results found."
            )
        }

    except requests.Timeout:
        return {
            "success": False,
            "message": "Search timed out. Please try again."
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "message": f"Search API error: {str(error)}"
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }

# --------------------------------------------------
# TOOL 2: READ A WEBPAGE
# --------------------------------------------------

def read_webpage(url):
    if not is_public_web_url(url):
        return {
            "success": False,
            "message": "Invalid or unsupported public webpage URL."
        }

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # Validate the final URL after redirects
            final_url = page.url

            if not is_public_web_url(final_url):
                browser.close()
                return {
                    "success": False,
                    "message": "Navigation redirected to an unsupported address."
                }

            if response and response.status >= 400:
                browser.close()
                return {
                    "success": False,
                    "message": f"Website returned HTTP {response.status}."
                }

            page.locator("body").wait_for(timeout=10000)

            title = page.title()

            # Remove irrelevant page elements
            page.evaluate("""
                () => {
                    document.querySelectorAll(
                        'script, style, nav, footer, header, '
                        + 'noscript, iframe, svg'
                    ).forEach(el => el.remove());
                }
            """)

            text = page.locator("body").inner_text(
                timeout=10000
            )

            browser.close()

        text = text.strip()

        return {
            "success": bool(text),
            "title": title,
            "url": final_url,
            "content": text[:15000],
            "truncated": len(text) > 15000
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"Page reading failed: {str(error)}"
        }


# --------------------------------------------------
# TOOL 3: OPEN A SEARCH RESULT
# --------------------------------------------------

def open_search_result(url):
    if not is_public_web_url(url):
        return {
            "success": False,
            "message": "Invalid or unsupported public webpage URL."
        }

    try:
        # Reuse the existing default browser
        import webbrowser

        opened = webbrowser.open(url)

        return {
            "success": bool(opened),
            "message": (
                "Search result opening requested."
                if opened else "Could not open the webpage."
            ),
            "url": url
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }
