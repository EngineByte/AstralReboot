from __future__ import annotations

from astralengine.app.logging_setup import get_logger
from astralengine.flow.states.loading_world import LoadingWorldState


class MainMenuState:
    name = 'main_menu'

    def on_enter(self, app) -> None:
        get_logger('flow.main_menu').info('Entered MainMenuState.')

    def update(self, app, dt: float) -> None:
        # Placeholder behavior:
        # auto-advance into a world load for now.
        #
        # Later this is where menu UI/input decides:
        # - new world
        # - load world
        # - settings
        # - quit
        app.change_state(LoadingWorldState())

    def render(self, app) -> None:
        pass

    def on_exit(self, app) -> None:
        get_logger('flow.main_menu').info('Exited MainMenuState.')