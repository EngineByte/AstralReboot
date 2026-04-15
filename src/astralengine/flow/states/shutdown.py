from __future__ import annotations

from astralengine.app.logging_setup import get_logger


class ShutdownState:
    name = 'shutdown'

    def on_enter(self, app) -> None:
        get_logger('flow.shutdown').info('Entered ShutdownState.')
        app.shutdown_requested = True

    def update(self, app, dt: float) -> None:
        pass

    def render(self, app) -> None:
        pass

    def on_exit(self, app) -> None:
        get_logger('flow.shutdown').info('Exited ShutdownState.')