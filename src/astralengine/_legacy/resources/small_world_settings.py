from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SmallWorldSettings:
    fine_voxel_size_m: float = 0.05
    stamp_voxel_size_m: float = 1.0
    default_chunk_size_voxels: int = 32
    max_lod_level: int = 4