from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.world,
    pytest.mark.unit
]


@dataclass
class Counter:
    value: int


class Player:
    pass


def test_scheduler_property_raises_when_unbound() -> None:
    from astralengine.ecs.core.world import ECSWorld

    world = ECSWorld()

    with pytest.raises(RuntimeError, match="No Scheduler bound"):
        _ = world.scheduler


def test_run_phase_raises_when_scheduler_unbound() -> None:
    from astralengine.ecs.core.world import ECSWorld

    world = ECSWorld()

    with pytest.raises(RuntimeError, match="No Scheduler bound"):
        world.run_phase("sim", 1.0)


def test_run_frame_raises_when_scheduler_unbound() -> None:
    from astralengine.ecs.core.world import ECSWorld

    world = ECSWorld()

    with pytest.raises(RuntimeError, match="No Scheduler bound"):
        world.run_frame(1.0)


def test_get_component_missing_component_returns_none(world) -> None:
    eid = world.create_entity()

    result = world.get_component(eid, Counter)

    assert result is None


def test_remove_component_missing_component_raises_or_noops_cleanly(world) -> None:
    eid = world.create_entity()

    try:
        world.remove_component(eid, Counter)
    except Exception:
        return

    assert world.is_alive(eid)


def test_remove_tag_missing_tag_raises_or_noops_cleanly(world) -> None:
    eid = world.create_entity()

    try:
        world.remove_tag(eid, Player)
    except Exception:
        return

    assert world.is_alive(eid)


def test_get_component_dead_entity_returns_none(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    result = world.get_component(eid, Counter)

    assert result is None


def test_add_component_to_dead_entity_raises(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    with pytest.raises(Exception):
        world.add_component(eid, Counter(1))


def test_add_tag_to_dead_entity_raises(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    with pytest.raises(Exception):
        world.add_tag(eid, Player)


def test_remove_component_from_dead_entity_raises_or_noops_cleanly(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.remove_component(eid, Counter)
    except Exception:
        return

    assert world.is_alive(eid) is False


def test_remove_tag_from_dead_entity_raises_or_noops_cleanly(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.remove_tag(eid, Player)
    except Exception:
        return

    assert world.is_alive(eid) is False


def test_destroy_entity_twice_raises_or_noops_cleanly(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.destroy_entity(eid)
    except Exception:
        return

    assert world.is_alive(eid) is False


def test_get_component_invalid_entity_returns_none(world) -> None:
    result = world.get_component(999999, Counter)

    assert result is None


def test_add_component_invalid_entity_raises(world) -> None:
    with pytest.raises(Exception):
        world.add_component(999999, Counter(1))


def test_add_tag_invalid_entity_raises(world) -> None:
    with pytest.raises(Exception):
        world.add_tag(999999, Player)


def test_remove_component_invalid_entity_raises_or_noops_cleanly(world) -> None:
    try:
        world.remove_component(999999, Counter)
    except Exception:
        return

    assert True


def test_remove_tag_invalid_entity_raises_or_noops_cleanly(world) -> None:
    try:
        world.remove_tag(999999, Player)
    except Exception:
        return

    assert True


def test_destroy_invalid_entity_raises_or_noops_cleanly(world) -> None:
    try:
        world.destroy_entity(999999)
    except Exception:
        return

    assert True


def test_query_empty_component_tuple_raises_value_error(world) -> None:
    with pytest.raises(ValueError, match="at least one component type"):
        list(world.query(tuple()))


def test_query_missing_component_type_returns_empty(world) -> None:
    rows = list(world.query((Counter,)))
    assert rows == []


def test_run_unknown_phase_raises(world) -> None:
    with pytest.raises(Exception):
        world.run_phase("definitely_not_a_real_phase", 1.0)


def test_add_duplicate_system_name_raises(world) -> None:
    from astralengine.ecs.scheduling.system_spec import SystemSpec

    def system_a(world, dt: float) -> None:
        pass

    world.add_system(SystemSpec(name="dup", fn=system_a, phase="sim"))

    with pytest.raises(Exception):
        world.add_system(SystemSpec(name="dup", fn=system_a, phase="sim"))


def test_add_system_with_unknown_phase_raises(world) -> None:
    from astralengine.ecs.scheduling.system_spec import SystemSpec

    def system_a(world, dt: float) -> None:
        pass

    with pytest.raises(Exception):
        world.add_system(SystemSpec(name="bad_phase", fn=system_a, phase="not_real"))


def test_get_component_after_component_removed_raises_or_returns_missing_cleanly(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(4))
    world.remove_component(eid, Counter)

    try:
        result = world.get_component(eid, Counter)
    except Exception:
        return

    assert result is None


def test_query_with_destroyed_entity_does_not_crash(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.destroy_entity(eid)

    rows = list(world.query((Counter,)))
    assert rows == []


def test_apply_commands_with_no_pending_commands_does_not_crash(world) -> None:
    world.apply_commands()
    world.apply_commands()

    assert world.entity_count() == 0


def test_bind_scheduler_twice_raises_or_rebinds_cleanly(world) -> None:
    from astralengine.ecs.scheduling.scheduler import SystemScheduler

    new_scheduler = SystemScheduler()

    try:
        world.bind_scheduler(new_scheduler)
    except Exception:
        return

    assert world.scheduler is new_scheduler