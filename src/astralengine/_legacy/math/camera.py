from __future__ import annotations

import numpy as np
import numpy.typing as npt


Vec3 = npt.NDArray[np.float32]
Mat4 = npt.NDArray[np.float32]


def _deg2rad3(rotation: Vec3) -> tuple[float, float, float]:
    pitch = float(np.deg2rad(rotation[0]))
    yaw = float(np.deg2rad(rotation[1]))
    roll = float(np.deg2rad(rotation[2]))
    return pitch, yaw, roll


def rotation_matrix_xyz(rotation: Vec3) -> Mat4:
    """
    Build a 4x4 rotation matrix from pitch/yaw/roll in degrees.

    Convention here:
    - pitch about +X
    - yaw about +Y
    - roll about +Z
    - composed as Ry @ Rx @ Rz for camera/gameplay use
    """
    pitch, yaw, roll = _deg2rad3(rotation)

    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    cr, sr = np.cos(roll), np.sin(roll)

    rx = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, cp, -sp, 0.0],
            [0.0, sp, cp, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    ry = np.array(
        [
            [cy, 0.0, sy, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-sy, 0.0, cy, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    rz = np.array(
        [
            [cr, -sr, 0.0, 0.0],
            [sr, cr, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    return (ry @ rx @ rz).astype(np.float32, copy=False)


def make_view_matrix(position: Vec3, rotation: Vec3) -> Mat4:
    """
    Build a standard view matrix from world-space camera position/rotation.
    """
    rot = rotation_matrix_xyz(rotation)
    rot_inv = rot.T
    rot_inv[3, :] = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
    rot_inv[:, 3] = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)

    translation = np.eye(4, dtype=np.float32)
    translation[0, 3] = -float(position[0])
    translation[1, 3] = -float(position[1])
    translation[2, 3] = -float(position[2])

    return (rot_inv @ translation).astype(np.float32, copy=False)


def make_perspective_matrix(
    fov: float,
    aspect: float,
    near: float,
    far: float,
) -> Mat4:
    """
    OpenGL-style perspective projection matrix.
    """
    if aspect <= 0.0:
        aspect = 1.0

    fov_rad = np.deg2rad(float(fov))
    f = 1.0 / np.tan(fov_rad * 0.5)

    out = np.zeros((4, 4), dtype=np.float32)
    out[0, 0] = f / float(aspect)
    out[1, 1] = f
    out[2, 2] = (far + near) / (near - far)
    out[2, 3] = (2.0 * far * near) / (near - far)
    out[3, 2] = -1.0
    return out


def forward_vector_from_rotation(rotation: Vec3) -> Vec3:
    """
    Returns the camera/game forward direction from pitch/yaw.
    """
    pitch, yaw, _roll = _deg2rad3(rotation)

    forward = np.array(
        [
            -np.sin(yaw) * np.cos(pitch),
            np.sin(pitch),
            -np.cos(yaw) * np.cos(pitch),
        ],
        dtype=np.float32,
    )

    norm = np.linalg.norm(forward)
    if norm > 1.0e-8:
        forward /= norm
    return forward


def right_vector_from_rotation(rotation: Vec3) -> Vec3:
    """
    Returns the camera/game right direction from yaw only.
    Keeps FPS-style strafing level with horizon.
    """
    _pitch, yaw, _roll = _deg2rad3(rotation)

    right = np.array(
        [
            np.cos(yaw),
            0.0,
            -np.sin(yaw),
        ],
        dtype=np.float32,
    )

    norm = np.linalg.norm(right)
    if norm > 1.0e-8:
        right /= norm
    return right