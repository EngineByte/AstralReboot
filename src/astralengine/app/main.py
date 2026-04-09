from __future__ import annotations

from astralengine.app.startup import initialize_application
from astralengine.bootstrap.application import run_application


def main() -> None:
    initialize_application()
    run_application()