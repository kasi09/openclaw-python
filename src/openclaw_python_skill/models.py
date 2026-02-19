"""Data models for OpenClaw Python Skills."""

from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Type alias for pipeline parameter mapper functions.
ParameterMapper = Callable[[Optional[dict[str, Any]]], dict[str, Any]]


class SkillInput(BaseModel):
    """Input model for skill execution."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action": "analyze_text",
                "parameters": {"text": "Hello world"},
                "context": {"user_id": "user123"},
            }
        }
    )

    action: str = Field(..., description="The action to perform")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    context: Optional[dict[str, Any]] = Field(None, description="Execution context")


class SkillOutput(BaseModel):
    """Output model for skill execution."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "result": {"word_count": 2, "char_count": 11},
                "metadata": {"execution_time_ms": 1.5},
            }
        }
    )

    success: bool = Field(..., description="Whether the action succeeded")
    result: Optional[dict[str, Any]] = Field(None, description="Action result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PipelineStep(BaseModel):
    """Definition of a single step in a SkillPipeline."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    skill_name: Optional[str] = Field(
        None, description="Name of the skill to look up in the registry"
    )
    skill: Optional[Any] = Field(None, description="Direct Skill instance")
    action: str = Field(..., description="The action to invoke on the skill")
    mapper: Optional[ParameterMapper] = Field(
        None,
        description="Function that maps previous step's result to this step's parameters",
    )

    @model_validator(mode="after")
    def _check_skill_reference(self) -> "PipelineStep":
        if self.skill_name is None and self.skill is None:
            raise ValueError("Either 'skill_name' or 'skill' must be provided")
        if self.skill_name is not None and self.skill is not None:
            raise ValueError("Provide either 'skill_name' or 'skill', not both")
        return self


class StepResult(BaseModel):
    """Result from a single pipeline step execution."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    step_index: int = Field(..., description="Zero-based index of this step")
    skill_name: str = Field(..., description="Name of the skill that was executed")
    action: str = Field(..., description="The action that was called")
    output: SkillOutput = Field(..., description="The full SkillOutput from this step")


class PipelineResult(BaseModel):
    """Aggregated result from a full pipeline execution."""

    success: bool = Field(..., description="True if all steps succeeded")
    steps: list[StepResult] = Field(default_factory=list, description="Per-step results")
    final_result: Optional[dict[str, Any]] = Field(
        None, description="Result dict from the last successful step"
    )
    error: Optional[str] = Field(None, description="Error message if pipeline failed")
    failed_step: Optional[int] = Field(None, description="Index of the failed step")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Pipeline-level metadata")
