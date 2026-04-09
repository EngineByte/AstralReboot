from __future__ import annotations

import pytest

from astralengine.ecs.scheduling.system_spec import SystemSpec


def test_system_spec_requires_name() -> None:
    with pytest.raises((TypeError, ValueError)):
        SystemSpec(name="", fn=lambda world, dt: None, phase="sim")


def test_system_spec_requires_callable_fn() -> None:
    with pytest.raises((TypeError, ValueError)):
        SystemSpec(name="bad", fn=None, phase="sim")  # type: ignore[arg-type]s