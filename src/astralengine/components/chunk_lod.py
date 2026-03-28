from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChunkLOD:
    level: int
    target_level: int
    render_scale_cm: int