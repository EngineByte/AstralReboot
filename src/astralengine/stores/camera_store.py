from __future__ import annotations

import numpy as np

from astralengine.components.camera import Camera
from astralengine.ecs.storage.soa_store import SoAStore


class CameraStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 128) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.fov = np.full(cap, 75.0, dtype=np.float32)
        self.near = np.full(cap, 0.1, dtype=np.float32)
        self.far = np.full(cap, 10_000.0, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        self.fov = np.resize(self.fov_deg, new_cap).astype(np.float32, copy=False)
        self.near = np.resize(self.near, new_cap).astype(np.float32, copy=False)
        self.far = np.resize(self.far, new_cap).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Camera) -> None:
        self.fov[dense_i] = component.fov
        self.near[dense_i] = component.near
        self.far[dense_i] = component.far

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.fov[dst_i] = self.fov[src_i]
        self.near[dst_i] = self.near[src_i]
        self.far[dst_i] = self.far[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.fov[dense_i] = 75.0
        self.near[dense_i] = 0.1
        self.far[dense_i] = 10_000.0