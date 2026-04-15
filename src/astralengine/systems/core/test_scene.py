from __future__ import annotations

from astralengine.app.logging_setup import get_logger
from astralengine.components.lifecycle import Lifetime
from astralengine.components.motion import Velocity
from astralengine.components.transform import Transform
from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.resources.scenes import SceneBootstrapState, TestSceneConfig


logger = get_logger('systems.core.test_scene')


def spawn_test_scene_system(world, dt: float) -> None:
    bootstrap_state = world.get_resource(SceneBootstrapState)
    if bootstrap_state.did_spawn_initial_scene:
        return

    config = world.get_resource(TestSceneConfig)

    for i in range(config.entity_count):
        eid = world.create_entity()
        world.add_component(
            eid,
            Transform(x=float(i) * config.initial_x_spacing, y=0.0),
        )
        world.add_component(
            eid,
            Velocity(x=config.velocity_x, y=config.velocity_y),
        )
        world.add_component(
            eid,
            Lifetime(remaining=config.lifetime_sec),
        )

    bootstrap_state.did_spawn_initial_scene = True
    logger.info('Spawned test scene with %d entities.', config.entity_count)


def register_test_scene_systems(scheduler) -> None:
    scheduler.add_system(
        SystemSpec(
            name='core.spawn_test_scene',
            fn=spawn_test_scene_system,
            phase='startup',
            after=('world.startup',),
        )
    )