from __future__ import annotations

import numpy as np

from astralengine.components.model_matrix import ModelMatrix
from astralengine.components.tags import DirtyRemodel
from astralengine.components.transform import Transform
from astralengine.ecs.query import Query
from astralengine.ecs.world import ECSWorld
from astralengine.math.transforms import compose_centered_model_matrix
from astralengine.stores.model_matrix_store import ModelMatrixStore
from astralengine.stores.transform_store import TransformStore


def system_update_model_matrices(world: ECSWorld, dt: float) -> None:
    _ = dt

    tr_store: TransformStore = world.store(Transform)
    model_store: ModelMatrixStore = world.store(ModelMatrix)

    for eid, i_tr, i_model in Query(
        world,
        (Transform, ModelMatrix, DirtyRemodel),
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

        scale = np.array(
            [
                tr_store.sx[i_tr],
                tr_store.sy[i_tr],
                tr_store.sz[i_tr],
            ],
            dtype=np.float32,
        )

        centre = np.array(
            [
                model_store.cx[i_model],
                model_store.cy[i_model],
                model_store.cz[i_model],
            ],
            dtype=np.float32,
        )

        model_store.model[i_model] = compose_centered_model_matrix(
            position=position,
            rotation=rotation,
            scale=scale,
            centre=centre,
        )

        world.remove_tag(eid, DirtyRemodel)