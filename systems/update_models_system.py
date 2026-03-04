from __future__ import annotations

from typing import TYPE_CHECKING
import numpy as np

from ecs.query import Query
from ecs.math_camera import euler_yaw_pitch_roll

from components.transform import Transform
from components.camera import Camera
from components.model_matrix import ModelMatrix
from components.tags import DirtyRemodel

if TYPE_CHECKING:
    from ecs.world import ECSWorld


def system_update_model_matrices(world: 'ECSWorld', dt: float) -> None:
    tr = world.store(Transform)           
    mods = world.store(ModelMatrix)    

    for eid, i_tr, i_mod in Query(world, (Transform, ModelMatrix, DirtyRemodel)):
        px = float(tr.px[i_tr]); py = float(tr.py[i_tr]); pz = float(tr.pz[i_tr])
        yaw = float(tr.yaw[i_tr]); pitch = float(tr.pitch[i_tr]); roll = float(tr.roll[i_tr])

        rot = euler_yaw_pitch_roll(yaw, pitch, roll)
        pos = np.identity(4, dtype=np.float32)
        pos[:3, 3] = (px, py, pz)

        model = pos @ rot

        mods.model[i_mod] = model

        world.defer_remove_tag(eid, DirtyRemodel)
