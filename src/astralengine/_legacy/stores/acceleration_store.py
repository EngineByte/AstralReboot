# src/astralengine/stores/acceleration_store.py

from __future__ import annotations

import numpy as np

from astralengine._legacy.components.acceleration import Acceleration
from astralengine.ecs.storage.dense_store import DenseStore as SoAStore


class AccelerationStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.ax = np.zeros(cap, dtype=np.float32)
        self.ay = np.zeros(cap, dtype=np.float32)
        self.az = np.zeros(cap, dtype=np.float32)

        self.pitch_deg_per_sec2 = np.zeros(cap, dtype=np.float32)
        self.yaw_deg_per_sec2 = np.zeros(cap, dtype=np.float32)
        self.roll_deg_per_sec2 = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        self.ax = np.resize(self.ax, new_cap).astype(np.float32, copy=False)
        self.ay = np.resize(self.ay, new_cap).astype(np.float32, copy=False)
        self.az = np.resize(self.az, new_cap).astype(np.float32, copy=False)

        self.pitch_deg_per_sec2 = np.resize(
            self.pitch_deg_per_sec2, new_cap
        ).astype(np.float32, copy=False)
        self.yaw_deg_per_sec2 = np.resize(
            self.yaw_deg_per_sec2, new_cap
        ).astype(np.float32, copy=False)
        self.roll_deg_per_sec2 = np.resize(
            self.roll_deg_per_sec2, new_cap
        ).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Acceleration) -> None:
        self.ax[dense_i] = component.linear[0]
        self.ay[dense_i] = component.linear[1]
        self.az[dense_i] = component.linear[2]

        self.pitch_deg_per_sec2[dense_i] = component.angular[0]
        self.yaw_deg_per_sec2[dense_i] = component.angular[1]
        self.roll_deg_per_sec2[dense_i] = component.angular[2]

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.ax[dst_i] = self.ax[src_i]
        self.ay[dst_i] = self.ay[src_i]
        self.az[dst_i] = self.az[src_i]

        self.pitch_deg_per_sec2[dst_i] = self.pitch_deg_per_sec2[src_i]
        self.yaw_deg_per_sec2[dst_i] = self.yaw_deg_per_sec2[src_i]
        self.roll_deg_per_sec2[dst_i] = self.roll_deg_per_sec2[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.ax[dense_i] = 0.0
        self.ay[dense_i] = 0.0
        self.az[dense_i] = 0.0

        self.pitch_deg_per_sec2[dense_i] = 0.0
        self.yaw_deg_per_sec2[dense_i] = 0.0
        self.roll_deg_per_sec2[dense_i] = 0.0