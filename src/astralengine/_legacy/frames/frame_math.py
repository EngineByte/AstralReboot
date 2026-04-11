from __future__ import annotations

import numpy as np
import numpy.typing as npt


Float3 = npt.NDArray[np.float32]
Float4x4 = npt.NDArray[np.float32]


def frame_local_matrix(position: Float3, rotation: Float3) -> Float4x4: ...
def compose_frame_chain(frame_eid: int, world) -> Float4x4: ...
def world_to_frame(point_world: Float3, frame_eid: int, world) -> Float3: ...
def frame_to_world(point_local: Float3, frame_eid: int, world) -> Float3: ...