from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Mass:
    mass: float = 1.0