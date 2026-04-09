from __future__ import annotations

from astralengine.ecs.core.world import ECSWorld
from astralengine.bootstrap.system_bootstrap import install_core_ecs_systems


def create_ecs_world() -> ECSWorld:
    '''
    Create a new ECS world in its minimal runable form.
    '''

    world = ECSWorld()

    install_core_ecs_systems(world)

    return world