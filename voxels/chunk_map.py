from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from ecs.entity_allocator import EntityId


ChunkCoord = Tuple[int, int, int]


class ChunkMap:
    def __init__(self) -> None:
        self._coord_to_eid: Dict[ChunkCoord, EntityId] = {}

    def set(self, coord: ChunkCoord, eid: EntityId) -> None:
        self._coord_to_eid[coord] = eid

    def get(self, coord: ChunkCoord) -> EntityId | None:
        return self._coord_to_eid.get(coord)

    def remove(self, coord: ChunkCoord) -> None:
        self._coord_to_eid.pop(coord, None)

    def items(self):
        return self._coord_to_eid.items()