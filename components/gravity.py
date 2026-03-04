from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class GravityWell:
    mu: float = 1.0
    cx: float = 0.0
    cy: float = 0.0
    cz: float = 0.0