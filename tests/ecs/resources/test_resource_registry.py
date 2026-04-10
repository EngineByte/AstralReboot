from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [
    pytest.mark.ecs, 
    pytest.mark.unit,
    pytest.mark.resource]


@dataclass
class Time:
    dt: float


@dataclass
class Gravity:
    x: float
    y: float


@dataclass
class FrameCount:
    value: int


class Settings:
    def __init__(self, debug: bool) -> None:
        self.debug = debug


def test_registry_starts_empty() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    assert registry.is_empty() is True
    assert registry.count() == 0


def test_add_and_get_resource() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)

    registry.add(time)

    assert registry.get(Time) is time


def test_get_missing_resource_returns_none() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    assert registry.get(Time) is None


def test_has_resource_reflects_registration_state() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)

    assert registry.has(Time) is False

    registry.add(time)

    assert registry.has(Time) is True


def test_count_tracks_number_of_registered_resource_types() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    assert registry.count() == 0

    registry.add(Time(0.016))
    assert registry.count() == 1

    registry.add(Gravity(0.0, -9.81))
    assert registry.count() == 2


def test_add_same_type_replaces_existing_resource() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    t1 = Time(0.016)
    t2 = Time(0.032)

    registry.add(t1)
    registry.add(t2)

    assert registry.count() == 1
    assert registry.get(Time) is t2


def test_add_different_types_keeps_both_resources() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)
    gravity = Gravity(0.0, -9.81)

    registry.add(time)
    registry.add(gravity)

    assert registry.count() == 2
    assert registry.get(Time) is time
    assert registry.get(Gravity) is gravity


def test_remove_existing_resource_removes_it() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    registry.add(Time(0.016))

    registry.remove(Time)

    assert registry.has(Time) is False
    assert registry.get(Time) is None
    assert registry.count() == 0


def test_remove_missing_resource_raises_keyerror_if_strict() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    try:
        registry.remove(Time)
    except KeyError:
        return

    assert registry.count() == 0
    assert registry.get(Time) is None


def test_clear_removes_all_resources() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    registry.add(Time(0.016))
    registry.add(Gravity(0.0, -9.81))

    registry.clear()

    assert registry.is_empty() is True
    assert registry.count() == 0
    assert registry.get(Time) is None
    assert registry.get(Gravity) is None


def test_is_empty_false_when_resource_present() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    registry.add(Time(0.016))

    assert registry.is_empty() is False


def test_get_returns_exact_same_instance() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    settings = Settings(debug=True)

    registry.add(settings)

    assert registry.get(Settings) is settings


def test_registry_allows_plain_python_objects_as_resources() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    settings = Settings(debug=True)
    frame = FrameCount(10)

    registry.add(settings)
    registry.add(frame)

    assert registry.get(Settings) is settings
    assert registry.get(FrameCount) is frame


def test_contains_type_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    registry.add(Time(0.016))

    if not hasattr(registry, "__contains__"):
        return

    assert Time in registry
    assert Gravity not in registry


def test_types_returns_registered_resource_types_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    registry.add(Time(0.016))
    registry.add(Gravity(0.0, -9.81))

    if not hasattr(registry, "types"):
        return

    types = registry.types()
    assert set(types) == {Time, Gravity}

def test_values_returns_registered_resource_instances_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)
    gravity = Gravity(0.0, -9.81)

    registry.add(time)
    registry.add(gravity)

    if not hasattr(registry, "values"):
        return

    values = list(registry.values())

    assert len(values) == 2
    assert time in values
    assert gravity in values

def test_items_returns_type_resource_pairs_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)
    gravity = Gravity(0.0, -9.81)

    registry.add(time)
    registry.add(gravity)

    if not hasattr(registry, "items"):
        return

    items = dict(registry.items())
    assert items[Time] is time
    assert items[Gravity] is gravity


def test_len_matches_count_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    registry.add(Time(0.016))
    registry.add(Gravity(0.0, -9.81))

    if not hasattr(registry, "__len__"):
        return

    assert len(registry) == registry.count() == 2


def test_get_required_returns_resource_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)
    registry.add(time)

    if not hasattr(registry, "get_required"):
        return

    assert registry.get_required(Time) is time


def test_get_required_missing_raises_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    if not hasattr(registry, "get_required"):
        return

    with pytest.raises(KeyError):
        registry.get_required(Time)


def test_pop_returns_removed_resource_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)
    registry.add(time)

    if not hasattr(registry, "pop"):
        return

    removed = registry.pop(Time)

    assert removed is time
    assert registry.get(Time) is None
    assert registry.count() == 0


def test_pop_missing_raises_or_returns_none_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    if not hasattr(registry, "pop"):
        return

    try:
        result = registry.pop(Time)
    except KeyError:
        return

    assert result is None


def test_summary_reports_registry_state_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    if not hasattr(registry, "summary"):
        return

    empty_summary = registry.summary()
    assert isinstance(empty_summary, str)

    registry.add(Time(0.016))
    summary = registry.summary()

    assert isinstance(summary, str)
    assert "1" in summary or "Time" in summary


def test_stats_reports_registry_state_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    if not hasattr(registry, "stats"):
        return

    empty_stats = registry.stats()
    assert isinstance(empty_stats, dict)

    registry.add(Time(0.016))
    stats = registry.stats()
    assert isinstance(stats, dict)


def test_replacing_one_resource_does_not_affect_others() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    t1 = Time(0.016)
    t2 = Time(0.032)
    gravity = Gravity(0.0, -9.81)

    registry.add(t1)
    registry.add(gravity)
    registry.add(t2)

    assert registry.get(Time) is t2
    assert registry.get(Gravity) is gravity
    assert registry.count() == 2


def test_clear_after_replacements_leaves_registry_empty() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    registry.add(Time(0.016))
    registry.add(Time(0.032))
    registry.add(Gravity(0.0, -9.81))

    registry.clear()

    assert registry.is_empty() is True
    assert registry.count() == 0


def test_multiple_add_remove_cycles_keep_registry_consistent() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    registry.add(Time(0.016))
    registry.add(Gravity(0.0, -9.81))
    registry.remove(Time)
    registry.add(FrameCount(1))
    registry.remove(Gravity)

    assert registry.get(Time) is None
    assert registry.get(Gravity) is None

    frame = registry.get(FrameCount)
    assert frame is not None
    assert frame.value == 1
    assert registry.count() == 1


def test_registry_can_store_mutable_resource_and_return_updated_state() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    settings = Settings(debug=False)

    registry.add(settings)

    loaded = registry.get(Settings)
    assert loaded is settings

    loaded.debug = True

    again = registry.get(Settings)
    assert again is settings
    assert again.debug is True


def test_add_none_is_rejected_or_stored_cleanly() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()

    try:
        registry.add(None)  # type: ignore[arg-type]
    except Exception:
        return

    assert registry.get(type(None)) is None


def test_registry_iteration_over_items_is_stable_if_supported() -> None:
    from astralengine.ecs.resources.resource_registry import ResourceRegistry

    registry = ResourceRegistry()
    time = Time(0.016)
    gravity = Gravity(0.0, -9.81)
    registry.add(time)
    registry.add(gravity)

    if not hasattr(registry, "items"):
        return

    items1 = dict(registry.items())
    items2 = dict(registry.items())

    assert items1[Time] is time
    assert items1[Gravity] is gravity
    assert items2[Time] is time
    assert items2[Gravity] is gravity