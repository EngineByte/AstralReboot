from __future__ import annotations

import pytest
from astralengine.app.startup import ApplicationContext
from astralengine.bootstrap.application import (
    ApplicationConfig,
    build_application_runtime,
)
from astralengine.runtime.app_runner import run_app

pytestmark = [
    pytest.mark.integration,
    pytest.mark.application,
]


class _NullLogger:
    def debug(self, msg, *args, **kwargs) -> None:
        pass

    def info(self, msg, *args, **kwargs) -> None:
        pass

    def warning(self, msg, *args, **kwargs) -> None:
        pass

    def error(self, msg, *args, **kwargs) -> None:
        pass

    def exception(self, msg, *args, **kwargs) -> None:
        pass


def test_application_smoke() -> None:
    context = ApplicationContext(
        logger=_NullLogger(),
        debug=False,
        headless=True,
    )

    runtime = build_application_runtime(
        context=context,
        config=ApplicationConfig(
            max_frames=3,
            target_fps=None,
        ),
    )

    exit_code = run_app(runtime)
    assert exit_code == 0