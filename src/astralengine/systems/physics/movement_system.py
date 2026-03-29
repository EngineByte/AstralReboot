from __future__ import annotations

from astralengine.components.tags import DirtyMatrices, DirtyRemodel
from astralengine.components.transform import Transform
from astralengine.components.velocity import Velocity
from astralengine.ecs.query.query import Query
from astralengine.ecs.core.world import ECSWorld
from astralengine.stores.transform_store import TransformStore
from astralengine.stores.velocity_store import VelocityStore


def system_movement(world: ECSWorld, dt: float) -> None:
    tr_store: TransformStore = world.store(Transform)
    vel_store: VelocityStore = world.store(Velocity)

    for eid, i_tr, i_vel in Query(world, (Transform, Velocity)):
        moved = False

        vx = float(vel_store.vx[i_vel])
        vy = float(vel_store.vy[i_vel])
        vz = float(vel_store.vz[i_vel])

        avx = float(vel_store.pitch_deg_per_sec[i_vel])
        avy = float(vel_store.yaw_deg_per_sec[i_vel])
        avz = float(vel_store.roll_deg_per_sec[i_vel])

        if vx != 0.0 or vy != 0.0 or vz != 0.0:
            tr_store.px[i_tr] += vx * dt
            tr_store.py[i_tr] += vy * dt
            tr_store.pz[i_tr] += vz * dt
            moved = True

        if avx != 0.0 or avy != 0.0 or avz != 0.0:
            tr_store.pitch_deg[i_tr] += avx * dt
            tr_store.yaw_deg[i_tr] += avy * dt
            tr_store.roll_deg[i_tr] += avz * dt
            moved = True

        if moved:
            world.add_tag(eid, DirtyMatrices)
            world.add_tag(eid, DirtyRemodel)