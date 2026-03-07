from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GravityConfig:
    G: float = 0.1
    softening: float = 0.01
    max_accel: float | None = None
