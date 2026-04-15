from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from pyglet import gl

from astralengine.ecs.core.world import ECSWorld
from astralengine._legacy.resources.render_settings import RenderSettings
from astralengine._legacy.rendering.backend.gl_device import GLDevice
from astralengine._legacy.rendering.backend.shader_library import ShaderLibrary
from astralengine._legacy.rendering.backend.skybox_geometry import SkyboxGeometry
from astralengine._legacy.rendering.backend.texture_library import TextureLibrary
from astralengine._legacy.rendering.pipeline.render_context import RenderContext
from astralengine._legacy.rendering.pipeline.render_queue import RenderQueue


@dataclass(slots=True)
class SkyboxPass:
    shader_library: ShaderLibrary
    geometry: SkyboxGeometry
    texture_library: TextureLibrary
    order: int = 10
    name: str = "skybox_pass"

    def execute(
        self,
        *,
        world: ECSWorld,
        ctx: RenderContext,
        queue: RenderQueue,
    ) -> None:
        settings = world.resources.get(RenderSettings)
        if not settings.draw_skybox or not queue.skybox_draws:
            return

        cmd = queue.skybox_draws[-1]
        program = self.shader_library.get("skybox")

        device = GLDevice()
        device.set_depth_mask(False)
        device.set_depth_func(gl.GL_LEQUAL)

        program.use()

        view_rot = np.array(ctx.view, dtype=np.float32, copy=True)
        view_rot[:3, 3] = 0.0

        program.set_mat4("uViewRot", view_rot)
        program.set_mat4("uProj", ctx.proj)
        program.set_float("uExposure", cmd.exposure)

        cubemap = self.texture_library.get_or_load_cubemap(cmd.cubemap_asset_id)
        cubemap.bind(0)
        program.set_int("uSkybox", 0)

        self.geometry.draw()

        device.set_depth_func(gl.GL_LESS)
        device.set_depth_mask(True)