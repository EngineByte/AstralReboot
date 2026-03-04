from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.gravity import GravityWell


class GravityWellStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.mu: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

        self.cx: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.cy: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.cz: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.mu.shape[0])
        if new_dense_capacity <= cur:
            return

        super()._ensure_dense_capacity(new_dense_capacity)

        self.mu = np.resize(self.mu, new_dense_capacity).astype(np.float32, copy=False)
        self.cx = np.resize(self.cx, new_dense_capacity).astype(np.float32, copy=False)
        self.cy = np.resize(self.cy, new_dense_capacity).astype(np.float32, copy=False)
        self.cz = np.resize(self.cz, new_dense_capacity).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, GravityWell):
            raise TypeError(f'GravityWellStore expected GravityWell, got {type(component)}')

        self.mu[dense_i] = np.float32(component.mu)
        self.cx[dense_i] = np.float32(component.cx)
        self.cy[dense_i] = np.float32(component.cy)
        self.cz[dense_i] = np.float32(component.cz)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.mu[dst_i] = self.mu[src_i]
        self.cx[dst_i] = self.cx[src_i]
        self.cy[dst_i] = self.cy[src_i]
        self.cz[dst_i] = self.cz[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.mu[dense_i] = 0.0
        self.cx[dense_i] = 0.0
        self.cy[dense_i] = 0.0
        self.cz[dense_i] = 0.0