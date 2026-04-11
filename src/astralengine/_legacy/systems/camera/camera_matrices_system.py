from __future__ import annotations

import numpy as np

from astralengine.old_code.components.camera import Camera
from astralengine.old_code.components.camera_matrices import CameraMatrices
from astralengine.old_code.components.tags import DirtyMatrices
from astralengine.old_code.components.transform import Transform
from astralengine.ecs.query.query import Query
from astralengine.ecs.core.world import ECSWorld
from astralengine.old_code.math.camera import make_perspective_matrix, make_view_matrix
from astralengine.old_code.resources.render_settings import RenderSettings
from astralengine.old_code.stores.camera_matrices_store import CameraMatricesStore
from astralengine.old_code.stores.camera_store import CameraStore
from astralengine.old_code.stores.transform_store import TransformStore


def system_update_camera_matrices(world: ECSWorld, dt: float) -> None:
    _ = dt

    settings = world.resources.get(RenderSettings)

    tr_store: TransformStore = world.store(Transform)
    cam_store: CameraStore = world.store(Camera)
    mats_store: CameraMatricesStore = world.store(CameraMatrices)

    aspect = settings.aspect_ratio()

    for eid, i_tr, i_cam, i_mats in Query(
        world,
        (Transform, Camera, CameraMatrices, DirtyMatrices),
    ):
        position = np.array(
            [
                tr_store.px[i_tr],
                tr_store.py[i_tr],
                tr_store.pz[i_tr],
            ],
            dtype=np.float32,
        )

        rotation = np.array(
            [
                tr_store.pitch_deg[i_tr],
                tr_store.yaw_deg[i_tr],
                tr_store.roll_deg[i_tr],
            ],
            dtype=np.float32,
        )

        fov = float(cam_store.fov[i_cam])
        near = float(cam_store.near[i_cam])
        far = float(cam_store.far[i_cam])

        view = make_view_matrix(
            position=position,
            rotation=rotation,
        )
        proj = make_perspective_matrix(
            fov=fov,
            aspect=aspect,
            near=near,
            far=far,
        )

        mats_store.view[i_mats] = view
        mats_store.proj[i_mats] = proj

        world.remove_tag(eid, DirtyMatrices)