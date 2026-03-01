from __future__ import annotations

from ecs.query import Query
from ecs.world import ECSWorld
from components.mesh import Mesh
from renderer.renderer import Renderer
from renderer.mesh_pool import MeshPool


def system_chunk_render(world: "ECSWorld", dt: float) -> None:
    renderer = world.resources.get(Renderer)
    mesh_pool = world.resources.get(MeshPool)

    chunk_mesh = world.store(Mesh)

    for eid, i_mesh in Query(world, (Mesh,)):
        mesh_id = int(chunk_mesh.mesh_id[i_mesh])
        if mesh_id < 0:
            continue

        mesh = mesh_pool.get(mesh_id)
        if mesh is None or mesh.indices.size == 0:
            continue
        
        renderer.draw_mesh(mesh_id, mesh.verts, mesh.indices)
        
    renderer.end_frame()
        