"""Tests for WebScraperSkill."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from openclaw_python_skill import SkillInput
from openclaw_python_skill.skills import WebScraperSkill

SAMPLE_HTML = """
<html>
<head>
    <title>Test Page Title</title>
    <meta name="description" content="A test page description.">
    <meta property="og:title" content="OG Test Title">
    <meta property="og:image" content="https://example.com/image.jpg">
    <meta property="og:type" content="website">
</head>
<body>
<h1>Main Heading</h1>
<p class="intro">First paragraph.</p>
<p class="intro">Second paragraph.</p>
<div class="content">
    <span>Nested text</span>
</div>
<a href="https://example.com" class="link">Example Link</a>
</body>
</html>
"""


def _mock_response(text: str = SAMPLE_HTML) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    resp.url = "https://example.com"
    return resp


def _mock_client_get(text: str = SAMPLE_HTML):
    """Create a patch for httpx.Client that returns a mock response."""
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = _mock_response(text)
    return patch("httpx.Client", return_value=mock_client)


@pytest.fixture
def skill():
    return WebScraperSkill()


# --- extract_meta ---


@pytest.mark.asyncio
async def test_extract_meta(skill):
    with _mock_client_get():
        input_data = SkillInput(action="extract_meta", parameters={"url": "https://example.com"})
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["title"] == "Test Page Title"
    assert output.result["description"] == "A test page description."
    assert output.result["og_tags"]["og:title"] == "OG Test Title"
    assert output.result["og_tags"]["og:image"] == "https://example.com/image.jpg"
    assert output.result["og_tags"]["og:type"] == "website"


@pytest.mark.asyncio
async def test_extract_meta_missing_tags(skill):
    html = "<html><head></head><body>No meta</body></html>"
    with _mock_client_get(html):
        input_data = SkillInput(action="extract_meta", parameters={"url": "https://example.com"})
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["title"] == ""
    assert output.result["description"] == ""
    assert output.result["og_tags"] == {}


# --- extract_elements ---


@pytest.mark.asyncio
async def test_extract_elements_by_class(skill):
    with _mock_client_get():
        input_data = SkillInput(
            action="extract_elements",
            parameters={"url": "https://example.com", "selector": "p.intro"},
        )
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["element_count"] == 2
    assert output.result["elements"][0]["tag"] == "p"
    assert output.result["elements"][0]["text"] == "First paragraph."
    assert output.result["elements"][1]["text"] == "Second paragraph."
    assert output.result["selector"] == "p.intro"


@pytest.mark.asyncio
async def test_extract_elements_nested(skill):
    with _mock_client_get():
        input_data = SkillInput(
            action="extract_elements",
            parameters={"url": "https://example.com", "selector": "div.content span"},
        )
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["element_count"] == 1
    assert output.result["elements"][0]["text"] == "Nested text"


@pytest.mark.asyncio
async def test_extract_elements_no_match(skill):
    with _mock_client_get():
        input_data = SkillInput(
            action="extract_elements",
            parameters={"url": "https://example.com", "selector": "div.nonexistent"},
        )
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["element_count"] == 0
    assert output.result["elements"] == []


@pytest.mark.asyncio
async def test_extract_elements_with_attrs(skill):
    with _mock_client_get():
        input_data = SkillInput(
            action="extract_elements",
            parameters={"url": "https://example.com", "selector": "a.link"},
        )
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["element_count"] == 1
    el = output.result["elements"][0]
    assert el["tag"] == "a"
    assert el["text"] == "Example Link"
    assert el["attrs"]["href"] == "https://example.com"


# --- Error handling ---


@pytest.mark.asyncio
async def test_missing_url(skill):
    input_data = SkillInput(action="extract_meta", parameters={})
    output = await skill.execute(input_data)

    assert output.success is False
    assert "url" in output.error.lower()


@pytest.mark.asyncio
async def test_missing_selector(skill):
    with _mock_client_get():
        input_data = SkillInput(
            action="extract_elements", parameters={"url": "https://example.com"}
        )
        output = await skill.execute(input_data)

    assert output.success is False
    assert "selector" in output.error.lower()


@pytest.mark.asyncio
async def test_unknown_action(skill):
    input_data = SkillInput(action="invalid", parameters={"url": "https://example.com"})
    output = await skill.execute(input_data)

    assert output.success is False
    assert "Unknown action" in output.error


@pytest.mark.asyncio
async def test_network_error(skill):
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.side_effect = httpx.ConnectError("Connection refused")

    with patch("httpx.Client", return_value=mock_client):
        input_data = SkillInput(
            action="extract_meta", parameters={"url": "https://unreachable.test"}
        )
        output = await skill.execute(input_data)

    assert output.success is False
    assert output.error is not None


# --- describe ---


def test_describe(skill):
    meta = skill.describe()
    assert meta["name"] == "web-scraper"
    assert meta["version"] == "1.0.0"
