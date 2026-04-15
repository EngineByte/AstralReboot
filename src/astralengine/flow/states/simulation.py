from __future__ import annotations

from astralengine.app.logging_setup import get_logger


class SimulationState:
    name = 'simulation'

    def on_enter(self, app) -> None:
        get_logger('flow.simulation').info('Entered SimulationState.')

    def update(self, app, dt: float) -> None:
        if app.simulation_session is None:
            raise RuntimeError('SimulationState requires an active simulation session.')

        app.run_simulation_frame()

        if app.should_end_simulation():
            app.shutdown_requested = True

    def render(self, app) -> None:
        pass

    def on_exit(self, app) -> None:
        get_logger('flow.simulation').info('Exited SimulationState.')