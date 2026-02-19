"""Skill Registry for OpenClaw Python Skills."""

import threading
from typing import Any, Optional

from .skill import Skill

# Type alias for the skill decorator
_SkillClass = type


class SkillRegistry:
    """Thread-safe registry for managing Skill instances.

    Provides registration, lookup, and enumeration of skills by name.
    Skills are stored in an in-memory dictionary keyed by their name attribute.

    Example::

        registry = SkillRegistry()
        registry.register(TextAnalyzerSkill())
        skill = registry.get("text-analyzer")
    """

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._lock = threading.Lock()

    def register(self, skill: Skill) -> None:
        """Register a skill instance.

        Args:
            skill: A Skill instance to register.

        Raises:
            TypeError: If skill is not a Skill instance.
            ValueError: If a skill with the same name is already registered.
        """
        if not isinstance(skill, Skill):
            raise TypeError(f"Expected a Skill instance, got {type(skill).__name__}")
        with self._lock:
            if skill.name in self._skills:
                raise ValueError(
                    f"Skill '{skill.name}' is already registered. "
                    "Unregister it first or use a different name."
                )
            self._skills[skill.name] = skill

    def unregister(self, name: str) -> Skill:
        """Remove and return a skill by name.

        Args:
            name: The name of the skill to remove.

        Returns:
            The removed Skill instance.

        Raises:
            KeyError: If no skill with the given name is registered.
        """
        with self._lock:
            if name not in self._skills:
                raise KeyError(f"No skill registered with name '{name}'")
            return self._skills.pop(name)

    def get(self, name: str) -> Skill:
        """Look up a skill by name.

        Args:
            name: The skill name to look up.

        Returns:
            The registered Skill instance.

        Raises:
            KeyError: If no skill with the given name is registered.
        """
        with self._lock:
            if name not in self._skills:
                raise KeyError(f"No skill registered with name '{name}'")
            return self._skills[name]

    def has(self, name: str) -> bool:
        """Check whether a skill is registered.

        Args:
            name: The skill name to check.

        Returns:
            True if a skill with the given name is registered.
        """
        with self._lock:
            return name in self._skills

    def list_skills(self) -> list[dict[str, Any]]:
        """List all registered skills with their metadata.

        Returns:
            A list of skill metadata dictionaries (from Skill.describe()).
        """
        with self._lock:
            return [skill.describe() for skill in self._skills.values()]

    def skill_names(self) -> list[str]:
        """Return a sorted list of all registered skill names."""
        with self._lock:
            return sorted(self._skills.keys())

    def clear(self) -> None:
        """Remove all registered skills."""
        with self._lock:
            self._skills.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._skills)

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False
        return self.has(name)

    def skill(self, cls: _SkillClass) -> _SkillClass:
        """Class decorator that instantiates and registers a Skill subclass.

        Usage::

            registry = SkillRegistry()

            @registry.skill
            class MySkill(Skill):
                def __init__(self):
                    super().__init__(name="my-skill")

                def process(self, action, parameters):
                    ...

        Args:
            cls: A Skill subclass (must be instantiable with no arguments).

        Returns:
            The original class, unmodified.

        Raises:
            TypeError: If cls is not a subclass of Skill or cannot be instantiated.
        """
        if not (isinstance(cls, type) and issubclass(cls, Skill)):
            raise TypeError(f"@registry.skill can only decorate Skill subclasses, got {cls}")
        try:
            instance = cls()
        except TypeError as e:
            raise TypeError(
                f"@registry.skill requires {cls.__name__} to be instantiable with no arguments: {e}"
            ) from e
        self.register(instance)
        return cls


# --- Global singleton ---

_global_registry: Optional[SkillRegistry] = None
_global_lock = threading.Lock()


def get_global_registry() -> SkillRegistry:
    """Return the global shared SkillRegistry instance.

    Creates it on first call (thread-safe lazy initialization).
    """
    global _global_registry
    if _global_registry is None:
        with _global_lock:
            if _global_registry is None:
                _global_registry = SkillRegistry()
    return _global_registry
