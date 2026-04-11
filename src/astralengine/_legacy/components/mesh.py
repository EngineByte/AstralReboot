from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Mesh:
    mesh_id: int