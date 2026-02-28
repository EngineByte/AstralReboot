from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

from ecs.query import Query
from components.transform import Transform
from components.velocity import Velocity

if TYPE_CHECKING:
    from ecs.world import ECSWorld


def system_movement(world: "ECSWorld", dt: float) -> None:
    tr = world.store(Transform)
    vel = world.store(Velocity)
    dt32 = np.float32(dt)

    for eid, i_tr, i_vel in Query(world, (Transform, Velocity)):
        tr.px[i_tr] += vel.vx[i_vel] * dt32
        tr.py[i_tr] += vel.vy[i_vel] * dt32
        tr.pz[i_tr] += vel.vz[i_vel] * dt32