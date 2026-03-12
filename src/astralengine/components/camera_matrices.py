from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

Mat4 = npt.NDArray[np.float32]

def _identity() -> Mat4:
    return np.identity(4, dtype=np.float32)


@dataclass(slots=True)
class CameraMatrices:
    view: Mat4 = field(default_factory=_identity)   
    proj: Mat4 = field(default_factory=_identity)   

    @classmethod
    def identity(cls) -> 'CameraMatrices':
        return cls()