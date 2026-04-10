from __future__ import annotations

from typing import Any, Dict

import numpy as np
import numpy.typing as npt


class TagStore:
    '''
    Dense storage for ECS tags.
    
    A tag store is similar to a component store, but it doesnt store payload data.
    
    Structure:
        entities: [entityhandle, entityhandle, ...]
        sparse: {entity_id -> dense_index}s
        
    Properties:
        - O(1) add
        - O(1) remove
        - O(1) check
        - Cache-friendly iteration
    '''
    
    __slots__ = (
        '_entities',
        '_sparse'
    )
    
    def __init__(self) -> None:
        self._entities: list[int] = []
        self._sparse: dict[int, int] = {}
    
    def add(self, entity: int) -> None:
        '''
        Add the tag to an entity.
        '''
        
        if entity in self._sparse:
            return
        
        idx = len(self._entities)
        self._entities.append(entity)
        self._sparse[entity] = idx
    
    def remove(self, entity: int) -> None:
        '''
        Removes the tag from an entity.
        '''
        
        idx = self._sparse.get(entity)
        if idx is None:
            return
        
        last_idx = len(self._entities) - 1
        last_entity = self._entities[last_idx]
        self._entities[idx] = last_entity
        self._sparse[last_entity] = idx
        self._entities.pop()
        del self._sparse[entity]
    
    def has(self, entity: int) -> bool:
        '''
        True if the entity currently has this tag.
        '''
        
        return entity in self._sparse
    
    def entities(self) -> tuple[int, ...]:
        '''
        Returns all tagged entities.
        '''
        
        return tuple(self._entities)
    
    def clear(self) -> None:
        '''
        Removes all tag assignments.
        '''
        
        self._entities.clear()
        self._sparse.clear()
    
    def __len__(self) -> int:
        '''
        Returns the number of entities holding this flag.
        '''
        
        return len(self._entities)
    
    def summary(self) -> str:
        '''
        Returns a compact readable summary.
        '''
        
        return f'TagStore(size={len(self._entities)})'