from __future__ import annotations

from typing import Any
import numpy as np
import numpy.typing as npt

from astralengine.ecs.storage.soa_store import SoAStore
from astralengine.components.frame_child import FrameChild
from astralengine.components.frame_anchor import ROOT_FRAME_EID


class FrameChildStore(SoAStore):
    frame_eid: npt.NDArray[np.int32]
    
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 4096) -> None:
        self.frame_eid = np.full(initial_dense_capacity, ROOT_FRAME_EID, dtype=np.int32)
    
    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        self.frame_eid = np.resize(new_dense_capacity).astype(np.int32, copy=False)
    
    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, FrameChild):
            raise TypeError(f'FrameChildStore expected FrameChild, got {type(component)}')
        
        self.frame_eid[dense_i] = np.int32(component.frame_eid)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.frame_eid[dst_i] = self.frame_eid[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.frame_eid[dense_i] = -1