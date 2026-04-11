from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GravityConfig:
    G: float = 0.9
    softening: float = 0.01
    max_force_distance: float | None = None
    max_accel: float | None = None
    enabled: bool = True
