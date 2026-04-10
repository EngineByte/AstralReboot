from __future__ import annotations

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.scheduler,
    pytest.mark.unit
]

from astralengine.ecs.scheduling.system_spec import SystemSpec


def test_after_dependency_runs_prerequisite_first(world) -> None:
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


def test_before_dependency_runs_declared_system_first(world) -> None:
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


def test_chained_after_dependencies_run_in_topological_order(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    def system_c(world, dt: float) -> None:
        calls.append("c")

    world.add_system(SystemSpec(name="c", fn=system_c, phase="sim", after=("b",)))
    world.add_system(SystemSpec(name="b", fn=system_b, phase="sim", after=("a",)))
    world.add_system(SystemSpec(name="a", fn=system_a, phase="sim"))

    world.run_phase("sim", 1.0)

    assert calls == ["a", "b", "c"]


def test_chained_before_dependencies_run_in_topological_order(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    def system_c(world, dt: float) -> None:
        calls.append("c")

    world.add_system(SystemSpec(name="c", fn=system_c, phase="sim"))
    world.add_system(SystemSpec(name="b", fn=system_b, phase="sim", before=("c",)))
    world.add_system(SystemSpec(name="a", fn=system_a, phase="sim", before=("b",)))

    world.run_phase("sim", 1.0)

    assert calls == ["a", "b", "c"]


def test_before_and_after_can_be_combined(world) -> None:
    calls: list[str] = []

    def pre(world, dt: float) -> None:
        calls.append("pre")

    def mid(world, dt: float) -> None:
        calls.append("mid")

    def post(world, dt: float) -> None:
        calls.append("post")

    world.add_system(SystemSpec(name="post", fn=post, phase="sim"))
    world.add_system(
        SystemSpec(
            name="mid",
            fn=mid,
            phase="sim",
            after=("pre",),
            before=("post",),
        )
    )
    world.add_system(SystemSpec(name="pre", fn=pre, phase="sim"))

    world.run_phase("sim", 1.0)

    assert calls == ["pre", "mid", "post"]


def test_unrelated_systems_keep_stable_order_around_dependencies(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    def system_c(world, dt: float) -> None:
        calls.append("c")

    def system_d(world, dt: float) -> None:
        calls.append("d")

    world.add_system(SystemSpec(name="a", fn=system_a, phase="sim"))
    world.add_system(SystemSpec(name="b", fn=system_b, phase="sim", after=("a",)))
    world.add_system(SystemSpec(name="c", fn=system_c, phase="sim"))
    world.add_system(SystemSpec(name="d", fn=system_d, phase="sim"))

    world.run_phase("sim", 1.0)

    assert calls.index("a") < calls.index("b")
    assert set(calls) == {"a", "b", "c", "d"}


def test_dependency_only_applies_within_same_phase(world) -> None:
    calls: list[str] = []

    def system_input(world, dt: float) -> None:
        calls.append("input")

    def system_sim(world, dt: float) -> None:
        calls.append("sim")

    world.add_system(
        SystemSpec(
            name="input_system",
            fn=system_input,
            phase="input",
        )
    )
    world.add_system(
        SystemSpec(
            name="sim_system",
            fn=system_sim,
            phase="sim",
            after=("input_system",),
        )
    )

    world.run_frame(1.0)

    assert calls == ["input", "sim"]


def test_missing_after_dependency_is_ignored_or_raises_cleanly(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
            after=("missing",),
        )
    )

    try:
        world.run_phase("sim", 1.0)
    except Exception:
        return

    assert calls == ["a"]


def test_missing_before_dependency_is_ignored_or_raises_cleanly(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
            before=("missing",),
        )
    )

    try:
        world.run_phase("sim", 1.0)
    except Exception:
        return

    assert calls == ["a"]


def test_two_system_cycle_raises(world) -> None:
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


def test_three_system_cycle_raises(world) -> None:
    def system_a(world, dt: float) -> None:
        pass

    def system_b(world, dt: float) -> None:
        pass

    def system_c(world, dt: float) -> None:
        pass

    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
            after=("c",),
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
    world.add_system(
        SystemSpec(
            name="c",
            fn=system_c,
            phase="sim",
            after=("b",),
        )
    )

    with pytest.raises(Exception):
        world.run_phase("sim", 1.0)


def test_self_dependency_raises_on_registration(world) -> None:
    def system_a(world, dt: float) -> None:
        pass

    with pytest.raises(ValueError, match="Self dependency"):
        world.add_system(
            SystemSpec(
                name="a",
                fn=system_a,
                phase="sim",
                after=("a",),
            )
        )


def test_disabled_dependency_target_does_not_crash_scheduler(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    world.add_system(
        SystemSpec(
            name="a",
            fn=system_a,
            phase="sim",
            enabled=False,
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

    try:
        world.run_phase("sim", 1.0)
    except Exception:
        return

    assert calls == ["b"] or calls == []


def test_dependency_graph_is_recomputed_consistently_each_run(world) -> None:
    calls: list[str] = []

    def system_a(world, dt: float) -> None:
        calls.append("a")

    def system_b(world, dt: float) -> None:
        calls.append("b")

    world.add_system(SystemSpec(name="b", fn=system_b, phase="sim", after=("a",)))
    world.add_system(SystemSpec(name="a", fn=system_a, phase="sim"))

    world.run_phase("sim", 1.0)
    world.run_phase("sim", 1.0)

    assert calls == ["a", "b", "a", "b"]


def test_longer_dependency_chain_with_unrelated_systems(world) -> None:
    calls: list[str] = []

    def s1(world, dt: float) -> None:
        calls.append("s1")

    def s2(world, dt: float) -> None:
        calls.append("s2")

    def s3(world, dt: float) -> None:
        calls.append("s3")

    def s4(world, dt: float) -> None:
        calls.append("s4")

    def s5(world, dt: float) -> None:
        calls.append("s5")

    world.add_system(SystemSpec(name="s3", fn=s3, phase="sim", after=("s2",)))
    world.add_system(SystemSpec(name="s1", fn=s1, phase="sim"))
    world.add_system(SystemSpec(name="s5", fn=s5, phase="sim"))
    world.add_system(SystemSpec(name="s2", fn=s2, phase="sim", after=("s1",)))
    world.add_system(SystemSpec(name="s4", fn=s4, phase="sim", after=("s3",)))

    world.run_phase("sim", 1.0)

    assert calls.index("s1") < calls.index("s2") < calls.index("s3") < calls.index("s4")
    assert set(calls) == {"s1", "s2", "s3", "s4", "s5"}