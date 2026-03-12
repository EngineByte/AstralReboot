# src/astralengine/stores/gravity_store.py

from __future__ import annotations

import numpy as np

from astralengine.components.gravity import GravityWell
from astralengine.ecs.soa_store import SoAStore


class GravityWellStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.mu = np.zeros(cap, dtype=np.float32)
        self.softening = np.zeros(cap, dtype=np.float32)
        self.enabled = np.ones(cap, dtype=np.bool_)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        self.mu = np.resize(self.mu, new_cap).astype(np.float32, copy=False)
        self.softening = np.resize(self.softening, new_cap).astype(np.float32, copy=False)
        self.enabled = np.resize(self.enabled, new_cap).astype(np.bool_, copy=False)

    def _on_add_dense(self, dense_i: int, component: GravityWell) -> None:
        self.mu[dense_i] = component.mu
        self.softening[dense_i] = component.softening
        self.enabled[dense_i] = component.enabled

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.mu[dst_i] = self.mu[src_i]
        self.softening[dst_i] = self.softening[src_i]
        self.enabled[dst_i] = self.enabled[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.mu[dense_i] = 0.0
        self.softening[dense_i] = 0.0
        self.enabled[dense_i] = False