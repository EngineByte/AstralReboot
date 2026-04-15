from __future__ import annotations

from astralengine.app.logging_setup import get_logger
from astralengine.flow.states.main_menu import MainMenuState


class BootState:
    name = 'boot'

    def on_enter(self, app) -> None:
        get_logger('flow.boot').info('Entered BootState.')

    def update(self, app, dt: float) -> None:
        # Later:
        # - splash screen
        # - asset warmup
        # - platform service readiness checks
        app.change_state(MainMenuState())

    def render(self, app) -> None:
        pass

    def on_exit(self, app) -> None:
        get_logger('flow.boot').info('Exited BootState.')