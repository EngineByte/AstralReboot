from __future__ import annotations

import logging

from astralengine.app.startup import initialize_application
from astralengine.bootstrap.application import run_application

logger = logging.getLogger(__name__)

def main() -> int:
    try:
        initialize_application()
        run_application()
        return 0
    except KeyboardInterrupt:
        logger.info('Application interupted by user.')
        return 130
    except Exception:
        logger.exception('Fatal application error.')
        return 1