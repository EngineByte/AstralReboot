# src/astralengine/components/gravity.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GravityWell:
    """
    Marks an entity as a gravitational source.

    mu:
        Gravitational parameter (G * mass).
        Using mu avoids repeatedly multiplying by G.

    softening:
        Prevents singularities when objects get extremely close.

    enabled:
        Allows temporary disabling without removing the component.
    """

    mu: float
    softening: float = 0.0
    enabled: bool = True