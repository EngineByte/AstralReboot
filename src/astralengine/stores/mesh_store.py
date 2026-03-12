from __future__ import annotations

from typing import Any
import numpy as np
import numpy.typing as npt

from astralengine.ecs.soa_store import SoAStore
from astralengine.components.mesh import Mesh


class MeshStore(SoAStore):
    def __init__(self, entity_capacity: int, initial_dense_capacity: int = 4096) -> None:
        super().__init__(entity_capacity=entity_capacity, initial_dense_capacity=initial_dense_capacity)

        cap = max(1, int(initial_dense_capacity))
        self.mesh_id: npt.NDArray[np.int32] = np.full(cap, -1, dtype=np.int32)

    def _ensure_dense_capacity(self, new_dense_capacity: int) -> None:
        cur = int(self.mesh_id.shape[0])
        if new_dense_capacity <= cur:
            return
        super()._ensure_dense_capacity(new_dense_capacity)
        self.mesh_id = np.resize(self.mesh_id, new_dense_capacity).astype(np.int32, copy=False)

    def _on_add_dense(self, dense_i: int, component: Any) -> None:
        if not isinstance(component, Mesh):
            raise TypeError(f'ChunkMeshStore expected ChunkMesh, got {type(component)}')
        self.mesh_id[dense_i] = np.int32(component.mesh_id)

    def _on_move_dense(self, dst_i: int, src_i: int) -> None:
        self.mesh_id[dst_i] = self.mesh_id[src_i]

    def _on_clear_dense(self, dense_i: int) -> None:
        self.mesh_id[dense_i] = -1