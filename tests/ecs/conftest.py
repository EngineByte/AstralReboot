from __future__ import annotations

from dataclasses import dataclass

import pytest

from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.scheduler import SystemScheduler


@dataclass
class Counter:
    value: int = 0


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Velocity:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Lifetime:
    frames_left: int = 0


class Active:
    pass


class Frozen:
    pass


@pytest.fixture
def world() -> ECSWorld:
    world = ECSWorld()
    world.bind_scheduler(SystemScheduler())
    return world