from __future__ import annotations

import numpy as np

from astralengine._legacy.components.chunk import Chunk
from astralengine._legacy.components.mesh import Mesh
from astralengine._legacy.components.model_matrix import ModelMatrix
from astralengine._legacy.components.chunk_residency import ChunkResidency
from astralengine._legacy.components.chunk_lod import ChunkLOD
from astralengine.ecs.query.query import Query
from astralengine.ecs.core.world import ECSWorld
from astralengine._legacy.rendering.pipeline.draw_commands import MeshDrawCommand
from astralengine._legacy.rendering.renderer import Renderer
from astralengine._legacy.resources.render_settings import RenderSettings
from astralengine._legacy.stores.mesh_store import MeshStore
from astralengine._legacy.stores.model_matrix_store import ModelMatrixStore


def system_submit_chunks(world: ECSWorld, dt: float) -> None:
    _ = dt

    renderer = world.resources.get(Renderer)
    settings = world.resources.get(RenderSettings)

    if not settings.draw_opaque:
        return

    mesh_store: MeshStore = world.store(Mesh)
    model_store: ModelMatrixStore = world.store(ModelMatrix)

    for eid, i_chunk, i_mesh, i_model in Query(world, (Chunk, Mesh, ModelMatrix)):
        mesh_id = int(mesh_store.mesh_id[i_mesh])
        if mesh_id < 0:
            continue

        model = np.array(model_store.model[i_model], dtype=np.float32, copy=False)

        renderer.queue.submit_mesh(
            MeshDrawCommand(
                mesh_id=mesh_id,
                model=model,
                material_name="chunk_opaque",
            )
        )