from __future__ import annotations

from dataclasses import dataclass
from typing import List
import numpy as np
import numpy.typing as npt


@dataclass(slots=True)
class VoxelBlock:
    size: int
    data: npt.NDArray[np.uint8]


class VoxelPool:
    def __init__(self) -> None:
        self._blocks: List[VoxelBlock] = []
        self._free: List[int] = []

    def alloc(self, size: int, fill: int = 0) -> int:
        size = int(size)
        if size <= 0:
            raise ValueError('size must be positive')

        if self._free:
            h = self._free.pop()
            self._blocks[h] = VoxelBlock(size=size, data=np.full(size**3, fill, dtype=np.uint8))
            return h

        h = len(self._blocks)
        self._blocks.append(VoxelBlock(size=size, data=np.full(size**3, fill, dtype=np.uint8)))
        return h

    def free(self, handle: int) -> None:
        h = int(handle)
        if h < 0 or h >= len(self._blocks):
            return
        self._free.append(h)

    def block(self, handle: int) -> VoxelBlock:
        h = int(handle)
        return self._blocks[h]

    @staticmethod
    def idx(size: int, x: int, y: int, z: int) -> int:
        return x + size * (y + size * z)