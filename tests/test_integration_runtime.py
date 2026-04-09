from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.scheduling.system_spec import SystemSpec

from .conftest import Counter, Lifetime


def system_increment_counter(world, dt: float) -> None:
    _ = dt
    for _, (counter,) in world.query((Counter,)):
        counter.value += 1


def system_tick_lifetime(world, dt: float) -> None:
    _ = dt
    for entity, (lifetime,) in world.query((Lifetime,)):
        lifetime.frames_left -= 1
        if lifetime.frames_left <= 0:
            world.command_buffer.defer_destroy_entity(entity)


def test_counter_system_runs_across_multiple_frames(world) -> None:
    world.scheduler.add_system(
        SystemSpec(
            name="increment_counter",
            fn=system_increment_counter,
            phase="sim",
        )
    )

    entity = world.create_entity()
    world.add_component(entity, Counter(value=0))

    for _ in range(3):
        world.run_frame(1.0 / 60.0)

    counter = world.get_component(entity, Counter)
    assert counter is not None
    assert counter.value == 3


def test_multiple_entities_update_independently(world) -> None:
    world.scheduler.add_system(
        SystemSpec(
            name="increment_counter",
            fn=system_increment_counter,
            phase="sim",
        )
    )

    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(value=0))
    world.add_component(e2, Counter(value=10))

    for _ in range(3):
        world.run_frame(1.0 / 60.0)

    c1 = world.get_component(e1, Counter)
    c2 = world.get_component(e2, Counter)

    assert c1 is not None
    assert c2 is not None
    assert c1.value == 3
    assert c2.value == 13


def test_deferred_destroy_is_safe_during_iteration(world) -> None:
    world.scheduler.add_system(
        SystemSpec(
            name="tick_lifetime",
            fn=system_tick_lifetime,
            phase="sim",
        )
    )

    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()

    world.add_component(e1, Lifetime(frames_left=1))
    world.add_component(e2, Lifetime(frames_left=2))
    world.add_component(e3, Lifetime(frames_left=3))

    world.run_frame(1.0 / 60.0)
    assert not world.is_alive(e1)
    assert world.is_alive(e2)
    assert world.is_alive(e3)

    world.run_frame(1.0 / 60.0)
    assert not world.is_alive(e1)
    assert not world.is_alive(e2)
    assert world.is_alive(e3)

    world.run_frame(1.0 / 60.0)
    assert not world.is_alive(e1)
    assert not world.is_alive(e2)
    assert not world.is_alive(e3)