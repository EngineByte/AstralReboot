from __future__ import annotations

from dataclasses import dataclass

from astralengine.app.startup import ApplicationContext
from astralengine.bootstrap.application import ApplicationConfig
from astralengine.bootstrap.demo_scene import create_demo_scene
from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.phases import ALL_PHASES
from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.resources.camera_state import CameraState
from astralengine.resources.diagnostics import DiagnosticStats
from astralengine.resources.render_queue import RenderQueue
from astralengine.resources.scenes import SceneBootstrapState, TestSceneConfig
from astralengine.resources.time import FrameClock, FrameStats
from astralengine.systems.core.diagnostics import register_diagnostic_systems
from astralengine.systems.core.test_scene import register_test_scene_systems
from astralengine.systems.core.timekeeping import register_core_systems
from astralengine.systems.rendering import register_render_extract_systems
from astralengine.systems.simulation.lifetime import register_lifetime_systems
from astralengine.systems.simulation.movement import register_movement_systems
from astralengine.systems.world_lifecycle import register_world_lifecycle_systems


@dataclass(slots=True)
class SimulationSession:
    '''
    A single loaded simulation session.

    This is distinct from the overall application lifetime.
    '''
    context: ApplicationContext
    world: ECSWorld
    config: ApplicationConfig


def _register_core_resources(world: ECSWorld, context: ApplicationContext) -> None:
    world.add_resource(context)
    world.add_resource(FrameClock())
    world.add_resource(FrameStats())
    world.add_resource(SceneBootstrapState())
    world.add_resource(TestSceneConfig())
    world.add_resource(DiagnosticStats(log_every_n_frames=60))

    # Render-facing extracted resources
    world.add_resource(CameraState())
    world.add_resource(RenderQueue())


def _register_core_systems(scheduler: SystemScheduler) -> None:
    register_world_lifecycle_systems(scheduler)
    register_core_systems(scheduler)
    register_movement_systems(scheduler)
    register_lifetime_systems(scheduler)
    register_render_extract_systems(scheduler)
    register_diagnostic_systems(scheduler)


def build_simulation_session(
    *,
    context: ApplicationContext,
    config: ApplicationConfig,
) -> SimulationSession:
    '''
    Compose and return a single simulation session.
    '''
    world = ECSWorld()
    scheduler = SystemScheduler(phases=ALL_PHASES)
    world.bind_scheduler(scheduler)

    _register_core_resources(world, context)
    _register_core_systems(scheduler)

    create_demo_scene(world)

    return SimulationSession(
        context=context,
        world=world,
        config=config,
    )