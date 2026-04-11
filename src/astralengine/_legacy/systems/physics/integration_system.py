from __future__ import annotations

from astralengine.old_code.components.acceleration import Acceleration
from astralengine.old_code.components.transform import Transform
from astralengine.old_code.components.velocity import Velocity
from astralengine.ecs.query.query import Query
from astralengine.ecs.core.world import ECSWorld


def system_integration(world: ECSWorld, dt: float) -> None:
    vel_store = world.store(Velocity)
    acc_store = world.store(Acceleration)

    for _, i_acc, i_vel in Query(world, (Acceleration, Velocity)):
        vel_store.vx[i_vel] += float(acc_store.ax[i_acc]) * dt
        vel_store.vy[i_vel] += float(acc_store.ay[i_acc]) * dt
        vel_store.vz[i_vel] += float(acc_store.az[i_acc]) * dt

        vel_store.pitch_deg_per_sec[i_vel] += float(acc_store.pitch_deg_per_sec2[i_acc]) * dt
        vel_store.yaw_deg_per_sec[i_vel] += float(acc_store.yaw_deg_per_sec2[i_acc]) * dt
        vel_store.roll_deg_per_sec[i_vel] += float(acc_store.roll_deg_per_sec2[i_acc]) * dt