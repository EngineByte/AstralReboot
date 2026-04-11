from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from astralengine.ecs.core.world import ECSWorld
from astralengine.old_code.rendering.pipeline.render_context import RenderContext
from astralengine.old_code.rendering.pipeline.render_queue import RenderQueue


class RenderPass(Protocol):
    order: int
    name: str

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        ...