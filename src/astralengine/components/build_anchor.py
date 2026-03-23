from dataclasses import dataclass
import numpy as np

from astralengine.math.types import Vec3, Quat


@dataclass(slots=True)
class BuildAnchor:
    frame_id: int
    position: Vec3
    rotation: Quat
    grid_size_m: float = 1.0
    
    @staticmethod
    def default(frame_id: int) -> 'BuildAnchor':
        return BuildAnchor(
            frame_id=frame_id,
            position=np.zeros(3, dtype=np.float64),
            rotation=np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float64),
            grid_size_m=1.0
        )