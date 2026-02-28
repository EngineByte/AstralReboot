from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.camera import Camera


class CameraStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 256) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.fov: npt.NDArray[np.float32] = np.full(cap, 75.0, dtype=np.float32)
        self.aspect: npt.NDArray[np.float32] = np.full(cap, 16.0 / 9.0, dtype=np.float32)
        self.near: npt.NDArray[np.float32] = np.full(cap, 0.1, dtype=np.float32)
        self.far: npt.NDArray[np.float32] = np.full(cap, 1000.0, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.fov.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)

        self.fov = np.resize(self.fov, new_dense_capacity).astype(np.float32, copy=False)
        self.aspect = np.resize(self.aspect, new_dense_capacity).astype(np.float32, copy=False)
        self.near = np.resize(self.near, new_dense_capacity).astype(np.float32, copy=False)
        self.far = np.resize(self.far, new_dense_capacity).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, Camera):
            raise TypeError(f"CameraStore expected Camera, got {type(component)}")

        self.fov[dense_i] = np.float32(component.fov)
        self.aspect[dense_i] = np.float32(component.aspect)
        self.near[dense_i] = np.float32(component.near)
        self.far[dense_i] = np.float32(component.far)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.fov[dst_i] = self.fov[src_i]
        self.aspect[dst_i] = self.aspect[src_i]
        self.near[dst_i] = self.near[src_i]
        self.far[dst_i] = self.far[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.fov[dense_i] = 75.0
        self.aspect[dense_i] = np.float32(1280.0 / 720.0)
        self.near[dense_i] = 0.1
        self.far[dense_i] = 5000.0