from __future__ import annotations

from astralengine.components.acceleration import Acceleration
from astralengine.components.chunk import Chunk
from astralengine.components.gravity import GravityWell
from astralengine.components.mass import Mass
from astralengine.components.mesh import Mesh
from astralengine.components.model_matrix import ModelMatrix
from astralengine.components.tags import DirtyMatrices, DirtyRemesh, DirtyRemodel
from astralengine.components.transform import Transform
from astralengine.components.velocity import Velocity
from astralengine.ecs.world import ECSWorld
from astralengine.game.specs.chunk_spec import ChunkSpec
from astralengine.voxels.chunk_map import ChunkMap
from astralengine.voxels.voxel_pool import VoxelPool


def spawn_chunk(world: ECSWorld, spec: ChunkSpec) -> int:
    voxel_pool = world.resources.get(VoxelPool)
    chunk_map = world.resources.get(ChunkMap)

    voxel_handle = voxel_pool.alloc(
        size=spec.size,
        fill=spec.fill_value,
    )

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
        Velocity(
            linear=spec.linvel,
            angular=spec.angvel,
        ),
    )
    world.add_component(
        eid,
        Acceleration(
            linear=(0.0, 0.0, 0.0),
            angular=(0.0, 0.0, 0.0),
        ),
    )
    world.add_component(
        eid,
        Chunk(
            coord=spec.coord,
            size=spec.size,
            voxel_handle=voxel_handle,
        ),
    )
    world.add_component(
        eid,
        Mesh(mesh_id=spec.mesh_id),
    )
    world.add_component(
        eid,
        ModelMatrix.identity(),
    )
    world.add_component(
        eid,
        Mass(mass=spec.mass),
    )

    if spec.gravity_strength != 0.0:
        world.add_component(
            eid,
            GravityWell(mu=spec.gravity_strength),
        )

    chunk_map.bind(spec.coord, eid)

    world.add_tag(eid, DirtyMatrices)

    if spec.mark_dirty_remesh:
        world.add_tag(eid, DirtyRemesh)

    if spec.mark_dirty_remodel:
        world.add_tag(eid, DirtyRemodel)

    return eid