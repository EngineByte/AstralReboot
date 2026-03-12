from __future__ import annotations

from astralengine.ecs.world import ECSWorld

from astralengine.components.transform import Transform
from astralengine.components.velocity import Velocity
from astralengine.components.acceleration import Acceleration
from astralengine.components.mass import Mass
from astralengine.components.camera import Camera
from astralengine.components.camera_matrices import CameraMatrices
from astralengine.components.model_matrix import ModelMatrix
from astralengine.components.mesh import Mesh
from astralengine.components.chunk import Chunk
from astralengine.components.tags import DirtyMatrices, DirtyRemesh, DirtyRemodel, ActiveCamera
from astralengine.components.parent_follow import ParentFollow
from astralengine.components.player_controller import PlayerController
from astralengine.components.gravity import GravityWell

from astralengine.stores.camera_matrices_store import CameraMatricesStore
from astralengine.stores.model_matrix_store import ModelMatrixStore
from astralengine.stores.camera_store import CameraStore
from astralengine.stores.transform_store import TransformStore
from astralengine.stores.velocity_store import VelocityStore
from astralengine.stores.acceleration_store import AccelerationStore
from astralengine.stores.mass_store import MassStore
from astralengine.stores.mesh_store import MeshStore
from astralengine.stores.chunk_store import ChunkStore
from astralengine.stores.parent_follow_store import ParentFollowStore
from astralengine.stores.player_controller_store import PlayerControllerStore
from astralengine.stores.gravity_store import GravityWellStore


def create_ecs_world() -> ECSWorld:
    '''
    Create a new ECS world and setup core stores
    '''

    world = ECSWorld(
        entity_capacity=100_000,
        enable_command_buffer=True)
    
    install_component_stores(world)
    install_tag_stores(world)
    install_scheduler_phases(world)
    
    return world

def install_component_stores(world: ECSWorld) -> None:
    world.register_store(Transform, TransformStore(entity_capacity=100_000))
    world.register_store(Velocity, VelocityStore(entity_capacity=100_000))
    world.register_store(Acceleration, AccelerationStore(entity_capacity=100_000))
    world.register_store(Camera, CameraStore(entity_capacity=128))
    world.register_store(CameraMatrices, CameraMatricesStore(entity_capacity=128))
    world.register_store(PlayerController, PlayerControllerStore(entity_capacity=128))
    world.register_store(ParentFollow, ParentFollowStore(entity_capacity=128))
    world.register_store(Chunk, ChunkStore(entity_capacity=16_384))
    world.register_store(Mesh, MeshStore(entity_capacity=16_384))
    world.register_store(ModelMatrix, ModelMatrixStore(entity_capacity=100_000))
    world.register_store(Mass, MassStore(entity_capacity=100_000))
    world.register_store(GravityWell, GravityWellStore(entity_capacity=100_000))
    

def install_tag_stores(world: ECSWorld) -> None:
    world.register_tag_store(DirtyMatrices)
    world.register_tag_store(DirtyRemesh)
    world.register_tag_store(DirtyRemodel)
    world.register_tag_store(ActiveCamera)

def install_scheduler_phases(world: ECSWorld) -> None:
    '''
    Define scheduler phases for each frame.
    '''
    
    world.scheduler.add_phase('input')
    world.scheduler.add_phase('pre-update')
    world.scheduler.add_phase('update')
    world.scheduler.add_phase('post_update')
    world.scheduler.add_phase('render_submit')
    world.scheduler.add_phase('render')
    