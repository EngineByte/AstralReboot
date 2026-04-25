from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from numpy import typing as npt

Vec3 = npt.NDArray[np.float32]


def _vec3(x: float, y: float, z: float) -> Vec3:
    return np.array([x, y, z], dtype=np.float32)


@dataclass(slots=True)
class Velocity:
    linear: Vec3 = field(default_factory=lambda: _vec3(0.0, 0.0, 0.0))
    angular: Vec3 = field(default_factory=lambda: _vec3(0.0, 0.0, 0.0))

    dirty: bool = True


    def set_linaer(self, linx: float, liny: float, linz: float) -> None:
        self.linear[:] = (linx, liny, linz)
        self.dirty = True

    def set_angular(self, angx: float, angy: float, angz: float) -> None:
        self.angular[:] = (angx, angy, angz)
        self.dirty = True

    def accelerate_linear(self, dlinx: float, dliny: float, dlinz: float) -> None:
        self.linear += (dlinx, dliny, dlinz)
        self.dirty = True

    def accelerate_linear(self, dangx: float, dangy: float, dangz: float) -> None:
        self.angular += (dangx, dangy, dangz)
        self.dirty = True       