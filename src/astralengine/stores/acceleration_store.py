from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.acceleration import Acceleration


class AccelerationStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.ax: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.ay: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.az: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.ax.shape[0])
        if new_dense_capacity <= cur:
            return

        super()._ensure_dense_capacity(new_dense_capacity)

        self.ax = np.resize(self.ax, new_dense_capacity).astype(np.float32, copy=False)
        self.ay = np.resize(self.ay, new_dense_capacity).astype(np.float32, copy=False)
        self.az = np.resize(self.az, new_dense_capacity).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, Acceleration):
            raise TypeError(f'AccelerationStore expected Acceleration, got {type(component)}')

        self.ax[dense_i] = np.float32(component.ax)
        self.ay[dense_i] = np.float32(component.ay)
        self.az[dense_i] = np.float32(component.az)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.ax[dst_i] = self.ax[src_i]
        self.ay[dst_i] = self.ay[src_i]
        self.az[dst_i] = self.az[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.ax[dense_i] = 0.0
        self.ay[dense_i] = 0.0
        self.az[dense_i] = 0.0