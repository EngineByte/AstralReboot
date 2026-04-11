from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

I32x3 = npt.NDArray[np.int32]


@dataclass(slots=True)
class Chunk:
    frame_eid: int
    coord: I32x3
    size: int
    voxel_handle: int