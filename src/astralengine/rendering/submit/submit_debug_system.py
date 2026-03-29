from __future__ import annotations

from astralengine.ecs.core.world import ECSWorld
from astralengine.rendering.renderer import Renderer
from astralengine.resources.render_settings import RenderSettings


def system_submit_debug(world: ECSWorld, dt: float) -> None:
    _ = dt

    renderer = world.resources.get(Renderer)
    settings = world.resources.get(RenderSettings)

    if not settings.draw_debug:
        return
    
    _ = renderer