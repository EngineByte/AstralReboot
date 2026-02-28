from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.velocity import Velocity


class VelocityStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.vx: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.vy: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.vz: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.vx.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)

        self.vx = np.resize(self.vx, new_dense_capacity).astype(np.float32, copy=False)
        self.vy = np.resize(self.vy, new_dense_capacity).astype(np.float32, copy=False)
        self.vz = np.resize(self.vz, new_dense_capacity).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, Velocity):
            raise TypeError(f"VelocityStore expected Velocity, got {type(component)}")

        v = component.linear
        if v.shape != (3,):
            raise ValueError("Velocity.linear must be shape (3,) float32 array")

        self.vx[dense_i] = np.float32(v[0])
        self.vy[dense_i] = np.float32(v[1])
        self.vz[dense_i] = np.float32(v[2])

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.vx[dst_i] = self.vx[src_i]
        self.vy[dst_i] = self.vy[src_i]
        self.vz[dst_i] = self.vz[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.vx[dense_i] = 0.0
        self.vy[dense_i] = 0.0
        self.vz[dense_i] = 0.0