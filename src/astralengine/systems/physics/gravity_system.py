from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

from astralengine.ecs.query import Query
from astralengine.components.transform import Transform
from astralengine.components.mass import Mass
from astralengine.components.acceleration import Acceleration

from astralengine.resources.gravity_config import GravityConfig

if TYPE_CHECKING:
    from ecs.world import ECSWorld


def system_gravity(world: "ECSWorld", dt: float) -> None:
    cfg = world.resources.get(GravityConfig)

    bodies = list(Query(world, (Transform, Mass, Acceleration)))
    n = len(bodies)

    if n < 2:
        return
    
    mass = world.store(Mass)
    tr = world.store(Transform)
    acc = world.store(Acceleration)

    G = np.float32(cfg.G)
    eps2 = np.float32(cfg.softening * cfg.softening)

    positions = np.empty((n, 3), dtype=np.float32)
    masses = np.empty((n,), dtype=np.float32)

    for i, (_, i_tr, i_mass, _) in enumerate(bodies):
        position = np.array([tr.px[i_tr], tr.py[i_tr], tr.pz[i_tr]], dtype=np.float32)
        positions[i] = position
        masses[i] = np.float32(mass.mass[i_mass])

    displacement = positions[None, :, :] - positions[:, None, :]

    dist_sq = np.sum(displacement * displacement, axis=2) + eps2

    np.fill_diagonal(dist_sq, np.inf)

    inv_dist = 1.0 / np.sqrt(dist_sq)
    inv_dist3 = inv_dist * inv_dist * inv_dist

    scalar = G * masses[None, :] * inv_dist3
    accel = np.sum(displacement * scalar[:, :, None], axis=1)

    if cfg.max_accel is not None:
        max_a = np.float32(cfg.max_accel)
        mag = np.linalg.norm(accel, axis=1)
        mask = mag > max_a
        if np.any(mask):
            accel[mask] *= (max_a / mag[mask])[:, None]

    for i, (_, _, _, i_acc) in enumerate(bodies):
        acc.ax[i_acc] = accel[i][0]
        acc.ay[i_acc] = accel[i][1]
        acc.az[i_acc] = accel[i][2]

    