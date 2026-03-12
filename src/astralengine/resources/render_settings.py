from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RenderSettings:
    """
    Global renderer configuration.

    These are engine/runtime settings rather than scene-authored renderables.
    """

    clear_color: tuple[float, float, float, float] = (0.02, 0.02, 0.04, 1.0)

    vsync: bool = True
    wireframe: bool = False
    cull_faces: bool = True
    depth_test: bool = True
    blend: bool = False

    draw_skybox: bool = True
    draw_opaque: bool = True
    draw_debug: bool = True
    draw_overlays: bool = True
    draw_postprocess: bool = False

    show_velocity_vectors: bool = False
    show_chunk_bounds: bool = False
    show_axes: bool = False
    show_wireframe_overlay: bool = False

    viewport_width: int = 1280
    viewport_height: int = 720

    def aspect_ratio(self) -> float:
        """
        Return the current viewport aspect ratio.
        """
        if self.viewport_height <= 0:
            return 1.0
        return self.viewport_width / self.viewport_height

    def set_viewport(self, width: int, height: int) -> None:
        """
        Update tracked viewport dimensions.
        """
        self.viewport_width = max(1, int(width))
        self.viewport_height = max(1, int(height))