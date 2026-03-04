from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

from ecs.query import Query
from components.transform import Transform
from components.velocity import Velocity
from components.acceleration import Acceleration
from components.gravity import GravityWell
from components.tags import DirtyRemodel

if TYPE_CHECKING:
    from ecs.world import ECSWorld


_EPS = np.float32(1e-6)

def system_movement(world: "ECSWorld", dt: float) -> None:
    tr = world.store(Transform)
    vel = world.store(Velocity)
    acc = world.store(Acceleration)
    grav = world.store(GravityWell)

    dt32 = np.float32(dt)
    half = np.float32(0.5) * dt32

    for eid, i_tr, i_g, i_a in Query(world, (Transform, GravityWell, Acceleration)):
        rx = tr.px[i_tr] - grav.cx[i_g]
        ry = tr.py[i_tr] - grav.cy[i_g]
        rz = tr.pz[i_tr] - grav.cz[i_g]

        r2 = rx*rx + ry*ry + rz*rz + _EPS
        inv_r = np.float32(1.0) / np.sqrt(r2)
        inv_r3 = inv_r * inv_r * inv_r

        mu = grav.mu[i_g]
        acc.ax[i_a] = -mu * rx * inv_r3
        acc.ay[i_a] = -mu * ry * inv_r3
        acc.az[i_a] = -mu * rz * inv_r3

    for eid, i_tr, i_v, i_a in Query(world, (Transform, Velocity, Acceleration)):
        vel.vx[i_v] += acc.ax[i_a] * half
        vel.vy[i_v] += acc.ay[i_a] * half
        vel.vz[i_v] += acc.az[i_a] * half

        tr.px[i_tr] += vel.vx[i_v] * dt32
        tr.py[i_tr] += vel.vy[i_v] * dt32
        tr.pz[i_tr] += vel.vz[i_v] * dt32

        tr.yaw[i_tr]   += vel.ay[i_v] * dt32
        tr.pitch[i_tr] += vel.ax[i_v] * dt32
        tr.roll[i_tr]  += vel.az[i_v] * dt32

        world.defer_add_tag(eid, DirtyRemodel)

    for eid, i_tr, i_g, i_a in Query(world, (Transform, GravityWell, Acceleration)):
        rx = tr.px[i_tr] - grav.cx[i_g]
        ry = tr.py[i_tr] - grav.cy[i_g]
        rz = tr.pz[i_tr] - grav.cz[i_g]

        r2 = rx*rx + ry*ry + rz*rz + _EPS
        inv_r = np.float32(1.0) / np.sqrt(r2)
        inv_r3 = inv_r * inv_r * inv_r

        mu = grav.mu[i_g]
        acc.ax[i_a] = -mu * rx * inv_r3
        acc.ay[i_a] = -mu * ry * inv_r3
        acc.az[i_a] = -mu * rz * inv_r3

    for eid, i_v, i_a in Query(world, (Velocity, Acceleration)):
        vel.vx[i_v] += acc.ax[i_a] * half
        vel.vy[i_v] += acc.ay[i_a] * half
        vel.vz[i_v] += acc.az[i_a] * half