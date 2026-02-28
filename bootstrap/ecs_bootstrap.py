from __future__ import annotations

from ecs.world import ECSWorld
from ecs.entity_allocator import EntityAllocator
from ecs.store_registry import StoreRegistry
from ecs.tag_store import TagStore
from ecs.scheduler import SystemScheduler
from ecs.command_buffer import CommandBuffer
from ecs.event_bus import EventBus
from ecs.resources import ResourceRegistry

from ecs.soa_store import SoAStore

from components.transform import Transform
from components.velocity import Velocity
from components.camera import Camera
from components.camera_matrices import CameraMatrices
from components.mesh import Mesh
from components.chunk import Chunk
from components.tags import DirtyMatrices, DirtyRemesh
from components.parent_follow import ParentFollow
from components.player_controller import PlayerController

from stores.camera_matrices_store import CameraMatricesStore
from stores.camera_store import CameraStore
from stores.transform_store import TransformStore
from stores.velocity_store import VelocityStore
from stores.mesh_store import MeshStore
from stores.chunk_store import ChunkStore
from stores.parent_follow_store import ParentFollowStore
from stores.player_controller_store import PlayerControllerStore


def create_ecs_world(entity_capacity: int = 100_000) -> ECSWorld:
    allocator = EntityAllocator(capacity=entity_capacity)
    stores = StoreRegistry()
    scheduler = SystemScheduler()
    command_buffer = CommandBuffer()
    events = EventBus()
    resources = ResourceRegistry()

    world = ECSWorld(
        allocator=allocator,
        stores=stores,
        scheduler=scheduler,
        command_buffer=command_buffer,
        event_bus=events,
        resources=resources,
    )

    stores.register(Transform, TransformStore(entity_capacity))
    stores.register(Velocity, VelocityStore(entity_capacity))
    stores.register(Camera, CameraStore(entity_capacity))
    stores.register(CameraMatrices, CameraMatricesStore(entity_capacity))
    stores.register(Mesh, MeshStore(entity_capacity))
    stores.register(Chunk, ChunkStore(entity_capacity))
    stores.register(ParentFollow, ParentFollowStore(entity_capacity))
    stores.register(PlayerController, PlayerControllerStore(entity_capacity))

    stores.register(DirtyMatrices, TagStore(entity_capacity))
    stores.register(DirtyRemesh, TagStore(entity_capacity))

    scheduler.add_phase("update")
    scheduler.add_phase("late_update")
    scheduler.add_phase("render")

    return world