from __future__ import annotations

import numpy as np

from astralengine._legacy.components.transform import Transform
from astralengine.ecs.storage.dense_store import DenseStore as SoAStore


class TransformStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.px = np.zeros(cap, dtype=np.float32)
        self.py = np.zeros(cap, dtype=np.float32)
        self.pz = np.zeros(cap, dtype=np.float32)

        self.pitch_deg = np.zeros(cap, dtype=np.float32)
        self.yaw_deg = np.zeros(cap, dtype=np.float32)
        self.roll_deg = np.zeros(cap, dtype=np.float32)

        self.sx = np.ones(cap, dtype=np.float32)
        self.sy = np.ones(cap, dtype=np.float32)
        self.sz = np.ones(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        self.px = np.resize(self.px, new_cap).astype(np.float32, copy=False)
        self.py = np.resize(self.py, new_cap).astype(np.float32, copy=False)
        self.pz = np.resize(self.pz, new_cap).astype(np.float32, copy=False)

        self.pitch_deg = np.resize(self.pitch_deg, new_cap).astype(np.float32, copy=False)
        self.yaw_deg = np.resize(self.yaw_deg, new_cap).astype(np.float32, copy=False)
        self.roll_deg = np.resize(self.roll_deg, new_cap).astype(np.float32, copy=False)

        old_sx = self.sx
        old_sy = self.sy
        old_sz = self.sz

        self.sx = np.ones(new_cap, dtype=np.float32)
        self.sy = np.ones(new_cap, dtype=np.float32)
        self.sz = np.ones(new_cap, dtype=np.float32)

        self.sx[:old_cap] = old_sx[:old_cap]
        self.sy[:old_cap] = old_sy[:old_cap]
        self.sz[:old_cap] = old_sz[:old_cap]

    def _on_add_dense(self, dense_i: int, component: Transform) -> None:
        self.px[dense_i] = component.position[0]
        self.py[dense_i] = component.position[1]
        self.pz[dense_i] = component.position[2]

        self.pitch_deg[dense_i] = component.rotation[0]
        self.yaw_deg[dense_i] = component.rotation[1]
        self.roll_deg[dense_i] = component.rotation[2]

        self.sx[dense_i] = component.scale[0]
        self.sy[dense_i] = component.scale[1]
        self.sz[dense_i] = component.scale[2]

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.px[dst_i] = self.px[src_i]
        self.py[dst_i] = self.py[src_i]
        self.pz[dst_i] = self.pz[src_i]

        self.pitch_deg[dst_i] = self.pitch_deg[src_i]
        self.yaw_deg[dst_i] = self.yaw_deg[src_i]
        self.roll_deg[dst_i] = self.roll_deg[src_i]

        self.sx[dst_i] = self.sx[src_i]
        self.sy[dst_i] = self.sy[src_i]
        self.sz[dst_i] = self.sz[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.px[dense_i] = 0.0
        self.py[dense_i] = 0.0
        self.pz[dense_i] = 0.0

        self.pitch_deg[dense_i] = 0.0
        self.yaw_deg[dense_i] = 0.0
        self.roll_deg[dense_i] = 0.0

        self.sx[dense_i] = 1.0
        self.sy[dense_i] = 1.0
        self.sz[dense_i] = 1.0