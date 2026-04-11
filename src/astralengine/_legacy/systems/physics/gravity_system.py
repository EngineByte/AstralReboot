from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from astralengine.old_code.components.acceleration import Acceleration
from astralengine.old_code.components.gravity import GravityWell
from astralengine.old_code.components.mass import Mass
from astralengine.old_code.components.transform import Transform
from astralengine.ecs.query.query import Query
from astralengine.old_code.resources.gravity_config import GravityConfig

if TYPE_CHECKING:
    from astralengine.ecs.core.world import ECSWorld


def system_gravity(world: "ECSWorld", dt: float) -> None:
    cfg = world.resources.get(GravityConfig)
    acc_store = world.store(Acceleration)

    target_bodies = list(Query(world, (Transform, Mass, Acceleration)))
    n_targets = len(target_bodies)

    if n_targets == 0:
        return

    # Clear old frame acceleration first.
    for _, _, _, i_acc in target_bodies:
        acc_store.ax[i_acc] = 0.0
        acc_store.ay[i_acc] = 0.0
        acc_store.az[i_acc] = 0.0
        acc_store.pitch_deg_per_sec2[i_acc] = 0.0
        acc_store.yaw_deg_per_sec2[i_acc] = 0.0
        acc_store.roll_deg_per_sec2[i_acc] = 0.0

    if not cfg.enabled:
        return

    source_bodies = list(Query(world, (Transform, GravityWell)))
    n_sources = len(source_bodies)

    if n_sources == 0:
        return

    tr_store = world.store(Transform)
    grav_store = world.store(GravityWell)

    target_eids = np.empty(n_targets, dtype=np.uint32)
    target_pos = np.empty((n_targets, 3), dtype=np.float32)

    for i, (eid, i_tr, _, _) in enumerate(target_bodies):
        target_eids[i] = np.uint32(eid)
        target_pos[i, 0] = np.float32(tr_store.px[i_tr])
        target_pos[i, 1] = np.float32(tr_store.py[i_tr])
        target_pos[i, 2] = np.float32(tr_store.pz[i_tr])

    source_eids = np.empty(n_sources, dtype=np.uint32)
    source_pos = np.empty((n_sources, 3), dtype=np.float32)
    source_mu = np.empty(n_sources, dtype=np.float32)
    source_softening = np.empty(n_sources, dtype=np.float32)
    source_enabled = np.empty(n_sources, dtype=np.bool_)

    for j, (eid, i_tr, i_grav) in enumerate(source_bodies):
        source_eids[j] = np.uint32(eid)
        source_pos[j, 0] = np.float32(tr_store.px[i_tr])
        source_pos[j, 1] = np.float32(tr_store.py[i_tr])
        source_pos[j, 2] = np.float32(tr_store.pz[i_tr])
        source_mu[j] = np.float32(grav_store.mu[i_grav])
        source_softening[j] = np.float32(grav_store.softening[i_grav])
        source_enabled[j] = bool(grav_store.enabled[i_grav])

    displacement = source_pos[None, :, :] - target_pos[:, None, :]
    dist_sq = np.sum(displacement * displacement, axis=2)

    total_softening = np.float32(cfg.softening) + source_softening[None, :]
    dist_sq = dist_sq + total_softening * total_softening

    # Prevent self-attraction when an entity is both a target and a source.
    same_entity = target_eids[:, None] == source_eids[None, :]
    dist_sq[same_entity] = np.inf

    # Disable inactive gravity sources.
    dist_sq[:, ~source_enabled] = np.inf

    if cfg.max_force_distance is not None:
        max_dist_sq = np.float32(cfg.max_force_distance) * np.float32(cfg.max_force_distance)
        too_far = dist_sq > max_dist_sq
        dist_sq[too_far] = np.inf

    inv_dist = 1.0 / np.sqrt(dist_sq)
    inv_dist3 = inv_dist * inv_dist * inv_dist

    # a_i = sum_j (mu_j * r_ij / |r_ij|^3)
    scalar = source_mu[None, :] * inv_dist3
    accel = np.sum(displacement * scalar[:, :, None], axis=1, dtype=np.float32)

    if cfg.max_accel is not None:
        max_a = np.float32(cfg.max_accel)
        mag = np.linalg.norm(accel, axis=1)
        mask = mag > max_a
        if np.any(mask):
            accel[mask] *= (max_a / mag[mask])[:, None]

    for i, (_, _, _, i_acc) in enumerate(target_bodies):
        acc_store.ax[i_acc] = np.float32(accel[i, 0])
        acc_store.ay[i_acc] = np.float32(accel[i, 1])
        acc_store.az[i_acc] = np.float32(accel[i, 2])