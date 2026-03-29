from __future__ import annotations

from dataclasses import dataclass, field

from astralengine.rendering.pipeline.draw_commands import (
    DebugLineCommand,
    MeshDrawCommand,
    SkyboxDrawCommand,
)


@dataclass(slots=True)
class RenderQueue:
    mesh_draws: list[MeshDrawCommand] = field(default_factory=list)
    skybox_draws: list[SkyboxDrawCommand] = field(default_factory=list)
    debug_line_draws: list[DebugLineCommand] = field(default_factory=list)

    def clear(self) -> None:
        self.mesh_draws.clear()
        self.skybox_draws.clear()
        self.debug_line_draws.clear()

    def submit_mesh(self, cmd: MeshDrawCommand) -> None:
        self.mesh_draws.append(cmd)

    def submit_skybox(self, cmd: SkyboxDrawCommand) -> None:
        self.skybox_draws.append(cmd)

    def submit_debug_lines(self, cmd: DebugLineCommand) -> None:
        self.debug_line_draws.append(cmd)