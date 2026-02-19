"""Tests for base Skill class and models."""

from typing import Any

import pytest

from openclaw_python_skill import Skill, SkillInput, SkillOutput


class TestSkill(Skill):
    """Test implementation of Skill."""

    def __init__(self):
        super().__init__(name="test-skill", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action == "echo":
            return {"echoed": parameters.get("message", "")}
        elif action == "add":
            a = parameters.get("a", 0)
            b = parameters.get("b", 0)
            return {"result": a + b}
        raise ValueError(f"Unknown action: {action}")


@pytest.mark.asyncio
async def test_skill_execute_success():
    """Test successful skill execution."""
    skill = TestSkill()

    input_data = SkillInput(action="echo", parameters={"message": "hello"})

    output = await skill.execute(input_data)

    assert isinstance(output, SkillOutput)
    assert output.success is True
    assert output.result["echoed"] == "hello"
    assert output.error is None
    assert "execution_time_ms" in output.metadata


@pytest.mark.asyncio
async def test_skill_execute_math():
    """Test skill with numeric operation."""
    skill = TestSkill()

    input_data = SkillInput(action="add", parameters={"a": 5, "b": 3})

    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 8


@pytest.mark.asyncio
async def test_skill_execute_error():
    """Test skill error handling."""
    skill = TestSkill()

    input_data = SkillInput(action="unknown", parameters={})

    output = await skill.execute(input_data)

    assert output.success is False
    assert output.error is not None
    assert output.result is None


def test_skill_describe():
    """Test skill metadata description."""
    skill = TestSkill()

    metadata = skill.describe()

    assert metadata["name"] == "test-skill"
    assert metadata["version"] == "1.0.0"


def test_skill_input_model():
    """Test SkillInput Pydantic model."""
    input_data = SkillInput(action="test", parameters={"key": "value"})

    assert input_data.action == "test"
    assert input_data.parameters["key"] == "value"
    assert input_data.context is None


def test_skill_output_model():
    """Test SkillOutput Pydantic model."""
    output = SkillOutput(success=True, result={"data": "test"}, metadata={"source": "test"})

    assert output.success is True
    assert output.result["data"] == "test"
    assert output.error is None
    assert output.metadata["source"] == "test"

    # Test JSON serialization
    json_data = output.model_dump_json()
    assert "success" in json_data
    assert "result" in json_data
