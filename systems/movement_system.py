from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

from ecs.query import Query
from components.transform import Transform
from components.velocity import Velocity
from components.mass import Mass
from components.acceleration import Acceleration
from components.gravity import GravityWell
from components.tags import DirtyRemodel

from systems.gravity_system import system_gravity

if TYPE_CHECKING:
    from ecs.world import ECSWorld


def system_clear_acceleration(world: 'ECSWorld', dt: float) -> None:
    acc = world.store(Acceleration)
    for eid, i_acc in Query(world, (Acceleration,)):
        acc.ax[i_acc] = 0
        acc.ay[i_acc] = 0
        acc.az[i_acc] = 0

def system_integrate_acceleration(world: 'ECSWorld', dt: float) -> None:
    acc = world.store(Acceleration)
    vel = world.store(Velocity)

    dt32 = np.float32(dt)

    for eid, i_acc, i_vel in Query(world, (Acceleration, Velocity)):
        vel.vx[i_vel] += acc.ax[i_acc] * dt32
        vel.vy[i_vel] += acc.ay[i_acc] * dt32
        vel.vz[i_vel] += acc.az[i_acc] * dt32

def system_integrate_velocity(world: 'ECSWorld', dt: float) -> None:
    vel = world.store(Velocity)
    tr = world.store(Transform)

    dt32 = np.float32(dt)

    for eid, i_vel, i_tr in Query(world, (Velocity, Transform)):
        tr.px[i_tr] += vel.vx[i_vel] * dt32
        tr.py[i_tr] += vel.vy[i_vel] * dt32
        tr.pz[i_tr] += vel.vz[i_vel] * dt32

        tr.yaw[i_tr] += vel.ay[i_vel] * dt32
        tr.pitch[i_tr] += vel.ax[i_vel] * dt32
        tr.roll[i_tr] += vel.az[i_vel] * dt32

def system_movement(world: 'ECSWorld', dt: float) -> None:
    tr = world.store(Transform)
    vel = world.store(Velocity)
    acc = world.store(Acceleration)
    grav = world.store(GravityWell)

    dt32 = np.float32(dt)
    half = np.float32(0.5) * dt32

    

    system_clear_acceleration(world, dt32)
    system_gravity(world, half)

    system_integrate_acceleration(world, half)
    system_integrate_velocity(world, dt32)

    system_clear_acceleration(world, dt32)
    system_gravity(world, half)

    system_integrate_acceleration(world, half)


    for eid, _, _, _, _ in Query(world, (Transform, Velocity, Acceleration, Mass)):
        world.add_tag(eid, DirtyRemodel)




    