from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

Vec3 = npt.NDArray[np.float32]


def _default_sun_dir() -> Vec3:
    v = np.array([0.35, 0.72, 0.18], dtype=np.float32)
    n = np.linalg.norm(v)
    if n <= 0.0:
        return np.array([0.0, 1.0, 0.0], dtype=np.float32)
    return v / n


def _default_sun_color() -> Vec3:
    return np.array([1.0, 0.96, 0.86], dtype=np.float32)


@dataclass(slots=True)
class SkySettings:
    cubemap_faces: tuple[str, str, str, str, str, str]
    sun_dir: Vec3 = field(default_factory=_default_sun_dir)
    sun_color: Vec3 = field(default_factory=_default_sun_color)
    sun_angular_radius: np.float32 = np.float32(0.012)
    sun_glow_power: np.float32 = np.float32(512.0)
    exposure: np.float32 = np.float32(1.0)