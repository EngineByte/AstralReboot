from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

Mat4 = npt.NDArray[np.float32]


@dataclass(slots=True)
class CameraMatrices:
    view: Mat4    
    projection: Mat4  