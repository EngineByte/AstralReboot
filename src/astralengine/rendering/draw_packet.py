from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


Mat4 = npt.NDArray[np.float32]


@dataclass(slots=True)
class DrawPacket:
    '''
    Render-facing extracted draw data for one visible entity.
    '''
    entity: int
    mesh_id: str
    material_id: str | None
    shader_id: str | None
    model_matrix: Mat4