"""Tests for SkillPipeline."""

from typing import Any

import pytest

from openclaw_python_skill import (
    PipelineResult,
    Skill,
    SkillPipeline,
    SkillRegistry,
)
from openclaw_python_skill.models import PipelineStep

# --- Test skills ---


class UpperCaseSkill(Skill):
    """Converts text to uppercase."""

    def __init__(self):
        super().__init__(name="upper", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action == "transform":
            return {"text": parameters["text"].upper()}
        raise ValueError(f"Unknown action: {action}")


class WordCountSkill(Skill):
    """Counts words in text."""

    def __init__(self):
        super().__init__(name="word-count", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action == "count":
            text = parameters["text"]
            return {"word_count": len(text.split()), "text": text}
        raise ValueError(f"Unknown action: {action}")


class FailingSkill(Skill):
    """Always fails."""

    def __init__(self):
        super().__init__(name="failing", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("Intentional failure")


@pytest.fixture
def registry():
    reg = SkillRegistry()
    reg.register(UpperCaseSkill())
    reg.register(WordCountSkill())
    reg.register(FailingSkill())
    return reg


@pytest.fixture
def upper_skill():
    return UpperCaseSkill()


@pytest.fixture
def word_count_skill():
    return WordCountSkill()


# --- Construction & fluent API ---


def test_empty_pipeline():
    pipeline = SkillPipeline(name="empty")
    assert len(pipeline) == 0
    assert pipeline.name == "empty"
    assert pipeline.steps == []


def test_add_step_returns_self(upper_skill):
    pipeline = SkillPipeline()
    result = pipeline.add_step(skill=upper_skill, action="transform")
    assert result is pipeline
    assert len(pipeline) == 1


def test_fluent_chaining(upper_skill, word_count_skill):
    pipeline = (
        SkillPipeline()
        .add_step(skill=upper_skill, action="transform")
        .add_step(skill=word_count_skill, action="count")
    )
    assert len(pipeline) == 2


# --- Execution with direct skill instances ---


@pytest.mark.asyncio
async def test_single_step(upper_skill):
    pipeline = SkillPipeline().add_step(skill=upper_skill, action="transform")
    result = await pipeline.execute({"text": "hello world"})

    assert isinstance(result, PipelineResult)
    assert result.success is True
    assert result.final_result["text"] == "HELLO WORLD"
    assert len(result.steps) == 1
    assert result.failed_step is None
    assert result.error is None


@pytest.mark.asyncio
async def test_two_steps(upper_skill, word_count_skill):
    pipeline = (
        SkillPipeline()
        .add_step(skill=upper_skill, action="transform")
        .add_step(skill=word_count_skill, action="count")
    )
    result = await pipeline.execute({"text": "hello world"})

    assert result.success is True
    assert result.final_result["word_count"] == 2
    assert result.final_result["text"] == "HELLO WORLD"
    assert len(result.steps) == 2


@pytest.mark.asyncio
async def test_empty_pipeline_execution():
    pipeline = SkillPipeline()
    result = await pipeline.execute({"text": "ignored"})

    assert result.success is True
    assert result.final_result is None
    assert len(result.steps) == 0


# --- Execution with registry ---


@pytest.mark.asyncio
async def test_registry_based_step(registry):
    pipeline = SkillPipeline(registry=registry).add_step(skill_name="upper", action="transform")
    result = await pipeline.execute({"text": "hello"})

    assert result.success is True
    assert result.final_result["text"] == "HELLO"


@pytest.mark.asyncio
async def test_mixed_registry_and_direct(registry, word_count_skill):
    pipeline = (
        SkillPipeline(registry=registry)
        .add_step(skill_name="upper", action="transform")
        .add_step(skill=word_count_skill, action="count")
    )
    result = await pipeline.execute({"text": "hello world"})

    assert result.success is True
    assert result.final_result["word_count"] == 2


@pytest.mark.asyncio
async def test_registry_missing_skill(registry):
    pipeline = SkillPipeline(registry=registry).add_step(skill_name="nonexistent", action="do")
    result = await pipeline.execute({})

    assert result.success is False
    assert result.failed_step == 0
    assert "resolve skill" in result.error.lower() or "no skill registered" in result.error.lower()


@pytest.mark.asyncio
async def test_skill_name_without_registry():
    pipeline = SkillPipeline().add_step(skill_name="upper", action="transform")
    result = await pipeline.execute({"text": "hello"})

    assert result.success is False
    assert result.failed_step == 0
    assert "registry" in result.error.lower()


# --- Mapper functions ---


@pytest.mark.asyncio
async def test_mapper_transforms_parameters(upper_skill, word_count_skill):
    pipeline = (
        SkillPipeline()
        .add_step(skill=word_count_skill, action="count")
        .add_step(
            skill=upper_skill,
            action="transform",
            mapper=lambda prev: {"text": f"Words: {prev['word_count']}"},
        )
    )
    result = await pipeline.execute({"text": "hello world foo"})

    assert result.success is True
    assert result.final_result["text"] == "WORDS: 3"


@pytest.mark.asyncio
async def test_mapper_failure(upper_skill):
    def bad_mapper(prev):  # type: ignore[no-untyped-def]
        raise ValueError("mapper broke")

    pipeline = (
        SkillPipeline()
        .add_step(skill=upper_skill, action="transform")
        .add_step(skill=upper_skill, action="transform", mapper=bad_mapper)
    )
    result = await pipeline.execute({"text": "hello"})

    assert result.success is False
    assert result.failed_step == 1
    assert "mapper" in result.error.lower()
    assert len(result.steps) == 1  # only first step completed


# --- Fail-fast ---


@pytest.mark.asyncio
async def test_fail_fast(upper_skill):
    failing = FailingSkill()
    pipeline = (
        SkillPipeline()
        .add_step(skill=upper_skill, action="transform")
        .add_step(skill=failing, action="anything")
        .add_step(skill=upper_skill, action="transform")  # should not execute
    )
    result = await pipeline.execute({"text": "hello"})

    assert result.success is False
    assert result.failed_step == 1
    assert len(result.steps) == 2  # steps 0 and 1, step 2 skipped
    assert result.steps[0].output.success is True
    assert result.steps[1].output.success is False


# --- Metadata ---


@pytest.mark.asyncio
async def test_metadata_total_time(upper_skill, word_count_skill):
    pipeline = (
        SkillPipeline(name="timed")
        .add_step(skill=upper_skill, action="transform")
        .add_step(skill=word_count_skill, action="count")
    )
    result = await pipeline.execute({"text": "hello world"})

    assert result.metadata["pipeline_name"] == "timed"
    assert result.metadata["total_execution_time_ms"] >= 0
    assert result.metadata["step_count"] == 2
    assert result.metadata["steps_executed"] == 2
    assert len(result.metadata["per_step_times"]) == 2


@pytest.mark.asyncio
async def test_metadata_per_step(upper_skill):
    pipeline = SkillPipeline().add_step(skill=upper_skill, action="transform")
    result = await pipeline.execute({"text": "hello"})

    step_time = result.metadata["per_step_times"][0]
    assert step_time["step_index"] == 0
    assert step_time["skill_name"] == "upper"
    assert step_time["action"] == "transform"
    assert step_time["execution_time_ms"] >= 0


@pytest.mark.asyncio
async def test_metadata_on_failure():
    pipeline = SkillPipeline(name="fail-pipe").add_step(skill=FailingSkill(), action="go")
    result = await pipeline.execute({})

    assert result.metadata["pipeline_name"] == "fail-pipe"
    assert result.metadata["steps_executed"] == 1


# --- describe() ---


def test_describe(upper_skill, word_count_skill):
    pipeline = (
        SkillPipeline(name="my-pipeline")
        .add_step(skill=upper_skill, action="transform")
        .add_step(skill=word_count_skill, action="count", mapper=lambda prev: prev)
    )
    desc = pipeline.describe()

    assert desc["name"] == "my-pipeline"
    assert desc["step_count"] == 2
    assert desc["steps"][0]["skill"] == "upper"
    assert desc["steps"][0]["action"] == "transform"
    assert desc["steps"][0]["has_mapper"] is False
    assert desc["steps"][1]["has_mapper"] is True


def test_describe_with_registry_names(registry):
    pipeline = SkillPipeline(registry=registry, name="reg-pipe").add_step(
        skill_name="upper", action="transform"
    )
    desc = pipeline.describe()
    assert desc["steps"][0]["skill"] == "upper"


# --- Edge cases ---


@pytest.mark.asyncio
async def test_none_initial_parameters(upper_skill):
    pipeline = SkillPipeline().add_step(skill=upper_skill, action="transform")
    result = await pipeline.execute()

    assert result.success is False
    assert result.failed_step == 0


@pytest.mark.asyncio
async def test_step_with_none_result():
    class NoneResultSkill(Skill):
        def __init__(self):
            super().__init__(name="none-result")

        def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
            return None  # type: ignore[return-value]

    pipeline = (
        SkillPipeline()
        .add_step(skill=NoneResultSkill(), action="go")
        .add_step(skill=NoneResultSkill(), action="go")
    )
    result = await pipeline.execute({})
    assert result.success is True


@pytest.mark.asyncio
async def test_context_passed_to_steps(upper_skill):
    pipeline = SkillPipeline().add_step(skill=upper_skill, action="transform")
    result = await pipeline.execute({"text": "hello"}, context={"user": "test"})
    assert result.success is True


# --- PipelineStep validation ---


def test_pipeline_step_requires_skill_reference():
    with pytest.raises(ValueError, match="skill_name.*skill"):
        PipelineStep(action="test")


def test_pipeline_step_rejects_both_references(upper_skill):
    with pytest.raises(ValueError, match="not both"):
        PipelineStep(skill=upper_skill, skill_name="upper", action="test")
