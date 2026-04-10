from __future__ import annotations

from dataclasses import dataclass

import pytest

from astralengine.ecs.scheduling.system_spec import SystemSpec

pytestmark = [pytest.mark.ecs, pytest.mark.integration]


# ---------------------------------------------------------
# Components / Resources
# ---------------------------------------------------------

@dataclass
class Transform:
    x: float


@dataclass
class Velocity:
    vx: float


@dataclass
class Lifetime:
    remaining: float


@dataclass
class TimeScale:
    value: float


# ---------------------------------------------------------
# Systems
# ---------------------------------------------------------

def system_apply_velocity(world, dt: float) -> None:
    scale = world.get_required_resource(TimeScale)

    for _eid, (t, v) in world.query((Transform, Velocity)):
        t.x += v.vx * dt * scale.value


def system_decay_lifetime(world, dt: float) -> None:
    for _eid, (lifetime,) in world.query((Lifetime,)):
        lifetime.remaining -= dt


def system_despawn_expired(world, dt: float) -> None:
    for eid, (lifetime,) in world.query((Lifetime,)):
        if lifetime.remaining <= 0:
            world.defer_destroy_entity(eid)


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_entities_move_and_expire_over_multiple_frames(world) -> None:
    world.add_resource(TimeScale(1.0))

    eid = world.create_entity()
    world.add_component(eid, Transform(0.0))
    world.add_component(eid, Velocity(1.0))
    world.add_component(eid, Lifetime(3.0))

    world.add_system(SystemSpec("velocity", system_apply_velocity, phase="sim"))
    world.add_system(SystemSpec("lifetime", system_decay_lifetime, phase="sim"))
    world.add_system(SystemSpec("despawn", system_despawn_expired, phase="sim"))

    # Frame 1
    world.run_phase("sim", 1.0)
    t = world.get_component(eid, Transform)
    assert t is not None
    assert t.x == 1.0

    # Frame 2
    world.run_phase("sim", 1.0)
    t = world.get_component(eid, Transform)
    assert t is not None
    assert t.x == 2.0

    # Frame 3 (expires)
    world.run_phase("sim", 1.0)

    assert world.is_alive(eid) is False
    assert list(world.query((Transform,))) == []


def test_multiple_entities_update_independently(world) -> None:
    world.add_resource(TimeScale(1.0))

    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Transform(0.0))
    world.add_component(e1, Velocity(1.0))

    world.add_component(e2, Transform(10.0))
    world.add_component(e2, Velocity(-2.0))

    world.add_system(SystemSpec("velocity", system_apply_velocity, phase="sim"))

    world.run_phase("sim", 1.0)

    t1 = world.get_component(e1, Transform)
    t2 = world.get_component(e2, Transform)

    assert t1 is not None and t2 is not None
    assert t1.x == 1.0
    assert t2.x == 8.0


def test_resource_changes_affect_subsequent_frames(world) -> None:
    world.add_resource(TimeScale(1.0))

    eid = world.create_entity()
    world.add_component(eid, Transform(0.0))
    world.add_component(eid, Velocity(2.0))

    world.add_system(SystemSpec("velocity", system_apply_velocity, phase="sim"))

    world.run_phase("sim", 1.0)

    # Change resource
    world.add_resource(TimeScale(3.0))

    world.run_phase("sim", 1.0)

    t = world.get_component(eid, Transform)
    assert t is not None
    assert t.x == (2.0 * 1.0) + (2.0 * 3.0)


def test_deferred_destruction_safe_during_iteration(world) -> None:
    world.add_resource(TimeScale(1.0))

    for i in range(5):
        eid = world.create_entity()
        world.add_component(eid, Transform(float(i)))
        world.add_component(eid, Lifetime(1.0))

    world.add_system(SystemSpec("decay", system_decay_lifetime, phase="sim"))
    world.add_system(SystemSpec("despawn", system_despawn_expired, phase="sim"))

    world.run_phase("sim", 1.0)

    assert list(world.query((Transform,))) == []


def test_spawn_then_update_next_frame(world) -> None:
    world.add_resource(TimeScale(1.0))

    def system_spawn(world, dt: float) -> None:
        p = world.defer_create_entity()
        world.defer_add_component(p, Transform(0.0))
        world.defer_add_component(p, Velocity(1.0))

    world.add_system(SystemSpec("spawn", system_spawn, phase="sim"))
    world.add_system(SystemSpec("velocity", system_apply_velocity, phase="sim"))

    # First frame: spawn only
    world.run_phase("sim", 1.0)

    rows = list(world.query((Transform,)))
    assert len(rows) == 1
    eid = rows[0][0]
    assert rows[0][1][0].x == 0.0

    # Second frame: movement applies
    world.run_phase("sim", 1.0)

    t = world.get_component(eid, Transform)
    assert t is not None
    assert t.x == 1.0


def test_systems_execute_in_dependency_order(world) -> None:
    world.add_resource(TimeScale(1.0))

    execution_order: list[str] = []

    def system_a(world, dt: float) -> None:
        execution_order.append("a")

    def system_b(world, dt: float) -> None:
        execution_order.append("b")

    world.add_system(SystemSpec("a", system_a, phase="sim"))
    world.add_system(
        SystemSpec("b", system_b, phase="sim", after=("a",))
    )

    world.run_phase("sim", 1.0)

    assert execution_order == ["a", "b"]