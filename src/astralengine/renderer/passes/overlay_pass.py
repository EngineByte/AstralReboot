from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.world import ECSWorld
from astralengine.resources.render_settings import RenderSettings
from astralengine.renderer.backend.shader_library import ShaderLibrary
from astralengine.renderer.pipeline.render_context import RenderContext
from astralengine.renderer.pipeline.render_queue import RenderQueue


@dataclass(slots=True)
class OverlayPass:
    shader_library: ShaderLibrary
    order: int = 100
    name: str = "overlay_pass"

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        settings = world.resources.get(RenderSettings)
        if not settings.draw_overlays:
            return

        _ = self.shader_library
        _ = ctx
        _ = queue