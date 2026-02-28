from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

EntityId = np.uint64
Index = np.uint32
Generation = np.uint32

_INDEX_MASK: int = 0xFFFF_FFFF
_GEN_SHIFT: int = 32


def entity_index(eid: EntityId) -> Index:
    return Index(int(eid) & _INDEX_MASK)


def entity_generation(eid: EntityId) -> Generation:
    return Generation((int(eid) >> _GEN_SHIFT) & _INDEX_MASK)


def make_entity_id(index: Index, generation: Generation) -> EntityId:
    return EntityId((int(generation) << _GEN_SHIFT) | int(index))


class EntityAllocator:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")

        self._capacity: int = int(capacity)

        self._generations: npt.NDArray[np.uint32] = np.zeros(self._capacity, dtype=np.uint32)
        self._alive: npt.NDArray[np.bool_] = np.zeros(self._capacity, dtype=np.bool_)

        self._free: npt.NDArray[np.uint32] = np.arange(self._capacity - 1, -1, -1, dtype=np.uint32)
        self._free_top: int = self._capacity

        self._alive_count: int = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    def alive_count(self) -> int:
        return self._alive_count

    def create(self) -> EntityId:
        if self._free_top == 0:
            raise RuntimeError(
                f"EntityAllocator exhausted: capacity={self._capacity}. "
                f"Increase capacity or recycle entities."
            )

        self._free_top -= 1
        idx = Index(self._free[self._free_top])
        gen = Generation(self._generations[int(idx)])

        self._alive[int(idx)] = True
        self._alive_count += 1

        return make_entity_id(idx, gen)

    def destroy(self, eid: EntityId) -> None:
        idx_i = self._require_alive(eid)

        self._alive[idx_i] = False
        self._alive_count -= 1

        self._generations[idx_i] = np.uint32(self._generations[idx_i] + np.uint32(1))

        self._free[self._free_top] = np.uint32(idx_i)
        self._free_top += 1

    def is_alive(self, eid: EntityId) -> bool:
        idx = int(entity_index(eid))
        if idx < 0 or idx >= self._capacity:
            return False
        if not bool(self._alive[idx]):
            return False
        return int(entity_generation(eid)) == int(self._generations[idx])

    def _require_alive(self, eid: EntityId) -> int:
        idx = int(entity_index(eid))
        gen = int(entity_generation(eid))

        if idx < 0 or idx >= self._capacity:
            raise ValueError(f"Invalid entity index: {idx} (capacity={self._capacity})")

        if not bool(self._alive[idx]):
            raise ValueError(f"Entity is not alive: eid={int(eid)} idx={idx}")

        cur_gen = int(self._generations[idx])
        if gen != cur_gen:
            raise ValueError(
                f"Stale entity handle: eid={int(eid)} idx={idx} gen={gen} current_gen={cur_gen}"
            )

        return idx

    def grow(self, new_capacity: int) -> None:
        new_capacity = int(new_capacity)
        if new_capacity <= self._capacity:
            raise ValueError("new_capacity must be greater than current capacity")

        old_cap = self._capacity
        self._capacity = new_capacity

        self._generations = np.resize(self._generations, new_capacity).astype(np.uint32, copy=False)
        self._alive = np.resize(self._alive, new_capacity).astype(np.bool_, copy=False)

        self._generations[old_cap:new_capacity] = np.uint32(0)
        self._alive[old_cap:new_capacity] = False

        old_free = self._free[: self._free_top].copy()  # existing free stack content
        new_indices = np.arange(new_capacity - 1, old_cap - 1, -1, dtype=np.uint32)  # new slots
        self._free = np.empty(new_capacity, dtype=np.uint32)

        content = np.concatenate([old_free, new_indices])
        self._free[: content.size] = content
        self._free_top = int(content.size)

    def stats(self) -> dict:
        return {
            "capacity": self._capacity,
            "alive_count": self._alive_count,
            "free_count": self._free_top,
        }