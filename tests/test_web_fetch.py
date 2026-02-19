"""Tests for WebFetchSkill."""

from unittest.mock import MagicMock, patch

import pytest

from openclaw_python_skill import SkillInput
from openclaw_python_skill.skills import WebFetchSkill

SAMPLE_HTML = """
<html>
<head><title>Test Page</title></head>
<body>
<h1>Hello World</h1>
<p>Some text here.</p>
<a href="https://example.com">Example</a>
<a href="/about">About</a>
<script>var x = 1;</script>
<style>body { color: red; }</style>
</body>
</html>
"""


def _mock_response(text: str = SAMPLE_HTML, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    resp.status_code = status_code
    resp.url = "https://example.com"
    resp.headers = {"content-type": "text/html; charset=utf-8"}
    return resp


@pytest.fixture
def skill():
    return WebFetchSkill()


# --- fetch ---


@pytest.mark.asyncio
async def test_fetch(skill):
    with patch.object(skill, "_get", return_value=_mock_response()):
        input_data = SkillInput(action="fetch", parameters={"url": "https://example.com"})
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["status_code"] == 200
    assert output.result["url"] == "https://example.com"
    assert "text/html" in output.result["content_type"]
    assert "<h1>Hello World</h1>" in output.result["content"]
    assert output.result["content_length"] > 0


@pytest.mark.asyncio
async def test_fetch_custom_timeout(skill):
    with patch.object(skill, "_get", return_value=_mock_response()) as mock_get:
        input_data = SkillInput(
            action="fetch", parameters={"url": "https://example.com", "timeout": 30}
        )
        output = await skill.execute(input_data)

    assert output.success is True
    mock_get.assert_called_once()
    # Verify timeout was passed through
    call_args = mock_get.call_args
    assert call_args[0][2] == 30  # third positional arg is timeout


# --- extract_links ---


@pytest.mark.asyncio
async def test_extract_links(skill):
    with patch.object(skill, "_get", return_value=_mock_response()):
        input_data = SkillInput(action="extract_links", parameters={"url": "https://example.com"})
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["link_count"] == 2
    assert "https://example.com" in output.result["links"]
    assert "/about" in output.result["links"]


@pytest.mark.asyncio
async def test_extract_links_no_links(skill):
    resp = _mock_response(text="<html><body>No links here</body></html>")
    with patch.object(skill, "_get", return_value=resp):
        input_data = SkillInput(action="extract_links", parameters={"url": "https://example.com"})
        output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["link_count"] == 0
    assert output.result["links"] == []


# --- extract_text ---


@pytest.mark.asyncio
async def test_extract_text(skill):
    with patch.object(skill, "_get", return_value=_mock_response()):
        input_data = SkillInput(action="extract_text", parameters={"url": "https://example.com"})
        output = await skill.execute(input_data)

    assert output.success is True
    assert "Hello World" in output.result["text"]
    assert "Some text here." in output.result["text"]
    # Script and style content should be removed
    assert "var x" not in output.result["text"]
    assert "color: red" not in output.result["text"]
    # No HTML tags
    assert "<h1>" not in output.result["text"]
    assert output.result["text_length"] > 0


# --- Error handling ---


@pytest.mark.asyncio
async def test_missing_url(skill):
    input_data = SkillInput(action="fetch", parameters={})
    output = await skill.execute(input_data)

    assert output.success is False
    assert "url" in output.error.lower()


@pytest.mark.asyncio
async def test_unknown_action(skill):
    input_data = SkillInput(action="invalid", parameters={"url": "https://example.com"})
    output = await skill.execute(input_data)

    assert output.success is False
    assert "Unknown action" in output.error


@pytest.mark.asyncio
async def test_network_error(skill):
    with patch.object(skill, "_get", side_effect=httpx.ConnectError("Connection refused")):
        input_data = SkillInput(action="fetch", parameters={"url": "https://unreachable.test"})
        output = await skill.execute(input_data)

    assert output.success is False
    assert output.error is not None


# --- describe ---


def test_describe(skill):
    meta = skill.describe()
    assert meta["name"] == "web-fetch"
    assert meta["version"] == "1.0.0"


import httpx  # noqa: E402
