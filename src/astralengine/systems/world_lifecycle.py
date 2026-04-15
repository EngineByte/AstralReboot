from __future__ import annotations

from astralengine.app.logging_setup import get_logger
from astralengine.ecs.scheduling.system_spec import SystemSpec


logger = get_logger('systems.world_lifecycle')


def world_startup_system(world, dt: float) -> None:
    logger.info('World startup phase running.')


def world_shutdown_system(world, dt: float) -> None:
    logger.info('World shutdown phase running.')


def register_world_lifecycle_systems(scheduler) -> None:
    scheduler.add_system(
        SystemSpec(
            name='world.startup',
            fn=world_startup_system,
            phase='startup',
        )
    )
    scheduler.add_system(
        SystemSpec(
            name='world.shutdown',
            fn=world_shutdown_system,
            phase='shutdown',
        )
    )