from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.transform import Transform


class TransformStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 1024) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.px: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.py: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.pz: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

        self.yaw: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.pitch: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)
        self.roll: npt.NDArray[np.float32] = np.zeros(cap, dtype=np.float32)

        self.sx: npt.NDArray[np.float32] = np.ones(cap, dtype=np.float32)
        self.sy: npt.NDArray[np.float32] = np.ones(cap, dtype=np.float32)
        self.sz: npt.NDArray[np.float32] = np.ones(cap, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.px.shape[0])
        if new_dense_capacity <= cur:
            return

        super()._ensure_dense_capacity(new_dense_capacity)

        self.px = np.resize(self.px, new_dense_capacity).astype(np.float32, copy=False)
        self.py = np.resize(self.py, new_dense_capacity).astype(np.float32, copy=False)
        self.pz = np.resize(self.pz, new_dense_capacity).astype(np.float32, copy=False)

        self.yaw = np.resize(self.yaw, new_dense_capacity).astype(np.float32, copy=False)
        self.pitch = np.resize(self.pitch, new_dense_capacity).astype(np.float32, copy=False)
        self.roll = np.resize(self.roll, new_dense_capacity).astype(np.float32, copy=False)

        self.sx = np.resize(self.sx, new_dense_capacity).astype(np.float32, copy=False)
        self.sy = np.resize(self.sy, new_dense_capacity).astype(np.float32, copy=False)
        self.sz = np.resize(self.sz, new_dense_capacity).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, Transform):
            raise TypeError(f"TransformStore expected Transform, got {type(component)}")

        p = component.position
        r = component.rotation
        s = component.scale

        if p.shape != (3,) or r.shape != (3,) or s.shape != (3,):
            raise ValueError("Transform.position/rotation_ypr/scale must be shape (3,) float32 arrays")

        self.px[dense_i] = np.float32(p[0])
        self.py[dense_i] = np.float32(p[1])
        self.pz[dense_i] = np.float32(p[2])

        self.yaw[dense_i] = np.float32(r[0])
        self.pitch[dense_i] = np.float32(r[1])
        self.roll[dense_i] = np.float32(r[2])

        self.sx[dense_i] = np.float32(s[0])
        self.sy[dense_i] = np.float32(s[1])
        self.sz[dense_i] = np.float32(s[2])

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.px[dst_i] = self.px[src_i]
        self.py[dst_i] = self.py[src_i]
        self.pz[dst_i] = self.pz[src_i]

        self.yaw[dst_i] = self.yaw[src_i]
        self.pitch[dst_i] = self.pitch[src_i]
        self.roll[dst_i] = self.roll[src_i]

        self.sx[dst_i] = self.sx[src_i]
        self.sy[dst_i] = self.sy[src_i]
        self.sz[dst_i] = self.sz[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.px[dense_i] = 0.0
        self.py[dense_i] = 0.0
        self.pz[dense_i] = 0.0

        self.yaw[dense_i] = 0.0
        self.pitch[dense_i] = 0.0
        self.roll[dense_i] = 0.0

        self.sx[dense_i] = 1.0
        self.sy[dense_i] = 1.0
        self.sz[dense_i] = 1.0

    def set_position(self, dense_i: int, x: float, y: float, z: float) -> None:
        self.px[dense_i] = np.float32(x)
        self.py[dense_i] = np.float32(y)
        self.pz[dense_i] = np.float32(z)

    def get_position(self, dense_i: int) -> tuple[float, float, float]:
        return (float(self.px[dense_i]), float(self.py[dense_i]), float(self.pz[dense_i]))