from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


Mat4 = npt.NDArray[np.float32]


@dataclass(slots=True)
class MeshDrawCommand:
    mesh_id: int
    model: Mat4
    material_name: str = "chunk_opaque"


@dataclass(slots=True)
class SkyboxDrawCommand:
    cubemap_asset_id: str
    exposure: float = 1.0


@dataclass(slots=True)
class DebugLineCommand:
    points: npt.NDArray[np.float32]