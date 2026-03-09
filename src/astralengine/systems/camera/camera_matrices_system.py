from __future__ import annotations

from typing import TYPE_CHECKING

from ecs.query import Query
from ecs.math_camera import view_from_transform, perspective_rh_opengl

from components.transform import Transform
from components.camera import Camera
from components.camera_matrices import CameraMatrices
from components.tags import DirtyMatrices

if TYPE_CHECKING:
    from ecs.world import ECSWorld


def system_update_camera_matrices(world: 'ECSWorld', dt: float) -> None:
    tr = world.store(Transform)            
    cam = world.store(Camera)             
    mats = world.store(CameraMatrices)    

    for eid, i_tr, i_cam, i_mats in Query(world, (Transform, Camera, CameraMatrices, DirtyMatrices)):
        px = float(tr.px[i_tr]); py = float(tr.py[i_tr]); pz = float(tr.pz[i_tr])
        yaw = float(tr.yaw[i_tr]); pitch = float(tr.pitch[i_tr]); roll = float(tr.roll[i_tr])

        fov = float(cam.fov[i_cam])
        aspect = float(cam.aspect[i_cam])
        near = float(cam.near[i_cam])
        far = float(cam.far[i_cam])

        view = view_from_transform(px, py, pz, yaw, pitch, roll)
        proj = perspective_rh_opengl(fov, aspect, near, far)

        mats.view[i_mats] = view
        mats.proj[i_mats] = proj

        world.defer_remove_tag(eid, DirtyMatrices)
        