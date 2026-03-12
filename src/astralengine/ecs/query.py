from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from astralengine.ecs.entity_allocator import EntityId


@dataclass(frozen=True, slots=True)
class QuerySpec:
    component_types: tuple[type, ...]
    tag_types: tuple[type, ...]


def _split_query_types(world: Any, query_types: tuple[type, ...]) -> QuerySpec:
    """
    Split requested query types into component-backed types and tag-backed types.
    """
    component_types: list[type] = []
    tag_types: list[type] = []

    for typ in query_types:
        if world.has_store(typ):
            component_types.append(typ)
        elif world.has_tag_store(typ):
            tag_types.append(typ)
        else:
            raise KeyError(
                f"Query type is neither a registered component store nor tag store: {typ}"
            )

    return QuerySpec(
        component_types=tuple(component_types),
        tag_types=tuple(tag_types),
    )


class Query(Iterator[tuple[Any, ...]]):
    """
    Iterate entities matching a component/tag query.

    Yield format:
        (eid, dense_i_component0, dense_i_component1, ...)

    Important:
    - only component-backed types contribute dense indices
    - tag types are membership filters only
    """

    def __init__(self, world: Any, query_types: tuple[type, ...]) -> None:
        self.world = world
        self.query_types = tuple(query_types)

        spec = _split_query_types(world, self.query_types)
        self.component_types = spec.component_types
        self.tag_types = spec.tag_types

        if not self.component_types:
            raise ValueError(
                "Query requires at least one component-backed type as a driving store."
            )

        self.component_stores = [world.store(t) for t in self.component_types]
        self.tag_stores = [world.tag_store(t) for t in self.tag_types]

        # Drive iteration from the smallest component store for efficiency
        self._driver_store = min(self.component_stores, key=lambda s: s.dense_size())
        self._driver_eids = self._driver_store.dense_eids()
        self._cursor = 0

    def __iter__(self) -> "Query":
        return self

    def __next__(self) -> tuple[Any, ...]:
        while self._cursor < len(self._driver_eids):
            eid = EntityId(self._driver_eids[self._cursor])
            self._cursor += 1

            # Check all component stores
            dense_indices: list[int] = []
            component_ok = True

            for store in self.component_stores:
                if not store.has(eid):
                    component_ok = False
                    break
                dense_indices.append(store.dense_index(eid))

            if not component_ok:
                continue

            # Check all tag stores
            tag_ok = True
            for tag_store in self.tag_stores:
                if not tag_store.has(eid):
                    tag_ok = False
                    break

            if not tag_ok:
                continue

            return (eid, *dense_indices)

        raise StopIteration