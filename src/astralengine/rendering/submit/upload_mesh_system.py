from __future__ import annotations

from astralengine.components.chunk import Chunk
from astralengine.components.mesh import Mesh
from astralengine.components.tags import DirtyRemesh
from astralengine.ecs.query.query import Query
from astralengine.ecs.core.world import ECSWorld
from astralengine.rendering.backend.gpu_mesh_cache import GpuMeshCache
from astralengine.stores.mesh_store import MeshStore
from astralengine.voxels.mesh_pool import MeshPool


def system_upload_chunk_meshes(world: ECSWorld, dt: float) -> None:
    _ = dt

    mesh_store: MeshStore = world.store(Mesh)
    mesh_pool = world.resources.get(MeshPool)
    gpu_mesh_cache = world.resources.get(GpuMeshCache)

    for eid, i_chunk, i_mesh in Query(world, (Chunk, Mesh, DirtyRemesh)):
        mesh_id = int(mesh_store.mesh_id[i_mesh])
        if mesh_id < 0:
            continue

        mesh = mesh_pool.try_get(mesh_id)
        if mesh is None:
            continue

        gpu_mesh_cache.upload_or_replace(mesh_id, mesh)