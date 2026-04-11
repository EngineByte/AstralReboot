from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PlayerController:
    move_speed: float = 8.0
    look_sensitivity: float = 0.15