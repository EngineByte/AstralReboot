from __future__ import annotations

import numpy as np

from astralengine._legacy.components.model_matrix import ModelMatrix
from astralengine.ecs.storage.dense_store import DenseStore as SoAStore


class ModelMatrixStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.model = np.repeat(np.eye(4, dtype=np.float32)[None, :, :], cap, axis=0)

        self.cx = np.zeros(cap, dtype=np.float32)
        self.cy = np.zeros(cap, dtype=np.float32)
        self.cz = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        old_model = self.model
        self.model = np.repeat(np.eye(4, dtype=np.float32)[None, :, :], new_cap, axis=0)
        self.model[:old_cap] = old_model[:old_cap]

        self.cx = np.resize(self.cx, new_cap).astype(np.float32, copy=False)
        self.cy = np.resize(self.cy, new_cap).astype(np.float32, copy=False)
        self.cz = np.resize(self.cz, new_cap).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: ModelMatrix) -> None:
        self.model[dense_i] = component.model
        self.cx[dense_i] = component.centre[0]
        self.cy[dense_i] = component.centre[1]
        self.cz[dense_i] = component.centre[2]

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.model[dst_i] = self.model[src_i]
        self.cx[dst_i] = self.cx[src_i]
        self.cy[dst_i] = self.cy[src_i]
        self.cz[dst_i] = self.cz[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.model[dense_i] = np.eye(4, dtype=np.float32)
        self.cx[dense_i] = 0.0
        self.cy[dense_i] = 0.0
        self.cz[dense_i] = 0.0