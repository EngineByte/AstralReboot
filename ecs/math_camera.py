from __future__ import annotations

import numpy as np
import numpy.typing as npt

Mat4 = npt.NDArray[np.float32]


def _rot_x(a: float) -> Mat4:
    c = np.float32(np.cos(a))
    s = np.float32(np.sin(a))
    return np.array(
        [[1, 0, 0, 0],
         [0, c, -s, 0],
         [0, s,  c, 0],
         [0, 0, 0, 1]],
        dtype=np.float32,
    )


def _rot_y(a: float) -> Mat4:
    a = np.radians(a)
    c = np.float32(np.cos(a))
    s = np.float32(np.sin(a))
    return np.array(
        [[ c, 0, s, 0],
         [ 0, 1, 0, 0],
         [-s, 0, c, 0],
         [ 0, 0, 0, 1]],
        dtype=np.float32,
    )


def _rot_z(a: float) -> Mat4:
    c = np.float32(np.cos(a))
    s = np.float32(np.sin(a))
    return np.array(
        [[c, -s, 0, 0],
         [s,  c, 0, 0],
         [0,  0, 1, 0],
         [0,  0, 0, 1]],
        dtype=np.float32,
    )


def euler_yaw_pitch_roll(yaw: float, pitch: float, roll: float) -> Mat4:
    return _rot_y(yaw) @ _rot_x(pitch) @ _rot_z(roll)


def view_from_transform(px: float, py: float, pz: float, yaw: float, pitch: float, roll: float) -> Mat4:
    R = euler_yaw_pitch_roll(yaw + 180.0, pitch, roll)
    Rt = R.T

    Tinv = np.identity(4, dtype=np.float32)
    Tinv[0, 3] = np.float32(-px)
    Tinv[1, 3] = np.float32(-py)
    Tinv[2, 3] = np.float32(-pz)

    return Rt @ Tinv


def perspective_rh_opengl(fov_deg: float, aspect: float, near: float, far: float) -> Mat4:
    fov_rad = np.deg2rad(np.float32(fov_deg))
    f = np.float32(1.0) / np.float32(np.tan(fov_rad * np.float32(0.5)))

    nf = np.float32(1.0) / np.float32(near - far)

    M = np.zeros((4, 4), dtype=np.float32)
    M[0, 0] = f / np.float32(aspect)
    M[1, 1] = f
    M[2, 2] = (np.float32(far) + np.float32(near)) * nf
    M[2, 3] = (np.float32(2.0) * np.float32(far) * np.float32(near)) * nf
    M[3, 2] = np.float32(-1.0)
    return M