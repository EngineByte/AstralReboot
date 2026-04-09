from __future__ import annotations

from astralengine.ecs.scheduling.system_spec import SystemSpec


def test_run_phase_executes_only_systems_in_that_phase(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    world.scheduler.add_system(
        SystemSpec(name="a", fn=system_a, phase="pre_sim")
    )
    world.scheduler.add_system(
        SystemSpec(name="b", fn=system_b, phase="sim")
    )

    world.run_phase("pre_sim", 1.0 / 60.0)

    assert calls == ["a"]


def test_run_frame_executes_registered_systems(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    world.scheduler.add_system(
        SystemSpec(name="a", fn=system_a, phase="sim")
    )

    world.run_frame(1.0 / 60.0)

    assert calls == ["a"]


def test_disabled_system_does_not_run(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    world.scheduler.add_system(
        SystemSpec(name="a", fn=system_a, phase="sim", enabled=False)
    )

    world.run_frame(1.0 / 60.0)

    assert calls == []


def test_run_every_two_frames(world) -> None:
    calls: list[int] = []

    def system_a(world, dt: float) -> None:
        calls.append(1)

    world.scheduler.add_system(
        SystemSpec(name="a", fn=system_a, phase="sim", run_every=2)
    )

    for _ in range(5):
        world.run_frame(1.0 / 60.0)

    assert len(calls) in {2, 3}

def test_before_after_dependency_ordering(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    world.scheduler.add_system(
        SystemSpec(name="a", fn=system_a, phase="sim", before=("b",))
    )
    world.scheduler.add_system(
        SystemSpec(name="b", fn=system_b, phase="sim")
    )

    world.run_phase("sim", 1.0 / 60.0)

    assert calls == ["a", "b"]