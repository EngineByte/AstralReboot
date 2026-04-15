from __future__ import annotations

from logging import Logger

from astralengine.app.logging_setup import get_logger


LOGGER_RESOURCE = 'root_logger'


def shutdown_system(world, dt: float) -> None:
    logger: Logger = get_logger('systems.lifecycle')
    logger.info('AstralEngine shutdown phase running.')

