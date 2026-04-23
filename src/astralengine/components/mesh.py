from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Mesh:
    '''
    ECS component linking an entity to renderable mesh/material/shader IDs.
    '''
    mesh_id: str
    material_id: str | None = None
    shader_id: str | None = None
    visible: bool = True