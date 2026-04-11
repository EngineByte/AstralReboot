from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt


Float3 = npt.NDArray[np.float32]


@dataclass(slots=True)
class Transform:
    position: Float3
    rotation: Float3
    scale: Float3