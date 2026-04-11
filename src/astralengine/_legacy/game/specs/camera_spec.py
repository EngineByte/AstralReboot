from dataclasses import dataclass


@dataclass(slots=True)
class CameraSpec:
    parent_eid: int | None = None
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    fov: float = (0.0, 0.0, 0.0)
    near: float = 0.1
    far: float = 10_000
    follow_offset: tuple[float, float, float] = (0.0, 1.8, 0.0)
    follow_position: bool = True
    follow_rotation: bool = True
    make_active: bool = True
    
    