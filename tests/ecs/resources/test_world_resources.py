from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [
    pytest.mark.ecs, 
    pytest.mark.unit,
    pytest.mark.resource
]


@dataclass
class Time:
    dt: float


@dataclass
class Gravity:
    x: float
    y: float


@dataclass
class Settings:
    debug: bool


def test_add_and_get_resource(world) -> None:
    time = Time(0.016)

    world.add_resource(time)

    result = world.get_resource(Time)

    assert result is time

def test_get_missing_resource_returns_none(world) -> None:
    assert world.get_resource(Time) is None

def test_has_resource_reflects_state(world) -> None:
    assert world.has_resource(Time) is False

    world.add_resource(Time(0.016))

    assert world.has_resource(Time) is True

def test_add_same_type_replaces_existing_resource(world) -> None:
    t1 = Time(0.016)
    t2 = Time(0.032)

    world.add_resource(t1)
    world.add_resource(t2)

    result = world.get_resource(Time)

    assert result is t2

def test_add_different_types_keeps_both(world) -> None:
    time = Time(0.016)
    gravity = Gravity(0.0, -9.81)

    world.add_resource(time)
    world.add_resource(gravity)

    assert world.get_resource(Time) is time
    assert world.get_resource(Gravity) is gravity

def test_remove_existing_resource(world) -> None:
    world.add_resource(Time(0.016))

    world.remove_resource(Time)

    assert world.get_resource(Time) is None
    assert world.has_resource(Time) is False

def test_remove_missing_resource_raises(world) -> None:
    with pytest.raises(KeyError):
        world.remove_resource(Time)

def test_get_required_resource_returns_value(world) -> None:
    time = Time(0.016)
    world.add_resource(time)

    result = world.get_required_resource(Time)

    assert result is time

def test_get_required_resource_missing_raises(world) -> None:
    with pytest.raises(KeyError):
        world.get_required_resource(Time)

def test_multiple_resources_can_coexist(world) -> None:
    time = Time(0.016)
    gravity = Gravity(0.0, -9.81)
    settings = Settings(debug=True)

    world.add_resource(time)
    world.add_resource(gravity)
    world.add_resource(settings)

    assert world.get_resource(Time) is time
    assert world.get_resource(Gravity) is gravity
    assert world.get_resource(Settings) is settings

def test_removing_one_resource_does_not_affect_others(world) -> None:
    time = Time(0.016)
    gravity = Gravity(0.0, -9.81)

    world.add_resource(time)
    world.add_resource(gravity)

    world.remove_resource(Time)

    assert world.get_resource(Time) is None
    assert world.get_resource(Gravity) is gravity

def test_resource_is_same_instance(world) -> None:
    settings = Settings(debug=False)

    world.add_resource(settings)

    retrieved = world.get_resource(Settings)

    assert retrieved is settings

def test_mutating_resource_reflects_in_registry(world) -> None:
    settings = Settings(debug=False)

    world.add_resource(settings)

    retrieved = world.get_resource(Settings)
    retrieved.debug = True

    again = world.get_resource(Settings)

    assert again.debug is True

def test_world_stats_tracks_resource_count(world) -> None:
    assert world.stats().resource_count == 0

    world.add_resource(Time(0.016))
    assert world.stats().resource_count == 1

    world.add_resource(Gravity(0.0, -9.81))
    assert world.stats().resource_count == 2

def test_world_summary_includes_resource_count(world) -> None:
    summary_before = world.summary()

    assert "resources=0" in summary_before

    world.add_resource(Time(0.016))

    summary_after = world.summary()

    assert "resources=1" in summary_after

def test_add_none_resource_raises(world) -> None:
    with pytest.raises(ValueError, match='cannot be None'):
        world.add_resource(None)

def test_remove_then_readd_resource(world) -> None:
    time1 = Time(0.016)
    time2 = Time(0.032)

    world.add_resource(time1)
    world.remove_resource(Time)
    world.add_resource(time2)

    result = world.get_resource(Time)

    assert result is time2

def test_repeated_add_remove_cycles_are_consistent(world) -> None:
    for i in range(5):
        world.add_resource(Time(i))
        assert world.has_resource(Time)

        world.remove_resource(Time)
        assert not world.has_resource(Time)

def test_resources_property_exposes_registry(world) -> None:
    time = Time(0.016)

    world.resources.add(time)

    assert world.get_resource(Time) is time        

def test_replacing_resource_does_not_increase_resource_count(world) -> None:
    world.add_resource(Time(0.016))
    assert world.stats().resource_count == 1

    world.add_resource(Time(0.032))
    assert world.stats().resource_count == 1

def test_get_required_resource_returns_exact_instance(world) -> None:
    time = Time(0.016)
    world.add_resource(time)

    assert world.get_required_resource(Time) is time    

def test_world_summary_updates_after_resource_removal(world) -> None:
    world.add_resource(Time(0.016))
    assert "resources=1" in world.summary()

    world.remove_resource(Time)
    assert "resources=0" in world.summary()

def test_removed_resource_is_fully_absent(world) -> None:
    world.add_resource(Time(0.016))
    world.remove_resource(Time)

    assert world.has_resource(Time) is False
    assert world.get_resource(Time) is None
    
    with pytest.raises(KeyError):
        world.get_required_resource(Time)    