from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LodVolume:
    fine_voxel_size_m: float
    lod_level: int
    block_size: int


def lod_voxel_size_m(fine_voxel_size_m: float, lod_level: int) -> float: ...
def lod_downsample_stride(lod_level: int) -> int: ...