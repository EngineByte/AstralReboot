from __future__ import annotations

from logging import Logger

from astralengine.app.logging_setup import get_logger


def startup_system(world, dt: float) -> None:
    logger: Logger = get_logger('systems.lifecycle')
    logger.info('AstralEngine startup phase running.')