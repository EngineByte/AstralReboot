from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.model_matrix import ModelMatrix


class ModelMatrixStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 256) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.model: npt.NDArray[np.float32] = np.repeat(
            np.identity(4, dtype=np.float32)[None, :, :], cap, axis=0
        )
        self.centre: npt.NDArray[np.float32] = np.repeat(
            np.identity(4, dtype=np.float32)[None, :, :], cap, axis=0
        )

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.model.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)

        new_model = np.repeat(np.identity(4, dtype=np.float32)[None, :, :], new_dense_capacity, axis=0)
        new_model[:cur] = self.model

        new_centre = np.repeat(np.identity(4, dtype=np.float32)[None, :, :], new_dense_capacity, axis=0)
        new_centre[:cur] = self.centre
        
        self.model = new_model
        self.centre = new_centre

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, ModelMatrix):
            raise TypeError(f'ModelMatrixStore expected ModelMatrix, got {type(component)}')

        if component.model.shape != (4, 4):
            raise ValueError('ModelMatrix.model must be shape (4,4) float32 matrices')
        c = component.centre
        centre = np.identity(4, dtype=np.float32)
        centre[:3, 3] = (-c[0], -c[1], -c[2])

        self.model[dense_i] = component.model.astype(np.float32, copy=False)
        self.centre[dense_i] = centre.astype(np.float32, copy=False)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.model[dst_i] = self.model[src_i]
        self.centre[dst_i] = self.centre[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.model[dense_i] = np.identity(4, dtype=np.float32)
        self.centre[dense_i] = np.identity(4, dtype=np.float32)