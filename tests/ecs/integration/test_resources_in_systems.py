from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [
    pytest.mark.ecs, 
    pytest.mark.resource,
    pytest.mark.system,
    pytest.mark.integration
]


@dataclass
class TimeScale:
    value: float


@dataclass
class Counter:
    value: float


def test_system_can_read_required_resource(world) -> None:
    from astralengine.ecs.scheduling.system_spec import SystemSpec

    calls: list[float] = []

    def system_read_timescale(world, dt: float) -> None:
        timescale = world.get_required_resource(TimeScale)
        calls.append(timescale.value)

    world.add_resource(TimeScale(2.0))
    world.add_system(
        SystemSpec(
            name="read_timescale",
            fn=system_read_timescale,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.0)

    assert calls == [2.0]


def test_system_missing_required_resource_raises(world) -> None:
    from astralengine.ecs.scheduling.system_spec import SystemSpec

    def system_read_timescale(world, dt: float) -> None:
        world.get_required_resource(TimeScale)

    world.add_system(
        SystemSpec(
            name="read_timescale",
            fn=system_read_timescale,
            phase="sim",
        )
    )

    with pytest.raises(KeyError):
        world.run_phase("sim", 1.0)


def test_updated_resource_affects_next_phase_run(world) -> None:
    from astralengine.ecs.scheduling.system_spec import SystemSpec

    calls: list[float] = []

    def system_read_timescale(world, dt: float) -> None:
        timescale = world.get_required_resource(TimeScale)
        calls.append(timescale.value)

    world.add_resource(TimeScale(1.0))
    world.add_system(
        SystemSpec(
            name="read_timescale",
            fn=system_read_timescale,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.0)

    world.add_resource(TimeScale(3.0))
    world.run_phase("sim", 1.0)

    assert calls == [1.0, 3.0]


def test_system_can_use_resource_to_modify_entities(world) -> None:
    from astralengine.ecs.scheduling.system_spec import SystemSpec

    def system_scale_counter(world, dt: float) -> None:
        scale = world.get_required_resource(TimeScale)
        for eid, (counter,) in world.query((Counter,)):
            counter.value += dt * scale.value

    eid = world.create_entity()
    world.add_component(eid, Counter(0.0))
    world.add_resource(TimeScale(2.0))

    world.add_system(
        SystemSpec(
            name="scale_counter",
            fn=system_scale_counter,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.5)

    counter = world.get_component(eid, Counter)
    assert counter is not None
    assert counter.value == 3.0