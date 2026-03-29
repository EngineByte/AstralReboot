from astralengine.ecs.core.world import ECSWorld
from astralengine.app.paths import build_paths
from astralengine.assets.asset_manager import AssetManager
from astralengine.resources.gravity_config import GravityConfig
from astralengine.resources.input_state import InputState
from astralengine.resources.render_settings import RenderSettings

from astralengine.resources.sky_settings import SkySettings
from astralengine.voxels.chunk_map import ChunkMap
from astralengine.voxels.mesh_pool import MeshPool
from astralengine.voxels.voxel_pool import VoxelPool
from astralengine.rendering.renderer import Renderer
from astralengine.resources.gravity_config import GravityConfig
from astralengine.resources.sky_settings import SkySettings

from astralengine.frames.frame_graph import FrameGraph
from astralengine.resources.frame_settings import FrameSettings
from astralengine.resources.streaming_settings import StreamingSettings
from astralengine.resources.small_world_settings import SmallWorldSettings
from astralengine.streaming.chunk_stream_index import ChunkStreamIndex
from astralengine.streaming.chunk_requests import ChunkRequestQueue

def install_core_resources(world: ECSWorld) -> None:
    '''
    Install core global resources needed by astral engine.
    '''
    paths = build_paths()
    
    world.resources.add(paths)
    world.resources.add(AssetManager(paths=paths))
    world.resources.add(InputState())
    world.resources.add(RenderSettings())
    world.resources.add(default_gravity_config())
    world.resources.add(default_sky_settings())
    world.resources.add(ChunkMap())
    world.resources.add(VoxelPool())
    world.resources.add(MeshPool())
    world.resources.add(Renderer())
    world.resources.add(default_frame_settings())
    world.resources.add(default_streaming_settings())
    world.resources.add(default_small_world_settings())

def default_frame_settings() -> FrameSettings:
    return FrameSettings()

def default_streaming_settings() -> StreamingSettings:
    return StreamingSettings()

def default_small_world_settings() -> SmallWorldSettings:
    return SmallWorldSettings()
    
def default_gravity_config() -> GravityConfig:
    return GravityConfig(
        G=1.0,
        softening=0.01,
        max_force_distance=1.0e9,
        enabled=True
    )
    
def default_sky_settings() -> SkySettings:
    return SkySettings(
        enabled=True,
        asset_id='skybox.milkyway',
        sun_dir=(0.4, 0.8, 0.2),
        exposure=1.0
    )