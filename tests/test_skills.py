"""Tests for OpenClaw Python Skills."""

import pytest

from openclaw_python_skill import SkillInput
from openclaw_python_skill.skills import TextAnalyzerSkill


@pytest.fixture
def skill():
    """Create a text analyzer skill instance."""
    return TextAnalyzerSkill()


@pytest.mark.asyncio
async def test_text_stats(skill):
    """Test text statistics analysis."""
    input_data = SkillInput(action="text_stats", parameters={"text": "Hello world example text."})

    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["word_count"] == 4
    assert output.result["sentence_count"] == 1
    assert output.error is None


@pytest.mark.asyncio
async def test_text_sentiment(skill):
    """Test sentiment analysis."""
    input_data = SkillInput(
        action="text_sentiment", parameters={"text": "I love this! It's great and excellent!"}
    )

    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["sentiment"] == "positive"
    assert output.result["positive_words"] > 0
    assert output.error is None


@pytest.mark.asyncio
async def test_text_patterns(skill):
    """Test pattern detection."""
    input_data = SkillInput(
        action="text_patterns",
        parameters={"text": "Contact us at support@openclaw.ai or visit https://openclaw.ai"},
    )

    output = await skill.execute(input_data)

    assert output.success is True
    assert len(output.result["emails"]) > 0
    assert len(output.result["urls"]) > 0


@pytest.mark.asyncio
async def test_missing_parameter(skill):
    """Test error handling for missing parameters."""
    input_data = SkillInput(action="text_stats", parameters={})

    output = await skill.execute(input_data)

    assert output.success is False
    assert output.error is not None


@pytest.mark.asyncio
async def test_unknown_action(skill):
    """Test error handling for unknown action."""
    input_data = SkillInput(action="unknown_action", parameters={"text": "test"})

    output = await skill.execute(input_data)

    assert output.success is False
    assert "Unknown action" in output.error


def test_skill_describe(skill):
    """Test skill metadata."""
    metadata = skill.describe()

    assert metadata["name"] == "text-analyzer"
    assert metadata["version"] == "1.0.0"
    assert metadata["description"] != ""
