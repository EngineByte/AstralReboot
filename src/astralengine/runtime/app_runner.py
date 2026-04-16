from __future__ import annotations

from dataclasses import dataclass, field

from astralengine.app.logging_setup import get_logger
from astralengine.bootstrap.application import ApplicationRuntime
from astralengine.bootstrap.simulation import SimulationSession
from astralengine.flow.state_machine import StateMachine
from astralengine.flow.states.boot import BootState
from astralengine.runtime.simulation_runner import SimulationRunner


@dataclass(slots=True)
class AppController:
    '''
    High-level application controller.

    Owns the app state machine and, when active, a simulation session.
    '''
    runtime: ApplicationRuntime
    state_machine: StateMachine = field(default_factory=StateMachine)
    simulation_session: SimulationSession | None = None
    simulation_runner: SimulationRunner | None = None
    shutdown_requested: bool = False

    def change_state(self, new_state) -> None:
        self.state_machine.change_state(self, new_state)

    def run_simulation_frame(self) -> None:
        if self.simulation_session is None:
            raise RuntimeError('No simulation session is active.')

        if self.simulation_runner is None:
            self.simulation_runner = SimulationRunner(self.simulation_session)

        self.simulation_runner.run_one_frame()

    def should_end_simulation(self) -> bool:
        cfg = self.runtime.config
        if self.simulation_runner is None:
            return False

        if cfg.max_frames is None:
            return False

        return self.simulation_runner.frame_index >= cfg.max_frames

    def shutdown_simulation(self) -> None:
        if self.simulation_runner is not None:
            self.simulation_runner.shutdown()
            self.simulation_runner = None

        self.simulation_session = None


def run_app(runtime: ApplicationRuntime) -> int:
    '''
    Run the high-level application flow.
    '''
    logger = get_logger('runtime.app')
    app = AppController(runtime=runtime)

    try:
        app.change_state(BootState())

        while not app.shutdown_requested:
            window = runtime.context.window
            if window is not None:
                window.poll_events()
                if window.should_close():
                    app.shutdown_requested = True
                    break

            app.state_machine.update(app, runtime.config.fixed_dt)
            app.state_machine.render(app)

        logger.info('Application shutdown requested.')

    except KeyboardInterrupt:
        logger.info('Application interrupted by user.')

    except Exception:
        logger.exception('Unhandled exception in application controller.')
        return 1

    finally:
        app.shutdown_simulation()

        renderer = runtime.context.renderer
        if renderer is not None:
            renderer.shutdown()
        
        window = runtime.context.window
        if window is not None:
            window.close()

    return 0