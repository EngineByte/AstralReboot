from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Camera:
    '''
    ECS camera component.
    '''
    active: bool = True
    fov_y_degrees: float = 75.0
    near_clip: float = 0.1
    far_clip: float = 1000.0
    projection_mode: str = 'perspective'
    aspect_ratio_override: float | None = None