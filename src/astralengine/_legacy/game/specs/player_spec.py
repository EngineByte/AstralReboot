from dataclasses import dataclass


@dataclass(slots=True)
class PlayerSpec:
    position: tuple[float, float, float] = (0.0, 0.0, -5.0)
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    linvel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    angvel: tuple[float, float, float] = (0.0, 0.0, 0.0)
    move_speed: float = 10.0
    look_sensitivity: float = 0.15
    
    