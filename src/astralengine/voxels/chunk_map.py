from __future__ import annotations

from typing import Iterator

from astralengine.ecs.entity_allocator import EntityId


ChunkCoord = tuple[int, int, int]


class ChunkMap:
    """
    Maps chunk grid coordinates to ECS entity IDs.

    This is intentionally lightweight:
    - fast coord -> entity lookup
    - reverse entity -> coord lookup
    - simple neighborhood queries

    It does not own chunk data itself; it only tracks chunk identity/location.
    """

    def __init__(self) -> None:
        self._coord_to_eid: dict[ChunkCoord, EntityId] = {}
        self._eid_to_coord: dict[EntityId, ChunkCoord] = {}

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def bind(self, coord: ChunkCoord, eid: EntityId) -> None:
        """
        Bind a chunk coordinate to an entity.

        Raises:
            ValueError:
                If the coord is already bound to a different entity, or
                the entity is already bound to a different coord.
        """
        existing_eid = self._coord_to_eid.get(coord)
        if existing_eid is not None and existing_eid != eid:
            raise ValueError(
                f"Chunk coord {coord} already bound to eid={int(existing_eid)}"
            )

        existing_coord = self._eid_to_coord.get(eid)
        if existing_coord is not None and existing_coord != coord:
            raise ValueError(
                f"Entity eid={int(eid)} already bound to coord={existing_coord}"
            )

        self._coord_to_eid[coord] = eid
        self._eid_to_coord[eid] = coord

    def unbind_coord(self, coord: ChunkCoord) -> EntityId | None:
        """
        Remove binding by coord and return the removed entity if present.
        """
        eid = self._coord_to_eid.pop(coord, None)
        if eid is not None:
            self._eid_to_coord.pop(eid, None)
        return eid

    def unbind_entity(self, eid: EntityId) -> ChunkCoord | None:
        """
        Remove binding by entity and return the removed coord if present.
        """
        coord = self._eid_to_coord.pop(eid, None)
        if coord is not None:
            self._coord_to_eid.pop(coord, None)
        return coord

    def clear(self) -> None:
        self._coord_to_eid.clear()
        self._eid_to_coord.clear()

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, coord: ChunkCoord) -> EntityId | None:
        return self._coord_to_eid.get(coord)

    def get_coord(self, eid: EntityId) -> ChunkCoord | None:
        return self._eid_to_coord.get(eid)

    def require(self, coord: ChunkCoord) -> EntityId:
        try:
            return self._coord_to_eid[coord]
        except KeyError as exc:
            raise KeyError(f"No chunk bound at coord={coord}") from exc

    def require_coord(self, eid: EntityId) -> ChunkCoord:
        try:
            return self._eid_to_coord[eid]
        except KeyError as exc:
            raise KeyError(f"Entity eid={int(eid)} is not bound in ChunkMap") from exc

    def has_coord(self, coord: ChunkCoord) -> bool:
        return coord in self._coord_to_eid

    def has_entity(self, eid: EntityId) -> bool:
        return eid in self._eid_to_coord

    # ------------------------------------------------------------------
    # Neighborhood helpers
    # ------------------------------------------------------------------

    def neighbors6(self, coord: ChunkCoord) -> tuple[ChunkCoord, ...]:
        x, y, z = coord
        return (
            (x + 1, y, z),
            (x - 1, y, z),
            (x, y + 1, z),
            (x, y - 1, z),
            (x, y, z + 1),
            (x, y, z - 1),
        )

    def iter_neighbor_entities6(
        self,
        coord: ChunkCoord,
    ) -> Iterator[tuple[ChunkCoord, EntityId]]:
        for ncoord in self.neighbors6(coord):
            eid = self._coord_to_eid.get(ncoord)
            if eid is not None:
                yield ncoord, eid

    # ------------------------------------------------------------------
    # Iteration / diagnostics
    # ------------------------------------------------------------------

    def coords(self) -> Iterator[ChunkCoord]:
        return iter(self._coord_to_eid.keys())

    def entities(self) -> Iterator[EntityId]:
        return iter(self._coord_to_eid.values())

    def items(self) -> Iterator[tuple[ChunkCoord, EntityId]]:
        return iter(self._coord_to_eid.items())

    def __contains__(self, coord: object) -> bool:
        return isinstance(coord, tuple) and coord in self._coord_to_eid

    def __len__(self) -> int:
        return len(self._coord_to_eid)

    def stats(self) -> dict[str, int]:
        return {
            "chunk_count": len(self._coord_to_eid),
        }