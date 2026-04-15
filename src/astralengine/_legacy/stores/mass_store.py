from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from astralengine.ecs.storage.dense_store import DenseStore as SoAStore
from astralengine._legacy.components.mass import Mass


class MassStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.mass: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.mass.shape[0])
        if new_dense_capacity <= cur:
            return

        super()._ensure_dense_capacity(new_dense_capacity)

        self.mass = np.resize(self.mass, new_dense_capacity).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, Mass):
            raise TypeError(f'MassStore expected Mass, got {type(component)}')

        self.mass[dense_i] = np.float32(component.mass)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.mass[dst_i] = self.mass[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.mass[dense_i] = 0.0