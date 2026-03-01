from __future__ import annotations

from typing import TYPE_CHECKING
from ecs.query import Query

from components.camera import Camera
from components.camera_matrices import CameraMatrices
from renderer.renderer import Renderer
from stores.camera_matrices_store import CameraMatricesStore

if TYPE_CHECKING:
    from ecs.world import ECSWorld


def system_pre_render(world: 'ECSWorld', dt: float) -> None:
    renderer = world.resources.get(Renderer)

    mats_store:CameraMatricesStore = world.store(CameraMatrices)

    cam_eid = None
    cam_mats_i = None

    for eid, i_cam, i_mats in Query(world, (Camera, CameraMatrices)):
        cam_eid = eid
        cam_mats_i = i_mats
        break


    if cam_mats_i is not None:
        view = mats_store.view[cam_mats_i]
        proj = mats_store.proj[cam_mats_i]
        renderer.set_camera(view=view, proj=proj)
        
    renderer.begin_frame()

