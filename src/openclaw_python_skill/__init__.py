"""
OpenClaw Python Skills - Extensible Python-based skills for OpenClaw AI Assistant.

This package provides a framework for building Python-based skills that integrate
with OpenClaw, enabling custom functionality and integrations.
"""

from .models import PipelineResult, PipelineStep, SkillInput, SkillOutput, StepResult
from .pipeline import SkillPipeline
from .registry import SkillRegistry, get_global_registry
from .skill import Skill

__version__ = "0.1.0"
__all__ = [
    "PipelineResult",
    "PipelineStep",
    "Skill",
    "SkillInput",
    "SkillOutput",
    "SkillPipeline",
    "SkillRegistry",
    "StepResult",
    "get_global_registry",
]
