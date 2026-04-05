from __future__ import annotations

from typing import Any, Dict, Iterator, List, Sequence, Tuple, Type

from astralengine.ecs.core.entity_allocator import EntityId
from astralengine.ecs.storage.tag_store import TagStore
from astralengine.ecs.storage.dense_store import DenseStore


class StoreRegistry:
    '''
    Registry for ECS component stores and tag stores.
    
    Responsibility:
        - create and retrieve component stores by component type
        - create and retrieve tag stores by tag type
        - expose store iteration for world-level inspection and cleanup
        - report basic registry stats
    '''
    
    __slots__ = (
        '_component_stores',
        '_tag_stores'
    )
    
    def __init__(self) -> None:
        self._component_stores: dict[type, DenseStore] = {}
        self._tag_stores: Dict[Type[Any], TagStore] = {}
    
    def register_component_store(self, component_type: type, store: DenseStore) -> None:
        '''
        Register a component store for a specific component type
        '''
        
        if component_type in self._component_stores:
            raise ValueError(f'Component store already registered for {component_type.__name__}.')
        
        self._component_stores[component_type] = store
        
    def get_component_store(self, component_type: type) -> DenseStore:
        '''
        Returns the component store for the specified type, or None if type not registered.
        '''
        
        return self._component_stores.get(component_type)
    
    def get_or_create_component_store(self, component_type: type) -> DenseStore:
        '''
        Returns the component store for the specified type, or creates and registers on if needed.
        '''
        
        store = self._component_stores.get(component_type)
        
        if store is None:
            store = DenseStore()
            
        self._component_stores[component_type] = store
        
        return store
    
    def has_component_store(self, component_type: type) -> bool:
        '''
        True if component store is registered for the specified type.
        '''
        
        return component_type in self._component_stores
    
    def remove_component_store(self, component_type: type) -> None:
        '''
        De-register and remove a component store.
        
        Raises:
            KeyError: if not store is registered for component type.
        '''
        
        try:
            del self._component_stores[component_type]
        except KeyError as exc:
            raise KeyError(f'No component store registered for {component_type.__name__}.') from exc    
    
    def component_stores(self) -> tuple[DenseStore, ...]:
        '''
        Returns all registered component stores.
        '''
        
        return tuple(self._component_stores.values())
    
    def component_store_items(self) -> tuple[tuple[type, DenseStore], ...]:
        '''
        Returns (component_type, store) pairs for all component stores.
        '''
        
        return tuple(self._component_stores.items())
    
    def component_store_count(self) -> int:
        '''
        Return the number of registered component stores.
        '''
        return len(self._component_stores)
    
    def register_tag_store(self, tag_type: type, store: TagStore) -> None:
        '''
        Register a tag store for a specific tag type
        '''
        
        if tag_type in self._tag_stores:
            raise ValueError(f'Tag store already registered for {tag_type.__name__}.')
        
        self._tag_stores[tag_type] = store
        
    def get_tag_store(self, tag_type: type) -> TagStore:
        '''
        Returns the tag store for the specified type, or None if type not registered.
        '''
        
        return self._tag_stores.get(tag_type)
    
    def get_or_create_tag_store(self, tag_type: type) -> TagStore:
        '''
        Returns the tag store for the specified type, or creates and registers one if needed.
        '''
        
        store = self._tag_stores.get(tag_type)
        
        if store is None:
            store = TagStore()
            
        self._tag_stores[tag_type] = store
        
        return store
    
    def has_tag_store(self, tag_type: type) -> bool:
        '''
        True if tag store is registered for the specified type.
        '''
        
        return tag_type in self._tag_stores
    
    def remove_tag_store(self, tag_type: type) -> None:
        '''
        De-register and remove a tag store.
        
        Raises:
            KeyError: if no store is registered for tag type.
        '''
        
        try:
            del self._tag_stores[tag_type]
        except KeyError as exc:
            raise KeyError(f'No tag store registered for {tag_type.__name__}.') from exc    
    
    def tag_stores(self) -> tuple[TagStore, ...]:
        '''
        Returns all registered tag stores.
        '''
        
        return tuple(self._tag_stores.values())
    
    def tag_store_items(self) -> tuple[tuple[type, TagStore], ...]:
        '''
        Returns (tag_type, store) pairs for all tag stores.
        '''
        
        return tuple(self._tag_stores.items())
    
    def tag_store_count(self) -> int:
        '''
        Return the number of registered tag stores.
        '''
        return len(self._tag_stores)
    
    def clear(self) -> None:
        '''
        Removes all registered component and tag stores from the registry.
        '''
        
        self._component_stores.clear()
        self._tag_stores.clear()
        
    def is_empty(self) -> bool:
        '''
        True if no component or tag stores are registered.
        '''
        
        return not self._component_stores and not self._tag_stores
    
    def summary(self) -> str:
        '''
        Returns a compact readable summary of registry state.
        '''
        
        return (
            'StoreRegistry('
            f'component_stores={len(self._component_stores)}, '
            f'tag_stores={len(self._tag_stores)}'
            ')'
        )
    
    def add_component(self, eid: EntityId, component: Any) -> None:
        typ = type(component)
        store = self._component_stores.get(typ)
        if store is None:
            raise KeyError(f'No component store registered for type: {typ}')
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
            raise KeyError(f'No component store registered for type: {typ}')
        return store

    def add_tag(self, eid: EntityId, tag_type: Type[Any]) -> None:
        store = self._tag_stores.get(tag_type)
        if store is None:
            raise KeyError(f'No tag store registered for type: {tag_type}')
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
                raise KeyError(f'Type not registered as component or tag: {t}')

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
            'components': {t.__name__: s.stats() for t, s in self._component_stores.items()},
            'tags': {t.__name__: s.stats() for t, s in self._tag_stores.items()},
        }