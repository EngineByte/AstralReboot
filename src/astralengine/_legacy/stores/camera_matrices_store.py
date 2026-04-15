from __future__ import annotations

import numpy as np

from astralengine._legacy.components.camera_matrices import CameraMatrices
from astralengine.ecs.storage.dense_store import DenseStore as SoAStore


class CameraMatricesStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 128) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.view = np.repeat(np.eye(4, dtype=np.float32)[None, :, :], cap, axis=0)
        self.proj = np.repeat(np.eye(4, dtype=np.float32)[None, :, :], cap, axis=0)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        old_view = self.view
        old_proj = self.proj

        self.view = np.repeat(np.eye(4, dtype=np.float32)[None, :, :], new_cap, axis=0)
        self.proj = np.repeat(np.eye(4, dtype=np.float32)[None, :, :], new_cap, axis=0)

        self.view[:old_cap] = old_view[:old_cap]
        self.proj[:old_cap] = old_proj[:old_cap]

    def _on_add_dense(self, dense_i: int, component: CameraMatrices) -> None:
        self.view[dense_i] = component.view
        self.proj[dense_i] = component.proj

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.view[dst_i] = self.view[src_i]
        self.proj[dst_i] = self.proj[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.view[dense_i] = np.eye(4, dtype=np.float32)
        self.proj[dense_i] = np.eye(4, dtype=np.float32)