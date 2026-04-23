from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt


Vec3 = npt.NDArray[np.float32]
Mat4 = npt.NDArray[np.float32]


def _vec3(x: float, y: float, z: float) -> Vec3:
    return np.array([x, y, z], dtype=np.float32)


def _identity_mat4() -> Mat4:
    return np.identity(4, dtype=np.float32)


@dataclass(slots=True)
class Transform:
    '''
    ECS Transform component.

    Responsibilities:
    - store position / rotation / scale
    - optionally cache model matrix
    - remain lightweight and data-oriented

    Notes:
    - rotation is stored as Euler angles (radians)
    - model_matrix is optional and lazily updated
    '''

    position: Vec3 = field(default_factory=lambda: _vec3(0.0, 0.0, 0.0))
    rotation: Vec3 = field(default_factory=lambda: _vec3(0.0, 0.0, 0.0))
    scale: Vec3 = field(default_factory=lambda: _vec3(1.0, 1.0, 1.0))

    # Cached model matrix
    model_matrix: Mat4 | None = None

    # Dirty flag (optional but very useful)
    dirty: bool = True

    # ------------------------------------------------------------------
    # Mutation helpers (recommended usage pattern)
    # ------------------------------------------------------------------

    def set_position(self, x: float, y: float, z: float) -> None:
        self.position[:] = (x, y, z)
        self.dirty = True

    def set_rotation(self, x: float, y: float, z: float) -> None:
        self.rotation[:] = (x, y, z)
        self.dirty = True

    def set_scale(self, x: float, y: float, z: float) -> None:
        self.scale[:] = (x, y, z)
        self.dirty = True

    def translate(self, dx: float, dy: float, dz: float) -> None:
        self.position += (dx, dy, dz)
        self.dirty = True

    def rotate(self, dx: float, dy: float, dz: float) -> None:
        self.rotation += (dx, dy, dz)
        self.dirty = True

    def uniform_scale(self, s: float) -> None:
        self.scale *= s
        self.dirty = True