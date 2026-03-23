from __future__ import annotations

from typing import Tuple

import numpy as np
import numpy.typing as npt

from astralengine.math.camera import rotation_matrix_xyz
from astralengine.math.types import Vec3, Mat4, Quat
from astralengine.math.quaternion import (
    quat_to_mat4, 
    quat_rotate_vec3,
    quat_conjugate,
    quat_normalize    
)


def make_translation_matrix(position: Vec3) -> Mat4:
    out = np.eye(4, dtype=np.float32)
    out[0, 3] = float(position[0])
    out[1, 3] = float(position[1])
    out[2, 3] = float(position[2])
    return out


def make_scale_matrix(scale: Vec3) -> Mat4:
    out = np.eye(4, dtype=np.float32)
    out[0, 0] = float(scale[0])
    out[1, 1] = float(scale[1])
    out[2, 2] = float(scale[2])
    return out


def compose_model_matrix(
    position: Vec3,
    rotation_deg: Vec3,
    scale: Vec3,
) -> Mat4:
    t = make_translation_matrix(position)
    r = rotation_matrix_xyz(rotation_deg)
    s = make_scale_matrix(scale)
    return (t @ r @ s).astype(np.float32, copy=False)


def compose_centered_model_matrix(
    position: Vec3,
    rotation: Vec3,
    scale: Vec3,
    centre: Vec3,
) -> Mat4:
    """
    Compose model matrix using a local pivot/centre offset.

    Geometry is shifted by -centre in local space before scale/rotation/world translation.
    """
    t_world = make_translation_matrix(position)
    r = rotation_matrix_xyz(rotation)
    s = make_scale_matrix(scale)

    t_centre = np.eye(4, dtype=np.float32)
    t_centre[0, 3] = -float(centre[0])
    t_centre[1, 3] = -float(centre[1])
    t_centre[2, 3] = -float(centre[2])

    return (t_world @ r @ s @ t_centre).astype(np.float32, copy=False)

def transform_matrix(pos: Vec3, rot: Quat) -> Mat4:
    m = quat_to_mat4(rot)
    m[0:3, 3] = pos
    
    return m

def transform_point(pos: Vec3, rot: Quat, point: Vec3) -> Vec3:
    return pos + quat_rotate_vec3(rot, point)

def inverse_transform_point(pos: Vec3, rot: Quat, point: Vec3) -> Vec3:
    inv_q = quat_conjugate(quat_normalize(rot))
    
    return quat_rotate_vec3(inv_q, point - pos)

def compose_transform(
    parent_pos: Vec3,
    parent_rot: Quat,
    child_pos: Vec3,
    child_rot: Quat
) -> Tuple[Vec3, Quat]:
    
    from astralengine.math.quaternion import quat_mul
    
    world_pos = transform_point(parent_pos, parent_rot, child_pos)
    world_rot = quat_mul(parent_rot, child_rot)
    
    return world_pos, world_rot