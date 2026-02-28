from __future__ import annotations

from typing import Any, Dict, Iterable

import numpy as np
import numpy.typing as npt

from ecs.entity_allocator import EntityId, entity_index


class TagStore:
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        self.entity_capacity: int = int(entity_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self._dense_eids: npt.NDArray[np.uint64] = np.empty(cap, dtype=np.uint64)
        self._dense_size: int = 0

        self._sparse_to_dense: npt.NDArray[np.int32] = np.full(self.entity_capacity, -1, dtype=np.int32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = self._dense_eids.shape[0]
        if new_dense_capacity <= cur:
            return
        self._dense_eids = np.resize(self._dense_eids, new_dense_capacity).astype(np.uint64, copy=False)

    def has(self, eid: EntityId) -> bool:
        si = int(entity_index(eid))
        if si < 0 or si >= self.entity_capacity:
            return False
        return int(self._sparse_to_dense[si]) != -1

    def add(self, eid: EntityId) -> None:
        si = int(entity_index(eid))
        if si < 0 or si >= self.entity_capacity:
            raise ValueError(f"Entity index out of range for TagStore: {si}")

        if int(self._sparse_to_dense[si]) != -1:
            return

        dense_i = self._dense_size
        if dense_i >= self._dense_eids.shape[0]:
            new_cap = max(self._dense_eids.shape[0] * 2, dense_i + 1)
            self._ensure_dense_capacity(new_cap)

        self._dense_eids[dense_i] = np.uint64(eid)
        self._sparse_to_dense[si] = np.int32(dense_i)
        self._dense_size += 1

    def remove(self, eid: EntityId) -> None:
        si = int(entity_index(eid))
        if si < 0 or si >= self.entity_capacity:
            return

        dense_i = int(self._sparse_to_dense[si])
        if dense_i == -1:
            return

        last_i = self._dense_size - 1
        self._dense_size -= 1

        if dense_i != last_i:
            moved_eid = EntityId(self._dense_eids[last_i])
            self._dense_eids[dense_i] = np.uint64(moved_eid)
            moved_si = int(entity_index(moved_eid))
            self._sparse_to_dense[moved_si] = np.int32(dense_i)

        self._sparse_to_dense[si] = np.int32(-1)

    def dense_size(self) -> int:
        return self._dense_size

    def dense_eids(self) -> npt.NDArray[np.uint64]:
        return self._dense_eids[: self._dense_size]

    def clear(self) -> None:
        self._sparse_to_dense.fill(-1)
        self._dense_size = 0

    def stats(self) -> Dict[str, Any]:
        return {
            "dense_size": self._dense_size,
            "dense_capacity": int(self._dense_eids.shape[0]),
        }