from __future__ import annotations

import logging
from dataclasses import dataclass

from astralengine.app.logging_setup import configure_logging, get_logger
from astralengine.app.paths import configure_paths


@dataclass(slots=True)
class ApplicationContext:
    '''
    Process-level application context.
    '''
    logger: logging.Logger
    debug: bool = False
    headless: bool = False
    window: object | None = None
    renderer: object | None = None


def initialize_application(
    *,
    debug: bool = False,
    headless: bool = False,
) -> ApplicationContext:
    '''
    Perform process-level startup prior to any ECS world construction.
    '''
    configure_paths()

    logger = configure_logging(
        level=logging.DEBUG if debug else logging.INFO,
        debug=debug,
        console=True if debug else False
    )

    app_logger = get_logger('app.startup')
    app_logger.info('Application initialization started.')
    app_logger.debug('Debug mode: %s', debug)
    app_logger.debug('Headless mode: %s', headless)
    app_logger.info('Application initialization completed.')

    return ApplicationContext(
        logger=logger,
        debug=debug,
        headless=headless,
    )