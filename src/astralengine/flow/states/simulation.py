from __future__ import annotations

from astralengine.app.logging_setup import get_logger
from astralengine.resources.camera_state import CameraState
from astralengine.resources.render_queue import RenderQueue


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
        context = app.runtime.context
        session = app.simulation_session
        world = session.world

        renderer = context.renderer

        if renderer is None:
            return
        
        render_queue = world.get_required_resource(RenderQueue)
        camera_state = world.get_required_resource(CameraState)
        
        renderer.begin_frame()
        renderer.render_scene(render_queue, camera_state)
        renderer.end_frame()

    def on_exit(self, app) -> None:
        get_logger('flow.simulation').info('Exited SimulationState.')