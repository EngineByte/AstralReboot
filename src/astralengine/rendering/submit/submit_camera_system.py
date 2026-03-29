from __future__ import annotations

from astralengine.components.camera import Camera
from astralengine.components.transform import Transform
from astralengine.components.camera_matrices import CameraMatrices
from astralengine.components.tags import ActiveCamera
from astralengine.ecs.query.query import Query
from astralengine.ecs.core.world import ECSWorld
from astralengine.rendering.renderer import Renderer
from astralengine.resources.render_settings import RenderSettings
from astralengine.stores.camera_matrices_store import CameraMatricesStore
from astralengine.stores.transform_store import TransformStore


def system_submit_camera(world: ECSWorld, dt: float) -> None:
    _ = dt

    renderer = world.resources.get(Renderer)
    settings = world.resources.get(RenderSettings)

    renderer.begin_frame()

    renderer.ctx.viewport_width = settings.viewport_width
    renderer.ctx.viewport_height = settings.viewport_height

    mats_store: CameraMatricesStore = world.store(CameraMatrices)
    tr_store: TransformStore = world.store(Transform)

    chosen_i_mats: int | None = None
    chosen_pos: tuple[float, float, float] | None = None

    for eid, i_cam, i_mats in Query(world, (Camera, CameraMatrices, ActiveCamera)):
        chosen_i_mats = i_mats
        i_tr = tr_store.dense_index(eid)
        chosen_pos = (
            float(tr_store.px[i_tr]),
            float(tr_store.py[i_tr]),
            float(tr_store.pz[i_tr]),
        )
        break

    if chosen_i_mats is None:
        for eid, i_cam, i_mats in Query(world, (Camera, CameraMatrices)):
            chosen_i_mats = i_mats
            i_tr = tr_store.dense_index(eid)
            chosen_pos = (
                float(tr_store.px[i_tr]),
                float(tr_store.py[i_tr]),
                float(tr_store.pz[i_tr]),
            )
            break

    if chosen_i_mats is None:
        return

    renderer.ctx.view = mats_store.view[chosen_i_mats]
    renderer.ctx.proj = mats_store.proj[chosen_i_mats]
    renderer.ctx.camera_pos = chosen_pos if chosen_pos is not None else (0.0, 0.0, 0.0)