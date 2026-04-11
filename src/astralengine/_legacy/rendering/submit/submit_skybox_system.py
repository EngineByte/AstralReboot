from __future__ import annotations

from astralengine.ecs.core.world import ECSWorld
from astralengine.old_code.rendering.pipeline.draw_commands import SkyboxDrawCommand
from astralengine.old_code.rendering.renderer import Renderer
from astralengine.old_code.resources.render_settings import RenderSettings
from astralengine.old_code.resources.sky_settings import SkySettings


def system_submit_skybox(world: ECSWorld, dt: float) -> None:
    _ = dt

    renderer = world.resources.get(Renderer)
    settings = world.resources.get(RenderSettings)
    sky = world.resources.get(SkySettings)

    if not settings.draw_skybox:
        return

    if not sky.enabled:
        return

    renderer.queue.submit_skybox(
        SkyboxDrawCommand(
            cubemap_asset_id=sky.asset_id,
            exposure=sky.exposure,
        )
    )