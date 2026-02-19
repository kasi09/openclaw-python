"""Skill Pipeline for composing skills sequentially."""

import time
from typing import Any, Optional

from .models import (
    ParameterMapper,
    PipelineResult,
    PipelineStep,
    SkillInput,
    StepResult,
)
from .registry import SkillRegistry
from .skill import Skill


class SkillPipeline:
    """Chain multiple skills together in a sequential pipeline.

    Each step's output feeds into the next step's input via an optional
    mapper function. If no mapper is provided, the previous step's result
    dict is passed through as-is as the next step's parameters.

    Example::

        pipeline = (
            SkillPipeline(registry=registry)
            .add_step(skill_name="text-analyzer", action="text_stats")
            .add_step(
                skill_name="text-analyzer",
                action="text_sentiment",
                mapper=lambda prev: {"text": prev["original_text"]},
            )
        )
        result = await pipeline.execute({"text": "Hello world!"})
    """

    def __init__(
        self,
        registry: Optional[SkillRegistry] = None,
        name: str = "pipeline",
    ) -> None:
        self._registry = registry
        self._name = name
        self._steps: list[PipelineStep] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def steps(self) -> list[PipelineStep]:
        return list(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def add_step(
        self,
        *,
        skill: Optional[Skill] = None,
        skill_name: Optional[str] = None,
        action: str,
        mapper: Optional[ParameterMapper] = None,
    ) -> "SkillPipeline":
        """Add a step to the pipeline. Returns self for fluent chaining."""
        step = PipelineStep(
            skill=skill,
            skill_name=skill_name,
            action=action,
            mapper=mapper,
        )
        self._steps.append(step)
        return self

    def _resolve_skill(self, step: PipelineStep) -> Skill:
        """Resolve a PipelineStep to a concrete Skill instance."""
        if step.skill is not None:
            return step.skill
        if self._registry is None:
            raise ValueError(
                f"Step references skill '{step.skill_name}' by name, "
                "but no SkillRegistry was provided to the pipeline."
            )
        return self._registry.get(step.skill_name)  # type: ignore[arg-type]

    async def execute(
        self,
        initial_parameters: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> PipelineResult:
        """Execute the pipeline sequentially. Stops on first error."""
        if not self._steps:
            return PipelineResult(
                success=True,
                final_result=None,
                error=None,
                failed_step=None,
                metadata=self._build_metadata(0.0, 0, 0, []),
            )

        pipeline_start = time.time()
        step_results: list[StepResult] = []
        current_params = initial_parameters or {}

        for index, step in enumerate(self._steps):
            # 1. Resolve skill
            try:
                resolved_skill = self._resolve_skill(step)
            except (ValueError, KeyError) as e:
                pipeline_time = (time.time() - pipeline_start) * 1000
                return PipelineResult(
                    success=False,
                    steps=step_results,
                    final_result=None,
                    error=f"Step {index}: Failed to resolve skill: {e}",
                    failed_step=index,
                    metadata=self._build_metadata(
                        pipeline_time, len(self._steps), index, step_results
                    ),
                )

            # 2. Map parameters
            if step.mapper is not None:
                try:
                    mapped_params = step.mapper(current_params)
                except Exception as e:
                    pipeline_time = (time.time() - pipeline_start) * 1000
                    return PipelineResult(
                        success=False,
                        steps=step_results,
                        final_result=None,
                        error=f"Step {index}: Mapper function failed: {e}",
                        failed_step=index,
                        metadata=self._build_metadata(
                            pipeline_time, len(self._steps), index, step_results
                        ),
                    )
            else:
                mapped_params = current_params

            # 3. Execute skill
            skill_input = SkillInput(
                action=step.action,
                parameters=mapped_params,
                context=context,
            )
            output = await resolved_skill.execute(skill_input)

            # 4. Record step result
            step_result = StepResult(
                step_index=index,
                skill_name=resolved_skill.name,
                action=step.action,
                output=output,
            )
            step_results.append(step_result)

            # 5. Fail-fast
            if not output.success:
                pipeline_time = (time.time() - pipeline_start) * 1000
                return PipelineResult(
                    success=False,
                    steps=step_results,
                    final_result=None,
                    error=(
                        f"Step {index} ({resolved_skill.name}/{step.action}) failed: {output.error}"
                    ),
                    failed_step=index,
                    metadata=self._build_metadata(
                        pipeline_time, len(self._steps), index + 1, step_results
                    ),
                )

            # 6. Feed result forward
            current_params = output.result or {}

        pipeline_time = (time.time() - pipeline_start) * 1000
        return PipelineResult(
            success=True,
            steps=step_results,
            final_result=current_params,
            error=None,
            failed_step=None,
            metadata=self._build_metadata(
                pipeline_time, len(self._steps), len(self._steps), step_results
            ),
        )

    def _build_metadata(
        self,
        total_time_ms: float,
        step_count: int,
        steps_executed: int,
        step_results: list[StepResult],
    ) -> dict[str, Any]:
        per_step_times = [
            {
                "step_index": sr.step_index,
                "skill_name": sr.skill_name,
                "action": sr.action,
                "execution_time_ms": sr.output.metadata.get("execution_time_ms", 0.0),
            }
            for sr in step_results
        ]
        return {
            "pipeline_name": self._name,
            "total_execution_time_ms": total_time_ms,
            "step_count": step_count,
            "steps_executed": steps_executed,
            "per_step_times": per_step_times,
        }

    def describe(self) -> dict[str, Any]:
        """Describe the pipeline for introspection."""
        steps_desc = []
        for i, step in enumerate(self._steps):
            name = (
                step.skill_name
                if step.skill_name
                else (step.skill.name if step.skill else "unknown")
            )
            steps_desc.append(
                {
                    "index": i,
                    "skill": name,
                    "action": step.action,
                    "has_mapper": step.mapper is not None,
                }
            )
        return {
            "name": self._name,
            "step_count": len(self._steps),
            "steps": steps_desc,
        }
