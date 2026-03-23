from dataclasses import dataclass
import numpy as np

from astralengine.math.types import Vec3, Quat


@dataclass(slots=True)
class LocalTransform:
    frame_id: int
    position: Vec3
    rotation: Quat
    
    @staticmethod
    def identity(frame_id: int) -> 'LocalTransform':
        return LocalTransform(
            frame_id=frame_id,
            position=np.zeros(3, dtype=np.float64),
            rotation=np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float64)
        )