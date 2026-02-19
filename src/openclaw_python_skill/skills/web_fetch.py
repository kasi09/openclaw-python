"""Web Fetch Skill - Basic web fetching for OpenClaw."""

import re
from typing import Any

import httpx

from openclaw_python_skill.skill import Skill

_DEFAULT_HEADERS = {"User-Agent": "OpenClaw/1.0"}
_DEFAULT_TIMEOUT = 10


class WebFetchSkill(Skill):
    """Fetch web pages and extract basic content using httpx and regex.

    Provides actions for:
    - fetch: Retrieve a URL and return status, headers, and content
    - extract_links: Extract all hyperlinks from a page
    - extract_text: Strip HTML tags and return plain text
    """

    def __init__(self) -> None:
        super().__init__(name="web-fetch", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        url = parameters.get("url")
        if not url:
            raise ValueError("Missing required parameter: url")

        timeout = parameters.get("timeout", _DEFAULT_TIMEOUT)
        headers = {**_DEFAULT_HEADERS, **parameters.get("headers", {})}

        if action == "fetch":
            return self._fetch(url, headers, timeout)
        elif action == "extract_links":
            return self._extract_links(url, headers, timeout)
        elif action == "extract_text":
            return self._extract_text(url, headers, timeout)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _get(self, url: str, headers: dict[str, str], timeout: int) -> httpx.Response:
        """Perform a GET request."""
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
            return client.get(url)

    def _fetch(self, url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
        """Fetch a URL and return response details."""
        response = self._get(url, headers, timeout)
        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", ""),
            "content": response.text,
            "content_length": len(response.text),
        }

    def _extract_links(self, url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
        """Extract all <a href="..."> links from a page."""
        response = self._get(url, headers, timeout)
        pattern = r'<a\s+[^>]*href=["\']([^"\']+)["\']'
        links = re.findall(pattern, response.text, re.IGNORECASE)
        return {
            "url": str(response.url),
            "links": links,
            "link_count": len(links),
        }

    def _extract_text(self, url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
        """Strip HTML tags and return plain text."""
        response = self._get(url, headers, timeout)
        # Remove script and style blocks
        text = re.sub(
            r"<(script|style)[^>]*>.*?</\1>", "", response.text, flags=re.DOTALL | re.IGNORECASE
        )
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return {
            "url": str(response.url),
            "text": text,
            "text_length": len(text),
        }
