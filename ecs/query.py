from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Iterator, List, Sequence, Tuple, Type, TYPE_CHECKING

from ecs.entity_allocator import EntityId
from ecs.tag_store import TagStore

if TYPE_CHECKING:
    from ecs.world import ECSWorld

@dataclass(slots=True, frozen=True)
class QuerySpec:
    include: Tuple[Type[Any], ...]


class Query:
    def __init__(self, world: "ECSWorld", include: Sequence[Type[Any]]) -> None:
        if not include:
            raise ValueError("Query(include=...) must contain at least one type")

        self._world = world
        self._spec = QuerySpec(include=tuple(include))

        comp_types: List[Type[Any]] = []
        tag_types: List[Type[Any]] = []
        comp_stores: List[Any] = []
        tag_stores: List[TagStore] = []

        for t in self._spec.include:
            s = world.stores.get(t)  
            if isinstance(s, TagStore):
                tag_types.append(t)
                tag_stores.append(s)
            else:
                comp_types.append(t)
                comp_stores.append(s)

        self._comp_types = tuple(comp_types)
        self._tag_types = tuple(tag_types)
        self._comp_stores = tuple(comp_stores)
        self._tag_stores = tuple(tag_stores)

        drive_store: Any = None
        drive_dense_eids: Any = None
        drive_size: int = 0

        candidates: List[Tuple[int, Any]] = []
        for s in self._comp_stores:
            candidates.append((int(s.dense_size()), s))
        for s in self._tag_stores:
            candidates.append((int(s.dense_size()), s))

        candidates.sort(key=lambda x: x[0])
        drive_size, drive_store = candidates[0]
        drive_dense_eids = drive_store.dense_eids().copy()

        self._drive_store = drive_store
        self._drive_eids = drive_dense_eids

    def __iter__(self) -> Iterator[Tuple[EntityId, ...]]:
        comp_stores = self._comp_stores
        tag_stores = self._tag_stores

        for raw in self._drive_eids:
            eid = EntityId(raw)

            ok = True
            for s in comp_stores:
                if not s.has(eid):
                    ok = False
                    break
            if not ok:
                continue

            for ts in tag_stores:
                if not ts.has(eid):
                    ok = False
                    break
            if not ok:
                continue

            idxs = [s.dense_index(eid) for s in comp_stores]
            yield (eid, *idxs)

    @property
    def component_types(self) -> Tuple[Type[Any], ...]:
        return self._comp_types

    @property
    def tag_types(self) -> Tuple[Type[Any], ...]:
        return self._tag_types

    @property
    def component_stores(self) -> Tuple[Any, ...]:
        return self._comp_stores

    @property
    def tag_stores(self) -> Tuple[TagStore, ...]:
        return self._tag_stores