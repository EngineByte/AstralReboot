from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChunkResidency:
    active: bool
    resident: bool
    visible: bool
    pinned: bool