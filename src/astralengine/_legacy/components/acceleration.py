# src/astralengine/components/acceleration.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Acceleration:
    linear: tuple[float, float, float] = (0.0, 0.0, 0.0)
    angular: tuple[float, float, float] = (0.0, 0.0, 0.0)