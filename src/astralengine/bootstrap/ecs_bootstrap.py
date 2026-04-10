from __future__ import annotations

from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.phases import PhaseSpec
from astralengine.ecs.scheduling.scheduler import SystemScheduler


def build_world() -> ECSWorld:
    '''
    Construct the ECS world and bind a scheduler.

    This is the central ECS bootstrap point.
    '''
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name='startup', commit_after=True),
            PhaseSpec(name='input', commit_after=True),
            PhaseSpec(name='pre_sim', commit_after=True),
            PhaseSpec(name='sim', commit_after=True),
            PhaseSpec(name='post_sim', commit_after=True),
            PhaseSpec(name='cleanup', commit_after=True),
        )
    )

    world = ECSWorld()
    world.bind_scheduler(scheduler)
    return world