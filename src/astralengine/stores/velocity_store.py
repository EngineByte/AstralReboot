from __future__ import annotations

import numpy as np

from astralengine.components.velocity import Velocity
from astralengine.ecs.soa_store import SoAStore


class VelocityStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.vx = np.zeros(cap, dtype=np.float32)
        self.vy = np.zeros(cap, dtype=np.float32)
        self.vz = np.zeros(cap, dtype=np.float32)

        self.pitch_deg_per_sec = np.zeros(cap, dtype=np.float32)
        self.yaw_deg_per_sec = np.zeros(cap, dtype=np.float32)
        self.roll_deg_per_sec = np.zeros(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        self.vx = np.resize(self.vx, new_cap).astype(np.float32, copy=False)
        self.vy = np.resize(self.vy, new_cap).astype(np.float32, copy=False)
        self.vz = np.resize(self.vz, new_cap).astype(np.float32, copy=False)

        self.pitch_deg_per_sec = np.resize(self.pitch_deg_per_sec, new_cap).astype(np.float32, copy=False)
        self.yaw_deg_per_sec = np.resize(self.yaw_deg_per_sec, new_cap).astype(np.float32, copy=False)
        self.roll_deg_per_sec = np.resize(self.roll_deg_per_sec, new_cap).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Velocity) -> None:
        self.vx[dense_i] = component.linear[0]
        self.vy[dense_i] = component.linear[1]
        self.vz[dense_i] = component.linear[2]

        self.pitch_deg_per_sec[dense_i] = component.angular[0]
        self.yaw_deg_per_sec[dense_i] = component.angular[1]
        self.roll_deg_per_sec[dense_i] = component.angular[2]

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.vx[dst_i] = self.vx[src_i]
        self.vy[dst_i] = self.vy[src_i]
        self.vz[dst_i] = self.vz[src_i]

        self.pitch_deg_per_sec[dst_i] = self.pitch_deg_per_sec[src_i]
        self.yaw_deg_per_sec[dst_i] = self.yaw_deg_per_sec[src_i]
        self.roll_deg_per_sec[dst_i] = self.roll_deg_per_sec[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.vx[dense_i] = 0.0
        self.vy[dense_i] = 0.0
        self.vz[dense_i] = 0.0

        self.pitch_deg_per_sec[dense_i] = 0.0
        self.yaw_deg_per_sec[dense_i] = 0.0
        self.roll_deg_per_sec[dense_i] = 0.0