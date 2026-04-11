from __future__ import annotations

from astralengine.ecs.core.world import ECSWorld
from astralengine.old_code.rendering.backend.gpu_mesh_cache import GpuMeshCache
from astralengine.old_code.rendering.backend.shader_library import ShaderLibrary
from astralengine.old_code.rendering.pipeline.render_context import RenderContext
from astralengine.old_code.rendering.pipeline.render_pipeline import RenderPipeline
from astralengine.old_code.rendering.pipeline.render_queue import RenderQueue


class Renderer:
    """
    High-level render facade.
    """

    def __init__(self) -> None:
        self.shader_library: ShaderLibrary | None = None
        self.mesh_cache: GpuMeshCache | None = None
        self.pipeline: RenderPipeline | None = None
        self.ctx = RenderContext()
        self.queue = RenderQueue()

    def attach_shader_library(self, shader_library: ShaderLibrary) -> None:
        self.shader_library = shader_library

    def attach_mesh_cache(self, mesh_cache: GpuMeshCache) -> None:
        self.mesh_cache = mesh_cache

    def attach_pipeline(self, pipeline: RenderPipeline) -> None:
        self.pipeline = pipeline

    def begin_frame(self) -> None:
        self.queue.clear()

    def render_frame(self, world: ECSWorld) -> None:
        if self.pipeline is None:
            raise RuntimeError("Renderer pipeline not attached.")
        self.pipeline.execute(world=world, ctx=self.ctx, queue=self.queue)


def system_execute_render_pipeline(world: ECSWorld, dt: float) -> None:
    _ = dt
    renderer = world.resources.get(Renderer)
    renderer.render_frame(world)