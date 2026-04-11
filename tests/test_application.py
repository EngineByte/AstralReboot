from __future__ import annotations

import pytest

from astralengine.bootstrap.application import ApplicationConfig, run_application

pytestmark = [
    pytest.mark.application,
    pytest.mark.unit
]


def test_application_smoke() -> None:
    exit_code = run_application(
        config=ApplicationConfig(
            max_frames=3,
            target_fps=None,
        )
    )

    assert exit_code == 0