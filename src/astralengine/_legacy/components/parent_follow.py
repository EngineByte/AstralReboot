from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParentFollow:
    parent_eid: int
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0)
    follow_position: bool = True
    follow_rotation: bool = True