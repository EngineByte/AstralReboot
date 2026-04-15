from __future__ import annotations

import argparse
import logging

from astralengine.app.startup import initialize_application
from astralengine.bootstrap.application import (
    ApplicationConfig,
    build_application_runtime,
)
from astralengine.runtime.app_runner import run_app


logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames', type=int, default=None)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()

    try:
        context = initialize_application(
            debug=args.debug,
            headless=args.headless,
        )

        runtime = build_application_runtime(
            context=context,
            config=ApplicationConfig(
                fixed_dt=1.0 / 60.0,
                max_frames=args.frames,
                target_fps=None if args.headless else 60.0,
            ),
        )

        return run_app(runtime)

    except Exception:
        logger.exception('Fatal application error.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())