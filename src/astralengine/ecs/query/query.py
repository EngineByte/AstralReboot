from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from astralengine.ecs.core.entity_allocator import EntityId


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
    '''
    ECS query over required component types with flag filters.
    
    A Query selects entities with:
        - all required component types
        - specified flag conditions
    
    Iteration yeilds:
        - (entityhandle, (component_0, component_1, ...))
        
    Note:
        - Query chooses the smallest required component store as the driver.
    '''
    
    __slots__ = (
        '_world',
        '_component_types',
        '_with_tags',
        '_without_tags',
    )

    def __init__(self, 
        *, 
        world, 
        component_types: tuple[type, ...] = (),
        with_tags: tuple[type, ...] = (),
        without_tags: tuple[type, ...] = ()
    ) -> None:
        
        self._world = world
        self._component_types = component_types
        self._with_tags = with_tags
        self._without_tags = without_tags
        
    @property
    def component_types(self) -> tuple[type, ...]:
        return self._component_types

    @property
    def with_tags(self) -> tuple[type, ...]:
        return self._with_tags
    
    @property
    def without_tags(self) -> tuple[type, ...]:
        return self._without_tags
    
    def __iter__(self) -> Iterator[tuple[int, tuple[object, ...]]]:
        '''
        Iterate matching entities and their required components.
        '''
        if not self._component_types:
            raise ValueError('Query requires at least one component type.')
        
        driver_store = self._select_driver_store()
        
        if driver_store is None:
            return
            yield
            
        for entity in driver_store.entities():
            if not self._matches_tags(entity):
                continue
            
            components: list[object] = []
            
            matched = True
            
            for component_type in self._component_types:
                store = self._world.stores.get_component_store(component_type)
                
                if store is None or not store.has(entity):
                    matched = False
                    break
                
            if matched:
                yield entity, tuple(components)
    def _select_driver_store(self):
        '''
        Chooses the smallest required component store to use as the query-driver.
        '''
        
        stores = []
        
        for component_type in self._component_types:
            store = self._world.stores.get_component_store(component_type)
            
            if store is None:
                return None
            
            stores.append(store)
            
        return min(stores, key=len)
    
    def _matches_tags(self, entity: int) -> bool:
        '''
        Return True if the entity satisfies tag filters.
        '''            
        
        for tag_type in self._with_tags:
            store = self._world.stores.get_tag_store(tag_type)
            
            if store is None or not store.has(entity):
                return False
            
        for tag_type in self._without_tags:
            store = self._world.stores.get_tag_store(tag_type)
            
            if store is not None and store.has(entity):
                return False
            
        return True
    
    def count(self) -> int:
        '''
        Count matching entities by iterating the query.
        '''
        
        return sum(1 for _ in self)
    
    def first(self) -> tuple[int, tuple[object, ...]] | None:
        '''
        Return the first match, or None if there are no matches.
        '''
        
        for item in self:
            return item
        
        return None
    
    def summary(self) -> str:
        '''
        Returns a brief readable summary of the query definition.
        '''

        component_names = [t.__name__ for t in self._component_types]
        with_tag_names = [t.__name__ for t in self._with_tags]
        without_tag_names = [t.__name__ for t in self._without_tags]
        
        return (
            'Query('
            f'components={component_names}, '
            f'with_tags={with_tag_names}, '
            f'without_tags={without_tag_names}'
            ')'
        )
    
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