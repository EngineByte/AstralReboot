from __future__ import annotations

from typing import Any
import numpy as np
import numpy.typing as npt

from astralengine.ecs.storage.soa_store import SoAStore
from astralengine.old_code.components.frame_anchor import FrameAnchor


class FrameAnchorStore(SoAStore):
    local_position: npt.NDArray[np.float32]
    local_rotation: npt.NDArray[np.float32]
    local_linear_velocity: npt.NDArray[np.float32]
    local_angular_velocity: npt.NDArray[np.float32]
    parent_frame_eid: npt.NDArray[np.int32]
    
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 256) -> None: ...
        
    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None: ...
    def _on_add_dense(self, dense_i: int, component: Any) -> None: ...
    def _on_move_dense(self, dst_i: int, src_i: int) -> None: ...
    def _on_clear_dense(self, dense_i: int) -> None: ...