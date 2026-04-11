from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

Float3 = npt.NDArray[np.float32]


@dataclass(slots=True)
class Velocity:
    linear: Float3
    angular: Float3