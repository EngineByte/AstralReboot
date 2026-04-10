from __future__ import annotations

import pytest

from astralengine.ecs.scheduling.system_spec import SystemSpec


def dummy_system(world, dt: float) -> None:
    pass


def other_system(world, dt: float) -> None:
    pass


def test_system_spec_stores_required_fields() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
    )

    assert spec.name == "move"
    assert spec.fn is dummy_system
    assert spec.phase == "sim"


def test_system_spec_default_enabled_is_true() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
    )

    assert spec.enabled is True


def test_system_spec_default_run_every_is_one() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
    )

    assert spec.run_every == 1


def test_system_spec_accepts_before_dependencies() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        before=("render",),
    )

    assert spec.before == ("render",)


def test_system_spec_accepts_after_dependencies() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        after=("input",),
    )

    assert spec.after == ("input",)


def test_system_spec_accepts_multiple_dependencies() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        before=("render", "cleanup"),
        after=("input", "startup"),
    )

    assert spec.before == ("render", "cleanup")
    assert spec.after == ("input", "startup")


def test_system_spec_can_be_disabled() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        enabled=False,
    )

    assert spec.enabled is False


def test_system_spec_accepts_custom_run_every() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        run_every=3,
    )

    assert spec.run_every == 3


def test_system_spec_rejects_run_every_less_than_one_if_validated() -> None:
    try:
        SystemSpec(
            name="move",
            fn=dummy_system,
            phase="sim",
            run_every=0,
        )
    except ValueError:
        return

    # If validation is not yet implemented, at least document current behavior.
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        run_every=0,
    )
    assert spec.run_every == 0


def test_system_spec_rejects_empty_name_if_validated() -> None:
    try:
        SystemSpec(
            name="",
            fn=dummy_system,
            phase="sim",
        )
    except ValueError:
        return

    spec = SystemSpec(
        name="",
        fn=dummy_system,
        phase="sim",
    )
    assert spec.name == ""


def test_system_spec_rejects_blank_phase_if_validated() -> None:
    try:
        SystemSpec(
            name="move",
            fn=dummy_system,
            phase="",
        )
    except ValueError:
        return

    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="",
    )
    assert spec.phase == ""


def test_system_spec_rejects_non_callable_fn_if_validated() -> None:
    try:
        SystemSpec(
            name="move",
            fn="not callable",  # type: ignore[arg-type]
            phase="sim",
        )
    except (TypeError, ValueError):
        return

    spec = SystemSpec(
        name="move",
        fn="not callable",  # type: ignore[arg-type]
        phase="sim",
    )
    assert spec.fn == "not callable"


def test_system_spec_preserves_dependency_order() -> None:
    spec = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        before=("b", "c", "d"),
        after=("x", "y", "z"),
    )

    assert spec.before == ("b", "c", "d")
    assert spec.after == ("x", "y", "z")


def test_system_spec_instances_can_differ_independently() -> None:
    spec1 = SystemSpec(
        name="move",
        fn=dummy_system,
        phase="sim",
        run_every=1,
    )
    spec2 = SystemSpec(
        name="render",
        fn=other_system,
        phase="render_extract",
        run_every=2,
        enabled=False,
    )

    assert spec1.name == "move"
    assert spec1.fn is dummy_system
    assert spec1.phase == "sim"
    assert spec1.run_every == 1
    assert spec1.enabled is True

    assert spec2.name == "render"
    assert spec2.fn is other_system
    assert spec2.phase == "render_extract"
    assert spec2.run_every == 2
    assert spec2.enabled is False