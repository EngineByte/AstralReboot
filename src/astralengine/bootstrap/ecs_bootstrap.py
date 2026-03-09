from __future__ import annotations

from ecs.world import ECSWorld
from ecs.entity_allocator import EntityAllocator
from ecs.store_registry import StoreRegistry
from ecs.tag_store import TagStore
from ecs.scheduler import SystemScheduler
from ecs.command_buffer import CommandBuffer
from ecs.event_bus import EventBus
from ecs.resources import ResourceRegistry

from components.transform import Transform
from components.velocity import Velocity
from components.acceleration import Acceleration
from components.mass import Mass
from components.camera import Camera
from components.camera_matrices import CameraMatrices
from components.model_matrix import ModelMatrix
from components.mesh import Mesh
from components.chunk import Chunk
from components.tags import DirtyMatrices, DirtyRemesh, DirtyRemodel
from components.parent_follow import ParentFollow
from components.player_controller import PlayerController
from components.gravity import GravityWell

from stores.camera_matrices_store import CameraMatricesStore
from stores.model_matrix_store import ModelMatrixStore
from stores.camera_store import CameraStore
from stores.transform_store import TransformStore
from stores.velocity_store import VelocityStore
from stores.acceleration_store import AccelerationStore
from stores.mass_store import MassStore
from stores.mesh_store import MeshStore
from stores.chunk_store import ChunkStore
from stores.parent_follow_store import ParentFollowStore
from stores.player_controller_store import PlayerControllerStore
from stores.gravity_store import GravityWellStore


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
    