from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.camera_matrices import CameraMatrices


class CameraMatricesStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 256) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.view: npt.NDArray[np.float32] = np.repeat(
            np.identity(4, dtype=np.float32)[None, :, :], cap, axis=0
        )
        self.proj: npt.NDArray[np.float32] = np.repeat(
            np.identity(4, dtype=np.float32)[None, :, :], cap, axis=0
        )

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.view.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)

        new_view = np.repeat(np.identity(4, dtype=np.float32)[None, :, :], new_dense_capacity, axis=0)
        new_proj = np.repeat(np.identity(4, dtype=np.float32)[None, :, :], new_dense_capacity, axis=0)

        new_view[:cur] = self.view
        new_proj[:cur] = self.proj

        self.view = new_view
        self.proj = new_proj

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, CameraMatrices):
            raise TypeError(f"CameraMatricesStore expected CameraMatrices, got {type(component)}")

        if component.view.shape != (4, 4) or component.projection.shape != (4, 4):
            raise ValueError("CameraMatrices.view/projection must be shape (4,4) float32 matrices")

        self.view[dense_i] = component.view.astype(np.float32, copy=False)
        self.proj[dense_i] = component.projection.astype(np.float32, copy=False)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.view[dst_i] = self.view[src_i]
        self.proj[dst_i] = self.proj[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.view[dense_i] = np.identity(4, dtype=np.float32)
        self.proj[dense_i] = np.identity(4, dtype=np.float32)