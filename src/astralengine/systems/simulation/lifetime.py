from __future__ import annotations

from typing import TYPE_CHECKING

from astralengine.components.lifecycle import Lifetime
from astralengine.ecs.scheduling.system_spec import SystemSpec

if TYPE_CHECKING:
    from astralengine.ecs.core.world import ECSWorld
    from astralengine.ecs.scheduling.scheduler import SystemScheduler


def lifetime_decay_system(world: ECSWorld, dt: float) -> None:
    for eid, (lifetime,) in world.query((Lifetime,)):
        lifetime.remaining -= dt
        if lifetime.remaining <= 0.0:
            world.defer_destroy_entity(eid)


def register_lifetime_systems(scheduler: SystemScheduler) -> None:
    scheduler.add_system(
        SystemSpec(
            name='simulation.lifetime_decay',
            fn=lifetime_decay_system,
            phase='post_sim',
        )
    )