from __future__ import annotations

import logging
import argparse

from astralengine.app.startup import initialize_application
from astralengine.bootstrap.application import (
    run_application, 
    ApplicationConfig
)

logger = logging.getLogger(__name__)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames', type=int, default=None)
    parser.add_argument('--headless', action='store_true')

    args = parser.parse_args()

    try:
        initialize_application()
        config = ApplicationConfig(
            fixed_dt=1.0 / 60.0,
            max_frames=args.frames,
            target_fps=None if args.headless else 60.0
        )

        return run_application(config=config)
    
    except KeyboardInterrupt:
        logger.info('Application interupted by user.')

        return 130
    
    except Exception:
        logger.exception('Fatal application error.')

        return 1
    

if __name__ == '__main__':
    raise SystemExit(main())