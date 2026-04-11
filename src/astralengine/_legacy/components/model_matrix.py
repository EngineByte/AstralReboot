from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

Mat4 = npt.NDArray[np.float32]

def _identity() -> Mat4:
    return np.identity(4, np.float32)

@dataclass(slots=True)
class ModelMatrix:
    model: Mat4 = field(default_factory=_identity)
    centre: tuple[float, float, float] = (0.0, 0.0, 0.0)


    @classmethod
    def identity(cls) -> 'ModelMatrix':
        return cls()