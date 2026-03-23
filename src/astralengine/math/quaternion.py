import numpy as np

from astralengine.math.types import Quat, Vec3, Mat4

def quat_identity() -> Quat:
    return np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float64)

def quat_normalize(q: Quat) -> Quat:
    n = np.linalg.norm(q)
    if n == 0.0:
        return quat_identity()
    
    return q / n

def quat_mul(a: Quat, b: Quat) -> Quat:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    
    return np.array([
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz
    ], dtype=np.float64)
    
def quat_conjugate(q: Quat) -> Quat:
    x, y, z, w = q
    
    return np.array([-x, -y, -z, w], dtype=np.float64)

def quat_rotate_vec3(q:Quat, v: Vec3) -> Vec3:
    q = quat_normalize(q)
    vq = np.array([v[0], v[1], v[2], 0.0], dtype=np.float64)
    
    rq = quat_mul(quat_mul(q, vq), quat_conjugate(q))
    
    return rq[:3]

def quat_to_mat4(q: Quat) -> Mat4:
    q = quat_normalize(q)
    x, y, z, w = q
   
    xx = x * x
    yy = y * y
    zz = z * z
    xy = x * y
    xz = x * z
    yz = y * z
    wx = w * x
    wy = w * y
    wz = w * z
   
    m = np.identity(4, dtype=np.float64)
    m[0, 0] = 1.0 - 2.0 * (yy + zz)
    m[0, 1] = 2.0 * (xy - wz)
    m[0, 2] = 2.0 * (xz + wy)
    

    m[1, 0] = 2.0 * (xy + wz)
    m[1, 1] = 1.0 - 2.0 * (xx + zz)
    m[1, 2] = 2.0 * (yz - wx)
   
    m[2, 0] = 2.0 * (xz - wy)
    m[2, 1] = 2.0 * (yz + wx)
    m[2, 2] = 1.0 - 2.0 * (xx + yy)
     
    return m                         