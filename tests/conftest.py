# tests/conftest.py
import pytest

from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.scheduler import SystemScheduler


@pytest.fixture
def world() -> ECSWorld:
    world = ECSWorld()
    world.bind_scheduler(SystemScheduler())
    return world