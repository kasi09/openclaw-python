"""Base Skill class for OpenClaw Python Skills."""

import time
from abc import ABC, abstractmethod
from typing import Any

from .models import SkillInput, SkillOutput


class Skill(ABC):
    """Base class for OpenClaw Python Skills.

    Subclass this to create custom skills that integrate with OpenClaw.
    Implement the `process` method to define your skill's behavior.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize the skill.

        Args:
            name: Skill name
            version: Skill version
        """
        self.name = name
        self.version = version

    @abstractmethod
    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Process a skill action.

        Args:
            action: The action to perform
            parameters: Action parameters

        Returns:
            Result dictionary

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError

    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        """Execute a skill with timing and error handling.

        Args:
            skill_input: Input model containing action and parameters

        Returns:
            SkillOutput with result or error information
        """
        start_time = time.time()

        try:
            result = self.process(action=skill_input.action, parameters=skill_input.parameters)

            execution_time_ms = (time.time() - start_time) * 1000

            return SkillOutput(
                success=True,
                result=result,
                error=None,
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "skill": self.name,
                    "version": self.version,
                },
            )
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            return SkillOutput(
                success=False,
                result=None,
                error=str(e),
                metadata={
                    "execution_time_ms": execution_time_ms,
                    "skill": self.name,
                    "version": self.version,
                },
            )

    def describe(self) -> dict[str, Any]:
        """Describe the skill for OpenClaw integration.

        Returns:
            Skill metadata dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__class__.__doc__ or "",
        }
