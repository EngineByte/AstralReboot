from __future__ import annotations

from astralengine.assets.asset_manager import AssetManager
from astralengine.assets.loaders.cubemap_loader import CubemapLoader
from astralengine.ecs.core.world import ECSWorld
from astralengine.rendering.backend.gpu_mesh_cache import GpuMeshCache
from astralengine.rendering.backend.shader_library import ShaderLibrary
from astralengine.rendering.backend.skybox_geometry import SkyboxGeometry
from astralengine.rendering.backend.texture_library import TextureLibrary
from astralengine.rendering.passes.clear_pass import ClearPass
from astralengine.rendering.passes.debug_pass import DebugPass
from astralengine.rendering.passes.opaque_mesh_pass import OpaqueMeshPass
from astralengine.rendering.passes.overlay_pass import OverlayPass
from astralengine.rendering.passes.skybox_pass import SkyboxPass
from astralengine.rendering.pipeline.render_pipeline import RenderPipeline
from astralengine.rendering.renderer import Renderer
from astralengine.resources.render_settings import RenderSettings


def install_render_pipeline(world: ECSWorld) -> None:
    """
    Build renderer internals and register render passes.
    """
    renderer = world.resources.get(Renderer)
    settings = world.resources.get(RenderSettings)
    assets = world.resources.get(AssetManager)

    shader_library = ShaderLibrary(assets=assets)
    mesh_cache = GpuMeshCache()
    cubemap_loader = CubemapLoader()
    texture_library = TextureLibrary(
        assets=assets,
        cubemap_loader=cubemap_loader,
    )
    skybox_geometry = SkyboxGeometry()
    pipeline = RenderPipeline()

    install_core_shaders(shader_library)
    install_core_passes(
        pipeline=pipeline,
        shader_library=shader_library,
        mesh_cache=mesh_cache,
        texture_library=texture_library,
        skybox_geometry=skybox_geometry,
        settings=settings,
    )

    renderer.attach_shader_library(shader_library)
    renderer.attach_mesh_cache(mesh_cache)
    renderer.attach_pipeline(pipeline)

    world.resources.add(shader_library)
    world.resources.add(mesh_cache)
    world.resources.add(texture_library)


def install_core_shaders(shader_library: ShaderLibrary) -> None:
    shader_library.register_from_asset_ids(
        name="chunk_opaque",
        vertex_asset_id="shader.chunk_opaque.vert",
        fragment_asset_id="shader.chunk_opaque.frag",
    )

    shader_library.register_from_asset_ids(
        name="skybox",
        vertex_asset_id="shader.skybox.vert",
        fragment_asset_id="shader.skybox.frag",
    )

    shader_library.register_from_asset_ids(
        name="debug_lines",
        vertex_asset_id="shader.debug.vert",
        fragment_asset_id="shader.debug.frag",
    )

    shader_library.register_from_asset_ids(
        name="overlay",
        vertex_asset_id="shader.overlay.vert",
        fragment_asset_id="shader.overlay.frag",
    )


def install_core_passes(
    *,
    pipeline: RenderPipeline,
    shader_library: ShaderLibrary,
    mesh_cache: GpuMeshCache,
    texture_library: TextureLibrary,
    skybox_geometry: SkyboxGeometry,
    settings: RenderSettings,
) -> None:
    pipeline.register_pass(ClearPass(order=0))
    pipeline.register_pass(
        SkyboxPass(
            order=10,
            shader_library=shader_library,
            geometry=skybox_geometry,
            texture_library=texture_library,
        )
    )
    pipeline.register_pass(
        OpaqueMeshPass(
            order=20,
            shader_library=shader_library,
            mesh_cache=mesh_cache,
        )
    )
    pipeline.register_pass(
        DebugPass(
            order=90,
            shader_library=shader_library,
        )
    )
    pipeline.register_pass(
        OverlayPass(
            order=100,
            shader_library=shader_library,
        )
    )

    _ = settings