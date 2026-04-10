from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.core.world import ECSWorld


@dataclass(slots=True)
class EngineConfig:
    fixed_dt: float = 1.0 / 60.0
    max_frames: int = 1
    debug: bool = True


@dataclass(slots=True)
class FrameClock:
    frame: int = 0
    dt: float = 1.0 / 60.0


def register_resources(world: ECSWorld) -> None:
    '''
    Register core application resources into the ECS world.
    '''
    world.add_resource(EngineConfig())
    world.add_resource(FrameClock())