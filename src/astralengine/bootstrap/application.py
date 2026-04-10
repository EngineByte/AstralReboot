from __future__ import annotations

import logging

from astralengine.bootstrap.ecs_bootstrap import build_world
from astralengine.bootstrap.resource_bootstrap import EngineConfig, register_resources
from astralengine.bootstrap.system_bootstrap import register_systems
from astralengine.ecs.core.world import ECSWorld

logger = logging.getLogger(__name__)


def bootstrap_application_world() -> ECSWorld:
    '''
    Build and fully initialize the ECS application world.
    '''
    world = build_world()
    register_resources(world)
    register_systems(world)
    return world


def run_application() -> None:
    '''
    Build the application world and run the main loop.

    Current behavior:
    - run startup phase once
    - run a short fixed-step loop controlled by EngineConfig.max_frames
    '''
    world = bootstrap_application_world()

    logger.info('Application bootstrap complete: %s', world.summary())

    world.run_phase('startup', 0.0)

    config = world.get_required_resource(EngineConfig)
    dt = config.fixed_dt

    for _ in range(config.max_frames):
        world.run_phase('input', dt)
        world.run_phase('pre_sim', dt)
        world.run_phase('sim', dt)
        world.run_phase('post_sim', dt)
        world.run_phase('cleanup', dt)

    logger.info('Application shutdown complete: %s', world.summary())