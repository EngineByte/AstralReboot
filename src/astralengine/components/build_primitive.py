from dataclasses import dataclass
from enum import IntEnum
import numpy as np

from astralengine.math.types import Vec3, Quat


class BuildPrimitiveType(IntEnum):
    CUBE = 1
    
    
@dataclass(slots=True)
class BuildPrimitive:
    primitive_type: BuildPrimitiveType
    size_m: Vec3
    material_id: int
    local_position: Vec3
    local_rotation: Quat
    
    @staticmethod
    def one_meter_cube(material_id: int) -> 'BuildPrimitive':
        return BuildPrimitive(
            primitive_type=BuildPrimitiveType.CUBE,
            size_m=np.array([1.0, 1.0, 1.0], dtype=np.float64),
            material_id=material_id,
            local_position=np.zeros(3, dtype=np.float64),
            local_rotation=np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float64)
        )