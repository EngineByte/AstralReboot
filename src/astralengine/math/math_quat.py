from __future__ import annotations

import numpy as np
from numpy import typing as npt

Vec3 = npt.NDArray[np.float32]
Quat = npt.NDArray[np.float32]  # [w, x, y, z]


def quat_identity() -> Quat:
    return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)


def quat_normalize(q: Quat) -> Quat:
    norm = np.linalg.norm(q)
    if norm == 0.0:
        return quat_identity()
    return q / norm


def quat_mul(a: Quat, b: Quat) -> Quat:
    aw, ax, ay, az = a
    bw, bx, by, bz = b

    return np.array(
        [
            aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
        ],
        dtype=np.float64,
    )


def quat_from_axis_angle(axis: Vec3, angle_radians: float) -> Quat:
    axis_norm = np.linalg.norm(axis)
    if axis_norm == 0.0:
        return quat_identity()

    axis_unit = axis / axis_norm
    half = angle_radians * 0.5
    s = np.sin(half)

    return quat_normalize(
        np.array(
            [
                np.cos(half),
                axis_unit[0] * s,
                axis_unit[1] * s,
                axis_unit[2] * s,
            ],
            dtype=np.float64,
        )
    )


def quat_to_mat3(q: Quat) -> np.ndarray:
    q = quat_normalize(q)
    w, x, y, z = q

    xx = x * x
    yy = y * y
    zz = z * z
    xy = x * y
    xz = x * z
    yz = y * z
    wx = w * x
    wy = w * y
    wz = w * z

    return np.array(
        [
            [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz),       2.0 * (xz + wy)],
            [2.0 * (xy + wz),       1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)],
            [2.0 * (xz - wy),       2.0 * (yz + wx),       1.0 - 2.0 * (xx + yy)],
        ],
        dtype=np.float64,
    )


def quat_to_euler_ypr_degrees(q: Quat) -> tuple[float, float, float]:
    '''
    Returns yaw, pitch, roll in degrees.
    Convention depends on your engine's rotation order, so treat this as debug/UI output.
    '''
    q = quat_normalize(q)
    w, x, y, z = q

    # yaw (Y), pitch (X), roll (Z) style extraction can vary by convention.
    # This is one common Tait-Bryan extraction.
    sinp = 2.0 * (w * x - y * z)
    if abs(sinp) >= 1.0:
        pitch = np.sign(sinp) * (np.pi / 2.0)
    else:
        pitch = np.arcsin(sinp)

    yaw = np.arctan2(
        2.0 * (w * y + x * z),
        1.0 - 2.0 * (x * x + y * y),
    )

    roll = np.arctan2(
        2.0 * (w * z + x * y),
        1.0 - 2.0 * (x * x + z * z),
    )

    return tuple(np.degrees([yaw, pitch, roll]))

def quat_to_mat4(q: np.ndarray) -> np.ndarray:
    w, x, y, z = q

    xx = x * x
    yy = y * y
    zz = z * z
    xy = x * y
    xz = x * z
    yz = y * z
    wx = w * x
    wy = w * y
    wz = w * z

    return np.array([
        [1.0 - 2.0*(yy + zz), 2.0*(xy - wz),     2.0*(xz + wy), 0.0],
        [2.0*(xy + wz),       1.0 - 2.0*(xx + zz), 2.0*(yz - wx), 0.0],
        [2.0*(xz - wy),       2.0*(yz + wx),     1.0 - 2.0*(xx + yy), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float64)

def quat_conjugate(q):
    w, x, y, z = q
    return np.array([w, -x, -y, -z], dtype=np.float64)