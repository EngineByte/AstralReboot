from __future__ import annotations

import pytest

from astralengine.ecs.scheduling.system_spec import SystemSpec


def dummy_system(world, dt: float) -> None:
    pass


def test_system_spec_validation_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        SystemSpec(
            name="",
            fn=dummy_system,
            phase="sim",
        )


def test_system_spec_validation_rejects_blank_name() -> None:
    with pytest.raises(ValueError):
        SystemSpec(
            name="   ",
            fn=dummy_system,
            phase="sim",
        )


def test_system_spec_validation_rejects_empty_phase() -> None:
    with pytest.raises(ValueError):
        SystemSpec(
            name="move",
            fn=dummy_system,
            phase="",
        )


def test_system_spec_validation_rejects_blank_phase() -> None:
    with pytest.raises(ValueError):
        SystemSpec(
            name="move",
            fn=dummy_system,
            phase="   ",
        )


def test_system_spec_validation_rejects_non_callable_fn() -> None:
    with pytest.raises((TypeError, ValueError)):
        SystemSpec(
            name="move",
            fn=None,  # type: ignore[arg-type]
            phase="sim",
        )


def test_system_spec_validation_rejects_run_every_zero() -> None:
    with pytest.raises(ValueError):
        SystemSpec(
            name="move",
            fn=dummy_system,
            phase="sim",
            run_every=0,
        )


def test_system_spec_validation_rejects_run_every_negative() -> None:
    with pytest.raises(ValueError):
        SystemSpec(
            name="move",
            fn=dummy_system,
            phase="sim",
            run_every=-1,
        )