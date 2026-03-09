from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Acceleration:
    ax: float = 0.0
    ay: float = 0.0
    az: float = 0.0