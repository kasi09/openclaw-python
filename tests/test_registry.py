"""Tests for SkillRegistry."""

import threading
from typing import Any

import pytest

from openclaw_python_skill import Skill, SkillRegistry, get_global_registry


# --- Test skill classes ---


class AlphaSkill(Skill):
    """A test skill."""

    def __init__(self):
        super().__init__(name="alpha", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {"skill": "alpha"}


class BetaSkill(Skill):
    """Another test skill."""

    def __init__(self):
        super().__init__(name="beta", version="2.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return {"skill": "beta"}


@pytest.fixture
def registry():
    """Create a fresh SkillRegistry."""
    return SkillRegistry()


@pytest.fixture
def alpha():
    return AlphaSkill()


@pytest.fixture
def beta():
    return BetaSkill()


# --- Registration ---


def test_register_skill(registry, alpha):
    registry.register(alpha)
    assert registry.has("alpha")
    assert len(registry) == 1


def test_register_multiple(registry, alpha, beta):
    registry.register(alpha)
    registry.register(beta)
    assert len(registry) == 2


def test_register_duplicate_raises(registry, alpha):
    registry.register(alpha)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(AlphaSkill())


def test_register_non_skill_raises(registry):
    with pytest.raises(TypeError, match="Expected a Skill instance"):
        registry.register("not a skill")


# --- Unregistration ---


def test_unregister_returns_skill(registry, alpha):
    registry.register(alpha)
    removed = registry.unregister("alpha")
    assert removed is alpha
    assert not registry.has("alpha")
    assert len(registry) == 0


def test_unregister_missing_raises(registry):
    with pytest.raises(KeyError, match="No skill registered"):
        registry.unregister("nonexistent")


def test_register_after_unregister(registry, alpha):
    registry.register(alpha)
    registry.unregister("alpha")
    new_alpha = AlphaSkill()
    registry.register(new_alpha)
    assert registry.get("alpha") is new_alpha


# --- Lookup ---


def test_get_returns_correct_skill(registry, alpha, beta):
    registry.register(alpha)
    registry.register(beta)
    assert registry.get("alpha") is alpha
    assert registry.get("beta") is beta


def test_get_missing_raises(registry):
    with pytest.raises(KeyError, match="No skill registered"):
        registry.get("nonexistent")


# --- Has / contains ---


def test_has_registered(registry, alpha):
    registry.register(alpha)
    assert registry.has("alpha") is True


def test_has_unregistered(registry):
    assert registry.has("nonexistent") is False


def test_contains_operator(registry, alpha):
    registry.register(alpha)
    assert "alpha" in registry
    assert "nonexistent" not in registry


# --- Listing ---


def test_list_empty(registry):
    assert registry.list_skills() == []


def test_list_skills_metadata(registry, alpha, beta):
    registry.register(alpha)
    registry.register(beta)
    skills = registry.list_skills()
    assert len(skills) == 2
    names = {s["name"] for s in skills}
    assert names == {"alpha", "beta"}
    for meta in skills:
        assert "name" in meta
        assert "version" in meta
        assert "description" in meta


def test_skill_names_sorted(registry, alpha, beta):
    registry.register(beta)
    registry.register(alpha)
    assert registry.skill_names() == ["alpha", "beta"]


# --- Clear / Len ---


def test_clear(registry, alpha, beta):
    registry.register(alpha)
    registry.register(beta)
    registry.clear()
    assert len(registry) == 0
    assert registry.list_skills() == []


def test_len_empty(registry):
    assert len(registry) == 0


def test_len_tracks_operations(registry, alpha, beta):
    registry.register(alpha)
    assert len(registry) == 1
    registry.register(beta)
    assert len(registry) == 2
    registry.unregister("alpha")
    assert len(registry) == 1


# --- Decorator ---


def test_decorator_registers(registry):
    @registry.skill
    class MySkill(Skill):
        """Decorated skill."""

        def __init__(self):
            super().__init__(name="decorated", version="1.0.0")

        def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
            return {}

    assert registry.has("decorated")
    assert registry.get("decorated").name == "decorated"


def test_decorator_returns_class(registry):
    @registry.skill
    class MySkill(Skill):
        """Decorated skill."""

        def __init__(self):
            super().__init__(name="decorated-ret", version="1.0.0")

        def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
            return {}

    assert MySkill.__name__ == "MySkill"
    instance = MySkill()
    assert instance.name == "decorated-ret"


def test_decorator_non_skill_raises(registry):
    with pytest.raises(TypeError, match="Skill subclasses"):

        @registry.skill
        class NotASkill:
            pass


def test_decorator_requires_no_arg_init(registry):
    with pytest.raises(TypeError, match="instantiable with no arguments"):

        @registry.skill
        class NeedsArgs(Skill):
            def __init__(self, config: str):
                super().__init__(name="needs-args", version="1.0.0")

            def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
                return {}


# --- Global registry ---


def test_global_registry_returns_instance():
    reg = get_global_registry()
    assert isinstance(reg, SkillRegistry)


def test_global_registry_is_singleton():
    reg1 = get_global_registry()
    reg2 = get_global_registry()
    assert reg1 is reg2


# --- Thread safety ---


def test_concurrent_registration():
    registry = SkillRegistry()
    errors: list[Exception] = []

    def register_skill(index: int):
        try:
            skill = type(
                f"Skill{index}",
                (Skill,),
                {
                    "__init__": lambda self, idx=index: Skill.__init__(
                        self, name=f"skill-{idx}", version="1.0.0"
                    ),
                    "process": lambda self, action, parameters: {},
                },
            )()
            registry.register(skill)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=register_skill, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
    assert len(registry) == 50


def test_concurrent_read_write():
    registry = SkillRegistry()
    registry.register(AlphaSkill())
    errors: list[Exception] = []

    def reader():
        try:
            for _ in range(100):
                registry.has("alpha")
                registry.list_skills()
                len(registry)
        except Exception as e:
            errors.append(e)

    def writer():
        try:
            for i in range(20):
                name = f"writer-{i}"
                skill = type(
                    f"WSkill{i}",
                    (Skill,),
                    {
                        "__init__": lambda self, n=name: Skill.__init__(
                            self, name=n, version="1.0.0"
                        ),
                        "process": lambda self, action, parameters: {},
                    },
                )()
                registry.register(skill)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=reader) for _ in range(5)]
    threads.append(threading.Thread(target=writer))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
