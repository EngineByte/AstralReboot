from __future__ import annotations

import numpy as np

from astralengine.components.player_controller import PlayerController
from astralengine.ecs.soa_store import SoAStore


class PlayerControllerStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 128) -> None:
        super().__init__(entity_capacity, initial_dense_capacity)

        cap = self._dense_eids.shape[0]

        self.move_speed = np.full(cap, 8.0, dtype=np.float32)
        self.look_sensitivity = np.full(cap, 0.15, dtype=np.float32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        old_cap = self._dense_eids.shape[0]
        super()._ensure_dense_capacity(new_dense_capacity)
        new_cap = self._dense_eids.shape[0]

        if new_cap == old_cap:
            return

        self.move_speed = np.resize(self.move_speed, new_cap).astype(np.float32, copy=False)
        self.look_sensitivity = np.resize(self.look_sensitivity, new_cap).astype(np.float32, copy=False)

    def _on_add_dense(self, dense_i: int, component: PlayerController) -> None:
        self.move_speed[dense_i] = component.move_speed
        self.look_sensitivity[dense_i] = component.look_sensitivity

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.move_speed[dst_i] = self.move_speed[src_i]
        self.look_sensitivity[dst_i] = self.look_sensitivity[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.move_speed[dense_i] = 8.0
        self.look_sensitivity[dense_i] = 0.15