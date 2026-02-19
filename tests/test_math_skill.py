"""Tests for MathSkill."""

import math

import pytest

from openclaw_python_skill import SkillInput
from openclaw_python_skill.skills import MathSkill


@pytest.fixture
def skill():
    return MathSkill()


# --- evaluate ---


@pytest.mark.asyncio
async def test_evaluate_basic_arithmetic(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "2 + 3 * 4"})
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 14.0


@pytest.mark.asyncio
async def test_evaluate_parentheses(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "(2 + 3) * 4"})
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 20.0


@pytest.mark.asyncio
async def test_evaluate_power(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "2 ** 10"})
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 1024.0


@pytest.mark.asyncio
async def test_evaluate_math_functions(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "sqrt(16)"})
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 4.0


@pytest.mark.asyncio
async def test_evaluate_pi(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "pi * 2"})
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == pytest.approx(math.pi * 2)


@pytest.mark.asyncio
async def test_evaluate_negative_number(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "-5 + 3"})
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == -2.0


@pytest.mark.asyncio
async def test_evaluate_division_by_zero(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "1 / 0"})
    output = await skill.execute(input_data)

    assert output.success is False
    assert output.error is not None


@pytest.mark.asyncio
async def test_evaluate_invalid_expression(skill):
    input_data = SkillInput(action="evaluate", parameters={"expression": "2 +"})
    output = await skill.execute(input_data)

    assert output.success is False


@pytest.mark.asyncio
async def test_evaluate_code_injection(skill):
    input_data = SkillInput(
        action="evaluate", parameters={"expression": "__import__('os').system('ls')"}
    )
    output = await skill.execute(input_data)

    assert output.success is False


@pytest.mark.asyncio
async def test_evaluate_missing_expression(skill):
    input_data = SkillInput(action="evaluate", parameters={})
    output = await skill.execute(input_data)

    assert output.success is False
    assert "expression" in output.error.lower()


# --- convert_units ---


@pytest.mark.asyncio
async def test_convert_length_m_to_km(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"value": 1500, "from_unit": "m", "to_unit": "km"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 1.5


@pytest.mark.asyncio
async def test_convert_weight_kg_to_lb(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"value": 1, "from_unit": "kg", "to_unit": "lb"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == pytest.approx(2.204623, rel=1e-3)


@pytest.mark.asyncio
async def test_convert_temperature_c_to_f(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"value": 100, "from_unit": "C", "to_unit": "F"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 212.0


@pytest.mark.asyncio
async def test_convert_temperature_f_to_c(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"value": 32, "from_unit": "F", "to_unit": "C"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_convert_temperature_k_to_c(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"value": 273.15, "from_unit": "K", "to_unit": "C"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_convert_incompatible_units(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"value": 100, "from_unit": "m", "to_unit": "kg"},
    )
    output = await skill.execute(input_data)

    assert output.success is False
    assert "incompatible" in output.error.lower()


@pytest.mark.asyncio
async def test_convert_unknown_unit(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"value": 100, "from_unit": "m", "to_unit": "lightyear"},
    )
    output = await skill.execute(input_data)

    assert output.success is False
    assert "unknown unit" in output.error.lower()


@pytest.mark.asyncio
async def test_convert_missing_value(skill):
    input_data = SkillInput(
        action="convert_units",
        parameters={"from_unit": "m", "to_unit": "km"},
    )
    output = await skill.execute(input_data)

    assert output.success is False
    assert "value" in output.error.lower()


# --- statistics ---


@pytest.mark.asyncio
async def test_statistics_summary(skill):
    input_data = SkillInput(
        action="statistics",
        parameters={"numbers": [1, 2, 3, 4, 5]},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["count"] == 5
    assert output.result["mean"] == 3.0
    assert output.result["median"] == 3.0
    assert output.result["min"] == 1.0
    assert output.result["max"] == 5.0
    assert output.result["sum"] == 15.0


@pytest.mark.asyncio
async def test_statistics_mean(skill):
    input_data = SkillInput(
        action="statistics",
        parameters={"numbers": [10, 20, 30], "operation": "mean"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["operation"] == "mean"
    assert output.result["result"] == 20.0


@pytest.mark.asyncio
async def test_statistics_median(skill):
    input_data = SkillInput(
        action="statistics",
        parameters={"numbers": [1, 3, 5, 7], "operation": "median"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == 4.0


@pytest.mark.asyncio
async def test_statistics_stdev(skill):
    input_data = SkillInput(
        action="statistics",
        parameters={"numbers": [2, 4, 4, 4, 5, 5, 7, 9], "operation": "stdev"},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["result"] == pytest.approx(2.1380899, rel=1e-4)


@pytest.mark.asyncio
async def test_statistics_single_number(skill):
    input_data = SkillInput(
        action="statistics",
        parameters={"numbers": [42]},
    )
    output = await skill.execute(input_data)

    assert output.success is True
    assert output.result["mean"] == 42.0
    assert output.result["stdev"] == 0.0


@pytest.mark.asyncio
async def test_statistics_empty_list(skill):
    input_data = SkillInput(
        action="statistics",
        parameters={"numbers": []},
    )
    output = await skill.execute(input_data)

    assert output.success is False
    assert "non-empty" in output.error.lower()


@pytest.mark.asyncio
async def test_statistics_missing_numbers(skill):
    input_data = SkillInput(action="statistics", parameters={})
    output = await skill.execute(input_data)

    assert output.success is False
    assert "numbers" in output.error.lower()


@pytest.mark.asyncio
async def test_statistics_unknown_operation(skill):
    input_data = SkillInput(
        action="statistics",
        parameters={"numbers": [1, 2, 3], "operation": "mode"},
    )
    output = await skill.execute(input_data)

    assert output.success is False
    assert "unknown operation" in output.error.lower()


# --- General ---


@pytest.mark.asyncio
async def test_unknown_action(skill):
    input_data = SkillInput(action="invalid", parameters={})
    output = await skill.execute(input_data)

    assert output.success is False
    assert "Unknown action" in output.error


def test_describe(skill):
    meta = skill.describe()
    assert meta["name"] == "math"
    assert meta["version"] == "1.0.0"
