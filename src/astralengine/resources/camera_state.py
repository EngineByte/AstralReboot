from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt


Vec3 = npt.NDArray[np.float32]


@dataclass(slots=True)
class CameraState:
    '''
    Render-facing extracted camera state for the current frame.
    '''
    entity: int | None = None
    is_valid: bool = False

    position: Vec3 = field(
        default_factory=lambda: np.zeros(3, dtype=np.float32)
    )
    rotation: Vec3 = field(
        default_factory=lambda: np.zeros(3, dtype=np.float32)
    )

    fov_y_degrees: float = 75.0
    near_clip: float = 0.1
    far_clip: float = 1000.0

    projection_mode: str = 'perspective'
    aspect_ratio_override: float | None = None