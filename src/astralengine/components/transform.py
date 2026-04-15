from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Transform:
    x: float = 0.0
    y: float = 0.0