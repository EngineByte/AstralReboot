from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.core.world import ECSWorld
from astralengine.resources.render_settings import RenderSettings
from astralengine.rendering.backend.shader_library import ShaderLibrary
from astralengine.rendering.pipeline.render_context import RenderContext
from astralengine.rendering.pipeline.render_queue import RenderQueue


@dataclass(slots=True)
class DebugPass:
    shader_library: ShaderLibrary
    order: int = 90
    name: str = "debug_pass"

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        settings = world.resources.get(RenderSettings)
        if not settings.draw_debug:
            return

        _ = self.shader_library
        _ = ctx
        _ = queue