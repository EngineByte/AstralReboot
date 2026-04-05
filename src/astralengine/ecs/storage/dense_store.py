from __future__ import annotations

class DenseStore:
    '''
    Dense component storage using sparse-set layout.
    
    Structure:
        dense: [component, component, ...]
        entities: [entityhandle, entityhandle, ...]
        sparse: [entityhandle -> dense_index]
    
    Properties:
        - O(1) add
        - O(1) remove
        - O(1) lookup
        - cache-friendly iteration
    '''
    
    __slots__ = (
        '_dense',
        '_entities',
        '_sparse',
    )
    
    def __init__(self) -> None:
        self._dense: list[object] = []
        self._entities: list[int] = []
        self._sparse: dict[int, int] = {}
        
    def add(self, entity: int, component: object) -> None:
        '''
        Add or replace a component for an entity.
        '''
        if entity in self._sparse:
            idx = self._sparse[entity]
            self._dense[idx] = component
            return
        
        idx = len(self._dense)
        self._dense.append(component)
        self._entities.append(entity)
        self._sparse[entity] = idx
        
    def remove(self, entity: int) -> None:
        '''
        Remove a component for an entity.
        
        uses a swap-remove for O(1) removal.
        '''
        
        idx = self._sparse[entity]
        if idx is None:
            return
        
        last_idx = len(self._dense) - 1
        last_entity = self._entities[last_idx]
        
        self._dense[idx] = self._dense[last_idx]
        self._entities[idx] = last_entity
        self._sparse[last_entity] = idx

        self._dense.pop()
        self._entities.pop()
        del self._sparse[entity]
        
    def get(self, entity: int) -> object | None:
        '''
        Returns component for entity, or none if none present.
        '''        
        
        idx = self._sparse.get(entity)
        if idx is None:
            return None
        
        return self._dense[idx]

    def has(self, entity: int) -> bool:
        '''
        True if entity has component.
        '''
        
        return entity in self._sparse
    
    def items(self) -> tuple[tuple[int, object], ...]:
        '''
        Returns (entity, component) pairs.
        '''
        
        return tuple(zip(self._entities, self._dense))
    
    def entities(self) -> tuple[int, ...]:
        '''
        Returns all entities in this store.
        '''
        
        return tuple(self._entities)
    
    def values(self) -> tuple[object, ...]:
        '''
        Returns all components.
        '''
        
        return tuple(self._dense)
    
    def clear(self) -> None:
        '''
        Removes all components.
        '''
        
        self._dense.clear()
        self._entities.clear()
        self._sparse.clear()
        
    def __len__(self) -> int:
        return len(self._dense)
    
    def __contains__(self, entity: int) -> bool:
        return entity in self._sparse
    
    def summary(self) -> str:
        return f'DenseStore(size={len(self._dense)})'