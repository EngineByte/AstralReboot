from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

from astralengine.math.math_quat import quat_identity, quat_normalize, quat_to_euler_ypr_degrees


Vec3 = npt.NDArray[np.float32]
Mat4 = npt.NDArray[np.float32]
Quat = npt.NDArray[np.float32]


def _vec3(x: float, y: float, z: float) -> Vec3:
    return np.array([x, y, z], dtype=np.float32)


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
    orientation: Quat = field(default_factory=quat_identity)
    scale: Vec3 = field(default_factory=lambda: _vec3(1.0, 1.0, 1.0))

    # Cached model matrix
    model_matrix: Mat4 | None = None

    # Dirty flag (optional but very useful)
    dirty: bool = True

    def invalidate_cached_matrices(self) -> None:
        self.dirty = True
        self.model_matrix = None

    # ------------------------------------------------------------------
    # Mutation helpers (recommended usage pattern)
    # ------------------------------------------------------------------

    def set_position(self, x: float, y: float, z: float) -> None:
        self.position[:] = (x, y, z)
        self.dirty = True

    def set_orientation(self, q: Quat) -> None:
        self.orientation = quat_normalize(q)
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

    @property
    def rotation(self) -> tuple[float, float, float]:
        return quat_to_euler_ypr_degrees(self.orientation)
    
    @rotation.setter
    def rotation(self, _value) -> None:
        raise AttributeError(
            'Transform.rotation is now derived from quaternion orientation.'
            'Set Transform.orientation instead.'
        )