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


def _translation_mat4(position: np.ndarray) -> np.ndarray:
    mat = _identity_mat4()
    mat[:3, 3] = position
    return mat


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

    return _translation_mat4(transform.position)


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