from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.parent_follow import ParentFollow
from ecs.entity_allocator import EntityId


class ParentFollowStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 256) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.parent: npt.NDArray[EntityId] = np.zeros(cap, dtype=EntityId)
        self.ox: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.oy: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.oz: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.ox.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)

        self.parent = np.resize(self.parent, new_dense_capacity).astype(EntityId, copy=False)
        self.ox = np.resize(self.ox, new_dense_capacity).astype(np.float32, copy=False)
        self.oy = np.resize(self.oy, new_dense_capacity).astype(np.float32, copy=False)
        self.oz = np.resize(self.oz, new_dense_capacity).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, ParentFollow):
            raise TypeError(f"ParentFollowStore expected ParentFollow, got {type(component)}")

        o = component.offset
        if o.shape != (3,):
            raise ValueError("ParentFollow.offset must be shape (3,) float32 array")
        self.parent[dense_i] = component.parent
        self.ox[dense_i] = np.float32(o[0])
        self.oy[dense_i] = np.float32(o[1])
        self.oz[dense_i] = np.float32(o[2])

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.parent[dst_i] = self.parent[src_i]
        self.ox[dst_i] = self.ox[src_i]
        self.oy[dst_i] = self.oy[src_i]
        self.oz[dst_i] = self.oz[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.parent[dense_i] = EntityId(0)
        self.ox[dense_i] = 0.0
        self.oy[dense_i] = 0.0
        self.oz[dense_i] = 0.0