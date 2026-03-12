from __future__ import annotations

from astralengine.components.parent_follow import ParentFollow
from astralengine.components.tags import DirtyMatrices
from astralengine.components.transform import Transform
from astralengine.ecs.query import Query
from astralengine.ecs.world import ECSWorld
from astralengine.stores.parent_follow_store import ParentFollowStore
from astralengine.stores.transform_store import TransformStore


def system_parent_follow(world: ECSWorld, dt: float) -> None:
    _ = dt

    tr_store: TransformStore = world.store(Transform)
    follow_store: ParentFollowStore = world.store(ParentFollow)

    for eid, i_tr, i_follow in Query(world, (Transform, ParentFollow)):
        parent_eid = int(follow_store.parent_eid[i_follow])

        try:
            i_parent = tr_store.dense_index(parent_eid)
        except KeyError:
            continue

        if bool(follow_store.follow_position[i_follow]):
            tr_store.px[i_tr] = tr_store.px[i_parent] + follow_store.off_x[i_follow]
            tr_store.py[i_tr] = tr_store.py[i_parent] + follow_store.off_y[i_follow]
            tr_store.pz[i_tr] = tr_store.pz[i_parent] + follow_store.off_z[i_follow]

        if bool(follow_store.follow_rotation[i_follow]):
            tr_store.pitch_deg[i_tr] = tr_store.pitch_deg[i_parent]
            tr_store.yaw_deg[i_tr] = tr_store.yaw_deg[i_parent]
            tr_store.roll_deg[i_tr] = tr_store.roll_deg[i_parent]

        world.add_tag(eid, DirtyMatrices)