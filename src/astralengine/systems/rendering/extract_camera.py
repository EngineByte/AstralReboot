from __future__ import annotations

from astralengine.components.camera import Camera
from astralengine.components.transform import Transform
from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.resources.camera_state import CameraState


def _select_active_camera(
    world: ECSWorld,
) -> tuple[int, Transform, Camera] | None:
    '''
    Return the first active camera found.

    Assumes:
    - world.query(Transform, Camera) yields:
        (entity_id, transform_component, camera_component)
    '''
    for entity, (transform, camera,) in world.query((Transform, Camera)):
        if camera.active:
            return entity, transform, camera
    return None


def system_extract_camera(world: ECSWorld, dt: float) -> None:
    '''
    Extract the active ECS camera into CameraState.
    '''
    _ = dt

    camera_state = world.get_required_resource(CameraState)
    selected = _select_active_camera(world)

    if selected is None:
        camera_state.entity = None
        camera_state.is_valid = False
        return

    entity, transform, camera = selected

    camera_state.entity = entity
    camera_state.is_valid = True

    camera_state.position = transform.position.copy()
    camera_state.rotation = transform.rotation.copy()

    camera_state.fov_y_degrees = camera.fov_y_degrees
    camera_state.near_clip = camera.near_clip
    camera_state.far_clip = camera.far_clip
    camera_state.projection_mode = camera.projection_mode
    camera_state.aspect_ratio_override = camera.aspect_ratio_override


def register_render_camera_systems(scheduler: SystemScheduler) -> None:
    '''
    Register camera extraction systems.
    '''
    scheduler.add_system(
        SystemSpec(
            name='extract_camera',
            fn=system_extract_camera,
            phase='render_extract',
        )
    )