"""Data models for OpenClaw Python Skills."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


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
