from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt


Float3 = npt.NDArray[np.float32]

ROOT_FRAME_EID = -1


@dataclass(slots=True)
class FrameAnchor:
    local_position: Float3
    local_rotation: Float3
    local_linear_velocity: Float3
    local_angular_velocity: Float3
    parent_frame_eid: int = ROOT_FRAME_EID