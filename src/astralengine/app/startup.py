from __future__ import annotations

from astralengine.app.logging_setup import configure_logging
from astralengine.app.paths import configure_paths


def initialize_application() -> None:
    configure_paths()
    configure_logging()