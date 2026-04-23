from __future__ import annotations

import numpy as np

from astralengine.components.camera import Camera
from astralengine.components.mesh import Mesh
from astralengine.components.transform import Transform
from astralengine.ecs.core.world import ECSWorld


def _vec3(x: float, y: float, z: float) -> np.ndarray:
    return np.array([x, y, z], dtype=np.float32)


def create_demo_scene(world: ECSWorld) -> None:
    '''
    Create a minimal test scene:

    - player entity
    - active camera entity
    - cube entity at origin
    - second cube for sanity checking

    This validates:
    ECS entities -> extraction systems -> render resources -> renderer.
    '''

    # ------------------------------------------------------------------
    # Player
    # ------------------------------------------------------------------
    player = world.create_entity()

    world.add_component(
        player,
        Transform(
            position=_vec3(0.0, 0.0, -10.0),
            rotation=_vec3(0.0, 0.0, 0.0),
        ),
    )

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------
    camera = world.create_entity()

    world.add_component(
        camera,
        Transform(
            position=_vec3(0.0, 1.5, -10.0),
            rotation=_vec3(0.0, 0.0, 0.0),
        ),
    )

    world.add_component(
        camera,
        Camera(
            active=True,
            fov_y_degrees=60.0,
            near_clip=0.1,
            far_clip=100.0,
        ),
    )

    # ------------------------------------------------------------------
    # Cube 1
    # ------------------------------------------------------------------
    cube = world.create_entity()

    world.add_component(
        cube,
        Transform(
            position=_vec3(0.0, 0.0, 0.0),
            rotation=_vec3(0.0, 0.0, 0.0),
        ),
    )

    world.add_component(
        cube,
        Mesh(
            mesh_id='cube',
            material_id=None,
            shader_id='solid',
            visible=True,
        ),
    )

    # ------------------------------------------------------------------
    # Cube 2
    # ------------------------------------------------------------------
    cube2 = world.create_entity()

    world.add_component(
        cube2,
        Transform(
            position=_vec3(2.0, 0.0, 0.0),
            rotation=_vec3(0.0, 0.0, 0.0),
        ),
    )

    world.add_component(
        cube2,
        Mesh(
            mesh_id='cube',
            material_id=None,
            shader_id='solid',
            visible=True,
        ),
    )