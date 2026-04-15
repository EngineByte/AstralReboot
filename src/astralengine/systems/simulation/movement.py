from __future__ import annotations

from astralengine.components.motion import Velocity
from astralengine.components.transform import Transform
from astralengine.ecs.scheduling.system_spec import SystemSpec


def movement_system(world, dt: float) -> None:
    for _eid, (transform, velocity) in world.query((Transform, Velocity)):
        transform.x += velocity.x * dt
        transform.y += velocity.y * dt


def register_movement_systems(scheduler) -> None:
    scheduler.add_system(
        SystemSpec(
            name='simulation.movement',
            fn=movement_system,
            phase='sim',
        )
    )