from __future__ import annotations

import numpy as np
import numpy.typing as npt

from astralengine.voxels.voxel_pool import VoxelBlock


Float4x4 = npt.NDArray[np.float32]


def stamp_cube_into_block(
    block: VoxelBlock,
    block_origin_m: tuple[float, float, float],
    voxel_size_m: float,
    stamp_matrix_world: Float4x4,
    stamp_size_m: tuple[float, float, float],
    fill_value: int = 1,
) -> None: ...