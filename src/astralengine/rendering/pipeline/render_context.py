from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt


Mat4 = npt.NDArray[np.float32]
Vec3 = tuple[float, float, float]


def identity_mat4() -> Mat4:
    return np.eye(4, dtype=np.float32)


@dataclass(slots=True)
class RenderContext:
    """
    Per-frame render state extracted from the ECS world.
    """
    view: Mat4 = field(default_factory=identity_mat4)
    proj: Mat4 = field(default_factory=identity_mat4)
    camera_pos: Vec3 = (0.0, 0.0, 0.0)
    viewport_width: int = 1280
    viewport_height: int = 720

    def clear(self) -> None:
        self.view = identity_mat4()
        self.proj = identity_mat4()
        self.camera_pos = (0.0, 0.0, 0.0)