from __future__ import annotations

from astralengine.app.logging_setup import get_logger
from astralengine.bootstrap.simulation import build_simulation_session
from astralengine.flow.states.simulation import SimulationState


class LoadingWorldState:
    name = 'loading_world'

    def on_enter(self, app) -> None:
        get_logger('flow.loading_world').info('Entered LoadingWorldState.')

    def update(self, app, dt: float) -> None:
        session = build_simulation_session(
            context=app.runtime.context,
            config=app.runtime.config,
        )
        app.simulation_session = session
        app.change_state(SimulationState())

    def render(self, app) -> None:
        pass

    def on_exit(self, app) -> None:
        get_logger('flow.loading_world').info('Exited LoadingWorldState.')