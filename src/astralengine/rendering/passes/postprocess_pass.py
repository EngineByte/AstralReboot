from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.core.world import ECSWorld
from astralengine.resources.render_settings import RenderSettings
from astralengine.rendering.pipeline.render_context import RenderContext
from astralengine.rendering.pipeline.render_queue import RenderQueue


@dataclass(slots=True)
class PostProcessPass:
    order: int = 110
    name: str = "postprocess_pass"

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        settings = world.resources.get(RenderSettings)
        if not settings.draw_postprocess:
            return

        _ = ctx
        _ = queue