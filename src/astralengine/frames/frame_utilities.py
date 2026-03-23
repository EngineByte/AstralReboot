import numpy as np

from astralengine.math.types import Vec3, Quat
from astralengine.math.quaternion import quat_identity


def normalize(v: Vec3) -> Vec3:
    n = np.linalg.norm(v)
    if n == 0.0:
        return v.copy()
    
    return v / n

def tangent_basis_from_planet_center(
    world_position: Vec3,
    planet_center_world: Vec3,
    preferred_forward_world: Vec3
) -> tuple[Vec3, Vec3, Vec3]:
    
    up = normalize(world_position - planet_center_world)
    
    fwd = preferred_forward_world - np.dot(preferred_forward_world, up) * up
    
    if np.linalg.norm(fwd) < 1e-9:
        arbitrary = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        if abs(np.dot(arbitrary, up)) > 0.99:
            arbitrary = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        fwd = arbitrary - np.dot(arbitrary, up) * up
        
    forward = normalize(fwd)
    right = normalize(np.cross(forward, up))
    forward = normalize(np.cross(up, right))
    
    return  right, up, forward

def basis_to_quat(right: Vec3, up: Vec3, forward: Vec3) -> Quat:
    
    _ = (right, up, forward)
    
    return quat_identity()