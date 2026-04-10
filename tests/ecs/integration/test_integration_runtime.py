from __future__ import annotations

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.integration
]

from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.phases import PhaseSpec
from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.ecs.scheduling.system_spec import SystemSpec


def test_scheduler_adds_and_runs_single_system_in_phase(world) -> None:
    calls: list[tuple[str, float]] = []

    def system_a(world, dt: float) -> None:
        calls.append(("a", dt))

    world.add_system(
        SystemSpec(
            name="system_a",
            fn=system_a,
            phase="sim",
        )
    )

    world.run_phase("sim", 0.25)

    assert calls == [("a", 0.25)]


def test_scheduler_runs_systems_in_insertion_order_when_no_dependencies(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    def system_c(world, dt: float) -> None:
        calls.append("c")

    world.add_system(SystemSpec(name="a", fn=system_a, phase="sim"))
    world.add_system(SystemSpec(name="b", fn=system_b, phase="sim"))
    world.add_system(SystemSpec(name="c", fn=system_c, phase="sim"))

    world.run_phase("sim", 1.0)

    assert calls == ["a", "b", "c"]


def test_scheduler_respects_after_dependency(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    world.add_system(
        SystemSpec(
            name="b",
            fn=system_b,
            phase="sim",
            after=("a",),
        )
    )
    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.0)

    assert calls == ["a", "b"]


def test_scheduler_respects_before_dependency(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    world.add_system(
        SystemSpec(
            name="b",
            fn=system_b,
            phase="sim",
        )
    )
    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
            before=("b",),
        )
    )

    world.run_phase("sim", 1.0)

    assert calls == ["a", "b"]


def test_scheduler_respects_chained_dependencies(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    def system_c(world, dt: float) -> None:
        calls.append("c")

    world.add_system(SystemSpec(name="c", fn=system_c, phase="sim", after=("b",)))
    world.add_system(SystemSpec(name="a", fn=system_a, phase="sim"))
    world.add_system(SystemSpec(name="b", fn=system_b, phase="sim", after=("a",)))

    world.run_phase("sim", 1.0)

    assert calls == ["a", "b", "c"]


def test_scheduler_skips_disabled_systems(world) -> None:
    calls: list[str] = []

    def system_enabled(world, dt: float) -> None:
        calls.append("enabled")

    def system_disabled(world, dt: float) -> None:
        calls.append("disabled")

    world.add_system(
        SystemSpec(
            name="enabled",
            fn=system_enabled,
            phase="sim",
            enabled=True,
        )
    )
    world.add_system(
        SystemSpec(
            name="disabled",
            fn=system_disabled,
            phase="sim",
            enabled=False,
        )
    )

    world.run_phase("sim", 1.0)

    assert calls == ["enabled"]


def test_scheduler_run_every_two_skips_every_other_frame(world) -> None:
    calls: list[int] = []

    def system_every_two(world, dt: float) -> None:
        calls.append(len(calls) + 1)

    world.add_system(
        SystemSpec(
            name="every_two",
            fn=system_every_two,
            phase="sim",
            run_every=2,
        )
    )

    world.run_phase("sim", 1.0)
    world.run_phase("sim", 1.0)
    world.run_phase("sim", 1.0)
    world.run_phase("sim", 1.0)

    assert len(calls) == 2


def test_scheduler_run_every_one_runs_every_time(world) -> None:
    calls: list[float] = []

    def system_every_frame(world, dt: float) -> None:
        calls.append(dt)

    world.add_system(
        SystemSpec(
            name="every_frame",
            fn=system_every_frame,
            phase="sim",
            run_every=1,
        )
    )

    world.run_phase("sim", 0.1)
    world.run_phase("sim", 0.2)
    world.run_phase("sim", 0.3)

    assert calls == [0.1, 0.2, 0.3]


def test_scheduler_commit_after_phase_applies_deferred_commands() -> None:
    class Marker:
        pass

    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=True),
        )
    )

    world = ECSWorld()
    world.bind_scheduler(scheduler)

    def spawn_marker(world, dt: float) -> None:
        placeholder = world.defer_create_entity()
        world.defer_add_component(placeholder, Marker())

    world.add_system(
        SystemSpec(
            name="spawn_marker",
            fn=spawn_marker,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.0)

    rows = list(world.query((Marker,)))
    assert len(rows) == 1
    eid, (marker,) = rows[0]
    assert world.is_alive(eid)
    assert isinstance(marker, Marker)


def test_scheduler_without_commit_after_does_not_apply_deferred_commands_automatically() -> None:
    class Marker:
        pass

    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=False),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    def spawn_marker(world, dt: float) -> None:
        placeholder = world.defer_create_entity()
        world.defer_add_component(placeholder, Marker())

    world.add_system(
        SystemSpec(
            name="spawn_marker",
            fn=spawn_marker,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.0)

    rows_before = list(world.query((Marker,)))
    assert rows_before == []

    world.apply_commands()

    rows_after = list(world.query((Marker,)))
    assert len(rows_after) == 1


def test_scheduler_run_frame_executes_multiple_phases_in_order(world) -> None:
    calls: list[str] = []

    def system_input(world, dt: float) -> None:
        calls.append("input")

    def system_sim(world, dt: float) -> None:
        calls.append("sim")

    def system_cleanup(world, dt: float) -> None:
        calls.append("cleanup")

    world.add_system(SystemSpec(name="input_system", fn=system_input, phase="input"))
    world.add_system(SystemSpec(name="sim_system", fn=system_sim, phase="sim"))
    world.add_system(SystemSpec(name="cleanup_system", fn=system_cleanup, phase="cleanup"))

    world.run_frame(1.0)

    assert calls == ["input", "sim", "cleanup"]


def test_scheduler_duplicate_system_name_in_same_phase_raises(world) -> None:
    def system_a(world, dt: float) -> None:
        pass

    world.add_system(SystemSpec(name="dup", fn=system_a, phase="sim"))

    with pytest.raises(Exception):
        world.add_system(SystemSpec(name="dup", fn=system_a, phase="sim"))


def test_scheduler_dependency_cycle_raises(world) -> None:
    def system_a(world, dt: float) -> None:
        pass

    def system_b(world, dt: float) -> None:
        pass

    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
            after=("b",),
        )
    )
    world.add_system(
        SystemSpec(
            name="b",
            fn=system_b,
            phase="sim",
            after=("a",),
        )
    )

    with pytest.raises(Exception):
        world.run_phase("sim", 1.0)


def test_scheduler_unknown_phase_raises(world) -> None:
    with pytest.raises(Exception):
        world.run_phase("not_a_real_phase", 1.0)


def test_scheduler_missing_dependency_is_ignored_or_raises_cleanly(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
            after=("missing_system",),
        )
    )

    try:
        world.run_phase("sim", 1.0)
    except Exception:
        return

    assert calls == ["a"]