from __future__ import annotations

import numpy as np
from pyglet.window import key

from astralengine.components.player_controller import PlayerController
from astralengine.components.tags import DirtyMatrices, DirtyRemodel
from astralengine.components.transform import Transform
from astralengine.components.velocity import Velocity
from astralengine.ecs.query import Query
from astralengine.ecs.world import ECSWorld
from astralengine.resources.input_state import InputState
from astralengine.stores.player_controller_store import PlayerControllerStore
from astralengine.stores.transform_store import TransformStore
from astralengine.stores.velocity_store import VelocityStore


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def system_player_controller(world: ECSWorld, dt: float) -> None:
    inp = world.resources.get(InputState)
    if not inp.enabled:
        return

    tr_store: TransformStore = world.store(Transform)
    vel_store: VelocityStore = world.store(Velocity)
    ctrl_store: PlayerControllerStore = world.store(PlayerController)

    mdx, mdy = inp.mouse_delta

    for eid, i_tr, i_vel, i_ctrl in Query(world, (Transform, Velocity, PlayerController)):
        move_speed = float(ctrl_store.move_speed[i_ctrl])
        look_sens = float(ctrl_store.look_sensitivity[i_ctrl])

        yaw = float(tr_store.yaw_deg[i_tr])
        pitch = float(tr_store.pitch_deg[i_tr])

        yaw += float(mdx) * look_sens
        pitch -= float(mdy) * look_sens
        pitch = _clamp(pitch, -89.9, 89.9)

        tr_store.yaw_deg[i_tr] = yaw
        tr_store.pitch_deg[i_tr] = pitch

        yaw_rad = np.deg2rad(yaw)

        forward = np.array(
            [
                -np.sin(yaw_rad),
                0.0,
                -np.cos(yaw_rad),
            ],
            dtype=np.float32,
        )
        right = np.array(
            [
                np.cos(yaw_rad),
                0.0,
                -np.sin(yaw_rad),
            ],
            dtype=np.float32,
        )

        move = np.zeros(3, dtype=np.float32)

        if key.W in inp.keys_down:
            move += forward
        if key.S in inp.keys_down:
            move -= forward
        if key.D in inp.keys_down:
            move += right
        if key.A in inp.keys_down:
            move -= right
        if key.SPACE in inp.keys_down:
            move[1] += 1.0
        if key.LSHIFT in inp.keys_down:
            move[1] -= 1.0

        norm = float(np.linalg.norm(move))
        if norm > 1.0e-6:
            move /= norm
            move *= move_speed

        vel_store.vx[i_vel] = move[0]
        vel_store.vy[i_vel] = move[1]
        vel_store.vz[i_vel] = move[2]

        world.add_tag(eid, DirtyMatrices)
        world.add_tag(eid, DirtyRemodel)