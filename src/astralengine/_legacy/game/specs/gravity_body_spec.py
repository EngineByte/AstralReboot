from dataclasses import dataclass


@dataclass(slots=True)
class GravityBodySpec:
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    linvel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    angvel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    mass: float = 1.0
    gravity_strength: float = 1.0