from dataclasses import dataclass

@dataclass(slots=True)
class PlayerController:
    move_speed: float = 6.0
    mouse_sens: float = 0.15
    invert_y: bool = False
    