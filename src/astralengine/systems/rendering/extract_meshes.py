from __future__ import annotations

import numpy as np

from astralengine.components.mesh import Mesh
from astralengine.components.transform import Transform
from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.rendering.draw_packet import DrawPacket
from astralengine.resources.render_queue import RenderQueue


def _identity_mat4() -> np.ndarray:
    return np.eye(4, dtype=np.float32)


def _build_model_matrix(transform: Transform) -> np.ndarray:
    '''
    Minimal first-pass model matrix builder.

    For now:
    - uses transform.model_matrix if present
    - otherwise falls back to translation-only

    Later you can replace this with your real compose helper once your
    transform math utilities are in place.
    '''
    model_matrix = getattr(transform, 'model_matrix', None)
    if model_matrix is not None:
        return model_matrix

    matpos = _identity_mat4()
    matpos[:3, 3] = transform.position

    matrotyaw = _identity_mat4()
    matrotpitch = _identity_mat4()
    matrotroll = _identity_mat4()

    y, p, r = transform.rotation

    yaw = np.radians(y)
    pitch = np.radians(p)
    roll = np.radians(r)

    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)

    matrotyaw[0, 0], matrotyaw[2, 2] = cy, cy
    matrotyaw[0, 2], matrotyaw[2, 0] = -sy, sy
    
    matrotpitch[1, 1], matrotpitch[2, 2] = cp, cp
    matrotpitch[1, 2], matrotpitch[2, 1] = sp, -sp

    matrotroll[0, 0], matrotroll[1, 1] = cr, cr
    matrotroll[0, 1], matrotroll[1, 0] = -sr, sr

    model_matrix = matpos @ matrotyaw @ matrotpitch @ matrotyaw

    return model_matrix


def system_extract_meshes(world: ECSWorld, dt: float) -> None:
    '''
    Extract visible mesh-bearing entities into the RenderQueue resource.
    '''
    _ = dt

    render_queue = world.get_required_resource(RenderQueue)
    render_queue.clear()

    for entity, (transform, mesh,) in world.query((Transform, Mesh)):
        if not mesh.visible:
            continue

        render_queue.add(
            DrawPacket(
                entity=entity,
                mesh_id=mesh.mesh_id,
                material_id=mesh.material_id,
                shader_id=mesh.shader_id,
                model_matrix=_build_model_matrix(transform),
            )
        )


def register_render_mesh_systems(scheduler: SystemScheduler) -> None:
    '''
    Register mesh extraction systems.
    '''
    scheduler.add_system(
        SystemSpec(
            name='extract_meshes',
            fn=system_extract_meshes,
            phase='render_extract',
        )
    )