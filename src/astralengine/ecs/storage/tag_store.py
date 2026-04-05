from __future__ import annotations

from typing import Any, Dict

import numpy as np
import numpy.typing as npt

from astralengine.ecs.core.entity_allocator import EntityId, entity_index


class TagStore:
    '''
    Dense storage for ECS tags.
    
    A tag store is similar to a component store, but it doesnt store payload data.
    
    Structure:
        entities: [entityhandle, entityhandle, ...]
        sparse: {entity_id -> dense_index}
        
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
        
        '''
    
    def entities(self) -> tuple[int, ...]:
        '''
        
        '''
    
    def clear(self) -> None:
        '''
        
        '''
    
    def __len__(self) -> int:
        '''
        
        '''
    
    def __contains__(self, entity: int) -> bool:
        '''
        
        '''
    
    def summary(self) -> str:
        '''
        
        '''