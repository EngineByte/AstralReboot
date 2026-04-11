from __future__ import annotations

import numpy as np

from astralengine.old_code.components.parent_follow import ParentFollow
from astralengine.ecs.storage.soa_store import SoAStore


class ParentFollowStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 128) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.parent_eid = np.full(cap, -1, dtype=np.int64)

        self.off_x = np.zeros(cap, dtype=np.float32)
        self.off_y = np.zeros(cap, dtype=np.float32)
        self.off_z = np.zeros(cap, dtype=np.float32)

        self.follow_position = np.ones(cap, dtype=np.bool_)
        self.follow_rotation = np.ones(cap, dtype=np.bool_)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        self.parent_eid = np.resize(self.parent_eid, new_cap).astype(np.int64, copy=False)

        self.off_x = np.resize(self.off_x, new_cap).astype(np.float32, copy=False)
        self.off_y = np.resize(self.off_y, new_cap).astype(np.float32, copy=False)
        self.off_z = np.resize(self.off_z, new_cap).astype(np.float32, copy=False)

        self.follow_position = np.resize(self.follow_position, new_cap).astype(np.bool_, copy=False)
        self.follow_rotation = np.resize(self.follow_rotation, new_cap).astype(np.bool_, copy=False)

    def _on_add_dense(self, dense_i: int, component: ParentFollow) -> None:
        self.parent_eid[dense_i] = component.parent_eid

        self.off_x[dense_i] = component.offset[0]
        self.off_y[dense_i] = component.offset[1]
        self.off_z[dense_i] = component.offset[2]

        self.follow_position[dense_i] = component.follow_position
        self.follow_rotation[dense_i] = component.follow_rotation

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.parent_eid[dst_i] = self.parent_eid[src_i]

        self.off_x[dst_i] = self.off_x[src_i]
        self.off_y[dst_i] = self.off_y[src_i]
        self.off_z[dst_i] = self.off_z[src_i]

        self.follow_position[dst_i] = self.follow_position[src_i]
        self.follow_rotation[dst_i] = self.follow_rotation[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.parent_eid[dense_i] = -1

        self.off_x[dense_i] = 0.0
        self.off_y[dense_i] = 0.0
        self.off_z[dense_i] = 0.0

        self.follow_position[dense_i] = True
        self.follow_rotation[dense_i] = True