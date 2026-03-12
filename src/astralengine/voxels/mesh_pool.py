from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import numpy as np
import numpy.typing as npt


Float32Array = npt.NDArray[np.float32]
UInt32Array = npt.NDArray[np.uint32]


@dataclass(slots=True)
class MeshData:
    """
    CPU-side mesh payload.

    Conventions:
    - verts is shape (N, F), typically float32
    - indices is shape (M,), uint32
    - vertex_format is descriptive only; it is not interpreted here
    """
    verts: Float32Array
    indices: UInt32Array
    vertex_format: str = "P3_N3_U2"

    @property
    def vertex_count(self) -> int:
        return int(self.verts.shape[0])

    @property
    def index_count(self) -> int:
        return int(self.indices.shape[0])

    @property
    def stride_floats(self) -> int:
        if self.verts.ndim != 2:
            raise ValueError("verts must have shape (N, F)")
        return int(self.verts.shape[1])

    def copy(self) -> "MeshData":
        return MeshData(
            verts=np.array(self.verts, dtype=np.float32, copy=True),
            indices=np.array(self.indices, dtype=np.uint32, copy=True),
            vertex_format=self.vertex_format,
        )


class MeshPool:
    """
    CPU-side mesh repository.

    This pool stores generated mesh data before it is uploaded to GPU memory.
    It is intentionally separate from any OpenGL/renderer backend state.

    Typical usage:
        mesh_pool = MeshPool()

        mesh_id = mesh_pool.upload_new(verts, indices)
        mesh = mesh_pool.get(mesh_id)

        mesh_pool.replace(mesh_id, new_verts, new_indices)
        mesh_pool.release(mesh_id)
    """

    def __init__(self) -> None:
        self._meshes: dict[int, MeshData] = {}
        self._free_ids: list[int] = []
        self._next_id: int = 0

    def upload_new(
        self,
        verts: Float32Array,
        indices: UInt32Array,
        *,
        vertex_format: str = "P3_N3_U2",
        copy_arrays: bool = True,
    ) -> int:
        """
        Store a new mesh and return its mesh_id.
        """
        mesh_id = self._allocate_id()
        self._meshes[mesh_id] = self._build_mesh_data(
            verts=verts,
            indices=indices,
            vertex_format=vertex_format,
            copy_arrays=copy_arrays,
        )
        return mesh_id

    def replace(
        self,
        mesh_id: int,
        verts: Float32Array,
        indices: UInt32Array,
        *,
        vertex_format: str | None = None,
        copy_arrays: bool = True,
    ) -> None:
        """
        Replace an existing mesh in-place.

        Raises:
            KeyError: if mesh_id does not exist
        """
        old = self._meshes[mesh_id]
        fmt = old.vertex_format if vertex_format is None else vertex_format
        self._meshes[mesh_id] = self._build_mesh_data(
            verts=verts,
            indices=indices,
            vertex_format=fmt,
            copy_arrays=copy_arrays,
        )

    def upload_or_replace(
        self,
        mesh_id: int,
        verts: Float32Array,
        indices: UInt32Array,
        *,
        vertex_format: str = "P3_N3_U2",
        copy_arrays: bool = True,
    ) -> int:
        """
        Replace mesh_id if it exists, otherwise allocate a new one.

        Returns the actual mesh_id that now holds the mesh.
        """
        if mesh_id < 0 or mesh_id not in self._meshes:
            return self.upload_new(
                verts,
                indices,
                vertex_format=vertex_format,
                copy_arrays=copy_arrays,
            )

        self.replace(
            mesh_id,
            verts,
            indices,
            vertex_format=vertex_format,
            copy_arrays=copy_arrays,
        )
        return mesh_id

    def get(self, mesh_id: int) -> MeshData:
        """
        Return the stored mesh data for mesh_id.
        """
        return self._meshes[mesh_id]

    def try_get(self, mesh_id: int) -> MeshData | None:
        """
        Return mesh data if present, else None.
        """
        return self._meshes.get(mesh_id)

    def release(self, mesh_id: int) -> None:
        """
        Remove a mesh and recycle its ID.

        Raises:
            KeyError: if mesh_id does not exist
        """
        del self._meshes[mesh_id]
        self._free_ids.append(mesh_id)

    def clear(self) -> None:
        """
        Remove all meshes and reset the pool.
        """
        self._meshes.clear()
        self._free_ids.clear()
        self._next_id = 0

    def contains(self, mesh_id: int) -> bool:
        return mesh_id in self._meshes

    def __contains__(self, mesh_id: object) -> bool:
        return isinstance(mesh_id, int) and mesh_id in self._meshes

    def __len__(self) -> int:
        return len(self._meshes)

    def ids(self) -> Iterator[int]:
        return iter(self._meshes.keys())

    def items(self) -> Iterator[tuple[int, MeshData]]:
        return iter(self._meshes.items())

    def total_vertices(self) -> int:
        return sum(mesh.vertex_count for mesh in self._meshes.values())

    def total_indices(self) -> int:
        return sum(mesh.index_count for mesh in self._meshes.values())

    def _allocate_id(self) -> int:
        if self._free_ids:
            return self._free_ids.pop()

        mesh_id = self._next_id
        self._next_id += 1
        return mesh_id

    def _build_mesh_data(
        self,
        *,
        verts: Float32Array,
        indices: UInt32Array,
        vertex_format: str,
        copy_arrays: bool,
    ) -> MeshData:
        verts32 = self._normalize_verts(verts, copy_arrays=copy_arrays)
        indices32 = self._normalize_indices(indices, copy_arrays=copy_arrays)

        if verts32.ndim != 2:
            raise ValueError(
                f"verts must have shape (N, F), got shape {verts32.shape}"
            )

        if indices32.ndim != 1:
            raise ValueError(
                f"indices must have shape (M,), got shape {indices32.shape}"
            )

        if verts32.shape[0] == 0:
            raise ValueError("verts must contain at least 1 vertex")

        if indices32.shape[0] == 0:
            raise ValueError("indices must contain at least 1 index")

        return MeshData(
            verts=verts32,
            indices=indices32,
            vertex_format=vertex_format,
        )

    @staticmethod
    def _normalize_verts(
        verts: Float32Array,
        *,
        copy_arrays: bool,
    ) -> Float32Array:
        arr = np.asarray(verts, dtype=np.float32)
        if copy_arrays:
            arr = np.array(arr, dtype=np.float32, copy=True)
        return np.ascontiguousarray(arr, dtype=np.float32)

    @staticmethod
    def _normalize_indices(
        indices: UInt32Array,
        *,
        copy_arrays: bool,
    ) -> UInt32Array:
        arr = np.asarray(indices, dtype=np.uint32)
        if copy_arrays:
            arr = np.array(arr, dtype=np.uint32, copy=True)
        return np.ascontiguousarray(arr, dtype=np.uint32)