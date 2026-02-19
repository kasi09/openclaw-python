"""Web Scraper Skill - Advanced web scraping with BeautifulSoup for OpenClaw."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from openclaw_python_skill.skill import Skill

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

_DEFAULT_HEADERS = {"User-Agent": "OpenClaw/1.0"}
_DEFAULT_TIMEOUT = 10


def _import_bs4() -> type:
    """Lazy-import BeautifulSoup, raising a clear error if not installed."""
    try:
        from bs4 import BeautifulSoup  # noqa: N812

        return BeautifulSoup
    except ImportError as err:
        raise ImportError(
            "WebScraperSkill requires beautifulsoup4. "
            "Install it with: pip install openclaw-python-skill[scraper]"
        ) from err


class WebScraperSkill(Skill):
    """Scrape web pages using BeautifulSoup for structured extraction.

    Provides actions for:
    - extract_meta: Extract title, meta description, and Open Graph tags
    - extract_elements: Extract elements matching a CSS selector
    """

    def __init__(self) -> None:
        _import_bs4()  # fail fast if bs4 is not installed
        super().__init__(name="web-scraper", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        url = parameters.get("url")
        if not url:
            raise ValueError("Missing required parameter: url")

        timeout = parameters.get("timeout", _DEFAULT_TIMEOUT)
        headers = {**_DEFAULT_HEADERS, **parameters.get("headers", {})}

        if action == "extract_meta":
            return self._extract_meta(url, headers, timeout)
        elif action == "extract_elements":
            selector = parameters.get("selector")
            if not selector:
                raise ValueError("Missing required parameter: selector")
            return self._extract_elements(url, headers, timeout, selector)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _get_soup(
        self, url: str, headers: dict[str, str], timeout: int
    ) -> tuple[BeautifulSoup, str]:
        """Fetch a URL and return a BeautifulSoup object and final URL."""
        soup_cls = _import_bs4()
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
        return soup_cls(response.text, "html.parser"), str(response.url)

    def _extract_meta(self, url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
        """Extract title, meta description, and Open Graph tags."""
        soup, final_url = self._get_soup(url, headers, timeout)

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag.get("content", "") if desc_tag else ""  # type: ignore[union-attr]

        og_tags: dict[str, str] = {}
        for tag in soup.find_all("meta", attrs={"property": True}):
            prop = tag.get("property", "")
            if isinstance(prop, str) and prop.startswith("og:"):
                og_tags[prop] = tag.get("content", "")

        return {
            "url": final_url,
            "title": title,
            "description": description,
            "og_tags": og_tags,
        }

    def _extract_elements(
        self,
        url: str,
        headers: dict[str, str],
        timeout: int,
        selector: str,
    ) -> dict[str, Any]:
        """Extract elements matching a CSS selector."""
        soup, final_url = self._get_soup(url, headers, timeout)
        elements = soup.select(selector)

        results = []
        for el in elements:
            results.append(
                {
                    "tag": el.name,
                    "text": el.get_text(strip=True),
                    "attrs": dict(el.attrs),
                }
            )

        return {
            "url": final_url,
            "selector": selector,
            "elements": results,
            "element_count": len(results),
        }
