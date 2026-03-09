from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from ecs.soa_store import SoAStore
from components.player_controller import PlayerController


class PlayerControllerStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 256) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = int(initial_dense_capacity)
        if cap <= 0:
            cap = 1

        self.move_speed: npt.NDArray[np.float32] = np.full(cap, 6.0, dtype=np.float32)
        self.mouse_sens: npt.NDArray[np.float32] = np.full(cap, 0.15, dtype=np.float32)
        self.invert_y: npt.NDArray[np.bool_] = np.zeros(cap, dtype=np.bool_)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.move_speed.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)

        self.move_speed = np.resize(self.move_speed, new_dense_capacity).astype(np.float32, copy=False)
        self.mouse_sens = np.resize(self.mouse_sens, new_dense_capacity).astype(np.float32, copy=False)
        self.invert_y = np.resize(self.invert_y, new_dense_capacity).astype(np.bool_, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, PlayerController):
            raise TypeError(f'PlayerControllerStore expected PlayerController, got {type(component)}')

        self.move_speed[dense_i] = np.float32(component.move_speed)
        self.mouse_sens[dense_i] = np.float32(component.mouse_sens)
        self.invert_y[dense_i] = np.bool_(component.invert_y)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.move_speed[dst_i] = self.move_speed[src_i]
        self.mouse_sens[dst_i] = self.mouse_sens[src_i]
        self.invert_y[dst_i] = self.invert_y[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.move_speed[dense_i] = np.float32(6.0)
        self.mouse_sens[dense_i] = np.float32(0.0025)
        self.invert_y[dense_i] = False