from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.core.world import ECSWorld
from astralengine.old_code.resources.render_settings import RenderSettings
from astralengine.old_code.rendering.backend.gpu_mesh_cache import GpuMeshCache
from astralengine.old_code.rendering.backend.shader_library import ShaderLibrary
from astralengine.old_code.rendering.pipeline.render_context import RenderContext
from astralengine.old_code.rendering.pipeline.render_queue import RenderQueue


@dataclass(slots=True)
class OpaqueMeshPass:
    shader_library: ShaderLibrary
    mesh_cache: GpuMeshCache
    order: int = 20
    name: str = "opaque_mesh_pass"

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        settings = world.resources.get(RenderSettings)
        if not settings.draw_opaque:
            return

        program = self.shader_library.get("chunk_opaque")
        program.use()
        program.set_mat4("view", ctx.view)
        program.set_mat4("proj", ctx.proj)

        for cmd in queue.mesh_draws:
            if not self.mesh_cache.contains(cmd.mesh_id):
                continue

            program.set_mat4("model", cmd.model)
            self.mesh_cache.draw(cmd.mesh_id)