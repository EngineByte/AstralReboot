from __future__ import annotations

from astralengine.ecs.core.world import ECSWorld
from astralengine.rendering.pipeline.render_context import RenderContext
from astralengine.rendering.pipeline.render_queue import RenderQueue
from astralengine.rendering.pipeline.render_pass import RenderPass


class RenderPipeline:
    """
    Ordered list of render passes.
    """

    def __init__(self) -> None:
        self._passes: list[RenderPass] = []

    def register_pass(self, render_pass: RenderPass) -> None:
        self._passes.append(render_pass)
        self._passes.sort(key=lambda p: p.order)

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        for render_pass in self._passes:
            render_pass.execute(world=world, ctx=ctx, queue=queue)