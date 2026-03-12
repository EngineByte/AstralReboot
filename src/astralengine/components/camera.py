from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Camera:
    fov: float
    near: float
    far: float