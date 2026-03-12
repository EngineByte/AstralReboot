from __future__ import annotations

import numpy as np

from astralengine.ecs.query import Query
from astralengine.ecs.world import ECSWorld
from astralengine.components.chunk import Chunk
from astralengine.components.mesh import Mesh
from astralengine.components.transform import Transform
from astralengine.components.tags import DirtyRemesh

from astralengine.voxels.voxel_pool import VoxelPool
from astralengine.voxels.mesh_pool import MeshPool
from astralengine.voxels.meshing import build_surface_mesh_from_voxels


def system_chunk_remesh(world: 'ECSWorld', dt: float) -> None:
    chunks = world.store(Chunk)    
    meshes = world.store(Mesh)
    tr = world.store(Transform)

    voxel_pool = world.resources.get(VoxelPool)
    mesh_pool = world.resources.get(MeshPool)

    for eid, i_chunk, i_mesh in Query(world, (Chunk, Mesh, DirtyRemesh)):
        size = int(chunks.size[i_chunk])
        handle = int(chunks.voxel_handle[i_chunk])

        block = voxel_pool.block(handle)
        verts, indices = build_surface_mesh_from_voxels(block.data, size=size, method='greedy')

        cur_mesh_id = int(meshes.mesh_id[i_mesh])
        new_mesh_id = mesh_pool.upload_or_replace(cur_mesh_id, verts, indices)
        meshes.mesh_id[i_mesh] = new_mesh_id

        world.defer_remove_tag(eid, DirtyRemesh)