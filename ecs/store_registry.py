from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Sequence, Tuple, Type

from ecs.entity_allocator import EntityId

from ecs.soa_store import SoAStore
from ecs.tag_store import TagStore


class StoreRegistry:
    def __init__(self) -> None:
        self._component_stores: Dict[Type[Any], Any] = {}
        self._tag_stores: Dict[Type[Any], TagStore] = {}

    def register(self, typ: Type[Any], store: Any) -> None:
        if isinstance(store, TagStore):
            self._tag_stores[typ] = store
            return
        self._component_stores[typ] = store

    def get(self, typ: Type[Any]) -> Any:
        if typ in self._component_stores:
            return self._component_stores[typ]
        if typ in self._tag_stores:
            return self._tag_stores[typ]
        raise KeyError(f"No store registered for type: {typ}")

    def add_component(self, eid: EntityId, component: Any) -> None:
        typ = type(component)
        store = self._component_stores.get(typ)
        if store is None:
            raise KeyError(f"No component store registered for type: {typ}")
        store.add(eid, component)

    def remove_component(self, eid: EntityId, typ: Type[Any]) -> None:
        store = self._component_stores.get(typ)
        if store is None:
            return
        store.remove(eid)

    def has_component(self, eid: EntityId, typ: Type[Any]) -> bool:
        store = self._component_stores.get(typ)
        if store is None:
            return False
        return bool(store.has(eid))

    def get_component(self, eid: EntityId, typ: Type[Any]) -> Any:
        store = self._component_stores.get(typ)
        if store is None:
            raise KeyError(f"No component store registered for type: {typ}")
        return store

    def add_tag(self, eid: EntityId, tag_type: Type[Any]) -> None:
        store = self._tag_stores.get(tag_type)
        if store is None:
            raise KeyError(f"No tag store registered for type: {tag_type}")
        store.add(eid)

    def remove_tag(self, eid: EntityId, tag_type: Type[Any]) -> None:
        store = self._tag_stores.get(tag_type)
        if store is None:
            return
        store.remove(eid)

    def has_tag(self, eid: EntityId, tag_type: Type[Any]) -> bool:
        store = self._tag_stores.get(tag_type)
        if store is None:
            return False
        return bool(store.has(eid))

    def remove_all_components(self, eid: EntityId) -> None:
        for store in self._component_stores.values():
            store.remove(eid)
        for store in self._tag_stores.values():
            store.remove(eid)

    def query(self, include: Sequence[Type[Any]]) -> Iterator[Tuple[EntityId, Tuple[Any, ...]]]:
        if not include:
            return iter(())

        comp_types: List[Type[Any]] = []
        tag_types: List[Type[Any]] = []

        for t in include:
            if t in self._component_stores:
                comp_types.append(t)
            elif t in self._tag_stores:
                tag_types.append(t)
            else:
                raise KeyError(f"Type not registered as component or tag: {t}")

        drive_store = None
        drive_is_tag = False

        candidates: List[Tuple[int, Any, bool]] = []
        for t in comp_types:
            s = self._component_stores[t]
            candidates.append((int(s.dense_size()), s, False))
        for t in tag_types:
            s = self._tag_stores[t]
            candidates.append((int(s.dense_size()), s, True))

        if not candidates:
            return iter(())

        candidates.sort(key=lambda x: x[0])
        _, drive_store, drive_is_tag = candidates[0]

        drive_eids = drive_store.dense_eids()

        comp_stores = [self._component_stores[t] for t in comp_types]

        def iterator() -> Iterator[Tuple[EntityId, Tuple[Any, ...]]]:
            for raw in drive_eids:
                eid = EntityId(raw)

                ok = True
                for s in comp_stores:
                    if not s.has(eid):
                        ok = False
                        break
                if not ok:
                    continue

                for tt in tag_types:
                    if not self._tag_stores[tt].has(eid):
                        ok = False
                        break
                if not ok:
                    continue

                yield eid, tuple(comp_stores)

        return iterator()

    def stats(self) -> Dict[str, Any]:
        return {
            "components": {t.__name__: s.stats() for t, s in self._component_stores.items()},
            "tags": {t.__name__: s.stats() for t, s in self._tag_stores.items()},
        }