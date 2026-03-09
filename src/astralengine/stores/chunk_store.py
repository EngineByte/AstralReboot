from __future__ import annotations

from typing import Any
import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.chunk import Chunk


class ChunkStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 4096) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = max(1, int(initial_dense_capacity))

        self.cx: npt.NDArray[np.int32] = np.zeros(cap, dtype=np.int32)
        self.cy: npt.NDArray[np.int32] = np.zeros(cap, dtype=np.int32)
        self.cz: npt.NDArray[np.int32] = np.zeros(cap, dtype=np.int32)

        self.size: npt.NDArray[np.int32] = np.full(cap, 32, dtype=np.int32)

        self.voxel_handle: npt.NDArray[np.int32] = np.full(cap, -1, dtype=np.int32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.cx.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)

        self.cx = np.resize(self.cx, new_dense_capacity).astype(np.int32, copy=False)
        self.cy = np.resize(self.cy, new_dense_capacity).astype(np.int32, copy=False)
        self.cz = np.resize(self.cz, new_dense_capacity).astype(np.int32, copy=False)

        self.size = np.resize(self.size, new_dense_capacity).astype(np.int32, copy=False)
        self.voxel_handle = np.resize(self.voxel_handle, new_dense_capacity).astype(np.int32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, Chunk):
            raise TypeError(f'ChunkStore expected Chunk, got {type(component)}')

        c = component.coord
        if c.shape != (3,):
            raise ValueError('Chunk.coord must be shape (3,) int32 array')

        self.cx[dense_i] = np.int32(c[0])
        self.cy[dense_i] = np.int32(c[1])
        self.cz[dense_i] = np.int32(c[2])

        self.size[dense_i] = np.int32(component.size)
        self.voxel_handle[dense_i] = np.int32(component.voxel_handle)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.cx[dst_i] = self.cx[src_i]
        self.cy[dst_i] = self.cy[src_i]
        self.cz[dst_i] = self.cz[src_i]
        self.size[dst_i] = self.size[src_i]
        self.voxel_handle[dst_i] = self.voxel_handle[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.cx[dense_i] = 0
        self.cy[dense_i] = 0
        self.cz[dense_i] = 0
        self.size[dense_i] = 32
        self.voxel_handle[dense_i] = -1