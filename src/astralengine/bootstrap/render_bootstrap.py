from astralengine.ecs.world import ECSWorld
from astralengine.renderer.renderer import Renderer
from astralengine.renderer.backend.shader_library import ShaderLibrary
from astralengine.renderer.backend.gpu_mesh_cache import GpuMeshCache
from astralengine.renderer.passes.clear_pass import ClearPass
from astralengine.renderer.passes.skybox_pass import SkyboxPass
from astralengine.renderer.passes.clear_pass import OpaqueMeshPass
from astralengine.renderer.passes.opaque_mesh_pass import OverlayPass
from astralengine.renderer.passes.debug_pass import DebugPass
from astralengine.renderer.pipeline.render_pipeline import RenderPipeline
from astralengine.resources.render_settings import RenderSettings


def install_render_pipeline(world: ECSWorld) -> None:
    '''
    Setup renderer internal systems: shader library, mesh cache, passes and pipelines.
    '''
    
    renderer = world.resources.get(Renderer)
    settings = world.resources.get(RenderSettings)
    shader_library = ShaderLibrary()
    mesh_cache = GpuMeshCache()
    pipeline = RenderPipeline()
    
    install_core_shaders(shader_library)
    install_core_passes(
        pipeline=pipeline,
        shader_library=shader_library,
        mesh_cache=mesh_cache,
        settings=settings
    )
    
    renderer.attach_shader_library(shader_library)
    renderer.attach_mesh_cache(mesh_cache)
    renderer.attach_pipeline(pipeline)
    
def install_core_shaders(shader_library: ShaderLibrary) -> None:
    shader_library.register_from_asset_ids(
        name='chunk_opaque',
        vertex_asset_id='shader.chunk_opaque_vert',
        fragment_asset_id='shader.chunk_opaque_frag'
    )
    
    shader_library.register_from_asset_ids(
        name='skybox',
        vertex_asset_id='shader.skybox_vert',
        fragment_asset_id='shader.skybox_frag'
    )
    
    shader_library.register_from_asset_ids(
        name='debug_lines',
        vertex_asset_id='shader.debug_vert',
        fragment_asset_id='shader.debug_frag'
    )
    
    shader_library.register_from_asset_ids(
        name='overlay',
        vertex_asset_id='shader.overlay_vert',
        fragment_asset_id='shader.overlay_frag'
    )
    
def install_core_passes(
    pipeline: RenderPipeline,
    shader_library: ShaderLibrary,
    mesh_cache: GpuMeshCache,
    settings: RenderSettings
) -> None:
    
    pipeline.register_pass(ClearPass(order=0, clear_colour=settings.clear_colour))
    
    pipeline.register_pass(SkyboxPass(order=10, shader_library=shader_library))
    
    pipeline.register_pass(OpaqueMeshPass(order=20, shader_library=shader_library, mesh_cache=mesh_cache))
    
    pipeline.register_pass(DebugPass(order=90, shader_library=shader_library))
    
    pipeline.register_pass(OverlayPass(order=100, shader_library=shader_library))
    