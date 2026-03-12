from __future__ import annotations

from astralengine.components.camera import Camera
from astralengine.components.camera_matrices import CameraMatrices
from astralengine.components.parent_follow import ParentFollow
from astralengine.components.tags import ActiveCamera, DirtyMatrices
from astralengine.components.transform import Transform
from astralengine.ecs.world import ECSWorld
from astralengine.game.specs.camera_spec import CameraSpec


def spawn_follow_camera(world: ECSWorld, spec: CameraSpec) -> int:
    eid = world.create_entity()

    world.add_component(
        eid,
        Transform(
            position=spec.position,
            rotation=spec.rotation,
            scale=(1.0, 1.0, 1.0),
        ),
    )
    world.add_component(
        eid,
        Camera(
            fov=spec.fov,
            near=spec.near,
            far=spec.far,
        ),
    )
    world.add_component(
        eid,
        CameraMatrices.identity(),
    )

    if spec.parent_eid is not None:
        world.add_component(
            eid,
            ParentFollow(
                parent_eid=spec.parent_eid,
                offset=spec.follow_offset,
                follow_position=spec.follow_position,
                follow_rotation=spec.follow_rotation,
            ),
        )

    world.add_tag(eid, DirtyMatrices)

    if spec.make_active:
        world.add_tag(eid, ActiveCamera)

    return eid