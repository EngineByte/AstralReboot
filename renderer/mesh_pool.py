from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np
import numpy.typing as npt


FloatArray = npt.NDArray[np.float32]
IndexArray = npt.NDArray[np.uint32]


@dataclass(slots=True)
class MeshData:
    verts: FloatArray
    indices: IndexArray


class MeshPool:
    def __init__(self) -> None:
        self._next_id: int = 0
        self._meshes: Dict[int, MeshData] = {}

    def upload_or_replace(self, mesh_id: int, verts: FloatArray, indices: IndexArray) -> int:
        if mesh_id < 0 or mesh_id not in self._meshes:
            mesh_id = self._next_id
            self._next_id += 1
        self._meshes[mesh_id] = MeshData(verts=verts, indices=indices)
        return mesh_id

    def get(self, mesh_id: int) -> MeshData | None:
        return self._meshes.get(mesh_id)