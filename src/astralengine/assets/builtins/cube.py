from __future__ import annotations

import numpy as np
import numpy.typing as npt


FloatArray = npt.NDArray[np.float32]
UIntArray = npt.NDArray[np.uint32]


def build_cube_mesh() -> tuple[FloatArray, UIntArray]:
    '''
    Return a simple indexed cube mesh. Used with glDrawElements()
    '''
    vertices = np.array([
        # Back (-z)
        [ 0.5,  0.5, -0.5], # 0
        [ 0.5, -0.5, -0.5], # 1
        [-0.5, -0.5, -0.5], # 2
        [-0.5,  0.5, -0.5], # 3
        # Front (+z)
        [-0.5,  0.5,  0.5], # 4
        [-0.5, -0.5,  0.5], # 5
        [ 0.5, -0.5,  0.5], # 6
        [ 0.5,  0.5,  0.5], # 7
        # Right (-x)
        [-0.5,  0.5, -0.5], # 8 dup of # 3
        [-0.5, -0.5, -0.5], # 9 dup of # 2
        [-0.5, -0.5,  0.5], # 10 dup of # 5
        [-0.5,  0.5,  0.5], # 11 dup of # 4
        # Left (+x)
        [ 0.5,  0.5,  0.5], # 12 dup of # 7
        [ 0.5, -0.5,  0.5], # 13 dup of # 6
        [ 0.5, -0.5, -0.5], # 14 dup of # 1
        [ 0.5,  0.5, -0.5], # 15 dup of # 0
        # Top (+y)
        [ 0.5,  0.5,  0.5], # 16 dup of # 7
        [ 0.5,  0.5, -0.5], # 17 dup of # 0
        [-0.5,  0.5, -0.5], # 18 dup of # 3
        [-0.5,  0.5,  0.5], # 19 dup of # 4
        # Bottom (-y)
        [ 0.5, -0.5, -0.5], # 20 dup of # 1
        [ 0.5, -0.5,  0.5], # 21 dup of # 6
        [-0.5, -0.5,  0.5], # 22 dup of # 5
        [-0.5, -0.5, -0.5]  # 23 dup of # 2
    ], dtype=np.float32)

    indices = np.array(
        [
            # back
            0, 1, 2, 2, 3, 0,
            # front
            4, 5, 6, 6, 7, 4,
            # right
            8, 9, 10, 10, 11, 8,
            # left
            12, 13, 14, 14, 15, 12,
            # top
            16, 17, 18, 18, 19, 16,
            # bottom
            20, 21, 22, 22, 23, 20,
        ],
        dtype=np.uint32,
    )

    return vertices, indices