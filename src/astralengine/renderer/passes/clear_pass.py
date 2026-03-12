from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.world import ECSWorld
from astralengine.resources.render_settings import RenderSettings
from astralengine.renderer.backend.gl_device import GLDevice
from astralengine.renderer.pipeline.render_context import RenderContext
from astralengine.renderer.pipeline.render_queue import RenderQueue


@dataclass(slots=True)
class ClearPass:
    order: int = 0
    name: str = "clear_pass"

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        settings = world.resources.get(RenderSettings)
        device = GLDevice()

        device.set_viewport(ctx.viewport_width, ctx.viewport_height)
        device.set_depth_test(settings.depth_test)
        device.set_cull_faces(settings.cull_faces)
        device.set_blend(settings.blend)
        device.set_wireframe(settings.wireframe)
        device.clear(settings.clear_color)