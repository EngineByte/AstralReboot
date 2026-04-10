from __future__ import annotations

import logging

from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.bootstrap.resource_bootstrap import EngineConfig, FrameClock

logger = logging.getLogger(__name__)


def system_log_startup(world: ECSWorld, dt: float) -> None:
    config = world.get_required_resource(EngineConfig)
    logger.info(
        'Startup system ran. debug=%s fixed_dt=%s',
        config.debug,
        config.fixed_dt,
    )


def system_advance_frame_clock(world: ECSWorld, dt: float) -> None:
    clock = world.get_required_resource(FrameClock)
    clock.frame += 1
    clock.dt = dt


def register_systems(world: ECSWorld) -> None:
    '''
    Register core engine/application systems.
    '''
    world.add_system(
        SystemSpec(
            name='log_startup',
            fn=system_log_startup,
            phase='startup',
        )
    )

    world.add_system(
        SystemSpec(
            name='advance_frame_clock',
            fn=system_advance_frame_clock,
            phase='pre_sim',
        )
    )