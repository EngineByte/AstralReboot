from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from astralengine.ecs.core.entity import EntityId


@dataclass(frozen=True, slots=True)
class AddComponentCommand:
    entity: int
    component: object


@dataclass(frozen=True, slots=True)
class RemoveComponentCommand:
    entity: int
    component_type: type


@dataclass(frozen=True, slots=True)
class AddTagCommand:
    entity: int
    tag_type: type


@dataclass(frozen=True, slots=True)
class RemoveTagCommand:
    entity: int
    tag_type: type


class CommandBuffer:
    '''
    Deferred ECS mutation buffer.

    Responsibilities
        - queue entity creation and destruction
        - queue component add/remove operations
        - queue tag add/remove operations
        - issue temporary placeholder entity IDs for deferred creates
        - resolve placeholder entity IDs are negative integers reserved by this buffer. 

    Notes
        - Only deals with ECS structural mutations.
        - In-place component data mutation should happen directly in systems.
        - Placeholder entity IDs are negative integers reserved by this buffer.
    '''

    __slots__ = (
        '_next_placeholder',
        '_create_entities',
        '_destroy_entities',
        '_add_components',
        '_remove_components',
        '_add_tags',
        '_remove_tags'
    )

    def __init__(self) -> None:
        self._next_placeholder: int = -1
        self._create_entities: list[int] = []
        self._destroy_entities: list[int] = []
        self._add_componenets: list[AddComponentCommand] = []
        self._remove_components: list[RemoveComponentCommand] = []
        self._add_tags: list[AddTagCommand] = []
        self._remove_tags: list[RemoveTagCommand] = []
        
    def defer_create(self) -> int:
        '''
        Queue entity creation and return a placeholder entity handle.

        Placeholder handles are negative integers unique within the current buffer.
        These are resolved to real handles during resolve_creates() 
        '''

        placeholder = self._next_placeholder
        self._next_placeholder -= 1
        self._create_entities.append(placeholder)

        return placeholder

        
    def defer_destroy(self, entity: int) -> None:
        '''
        Queue entity destruction.
        '''

        self._destroy_entities.append(entity)
        
    def defer_add_component(self, entity: int, component: object) -> None:
        '''
        Queue component addition.
        '''
        
        self._add_componenets.append(
            AddComponentCommand(entity=entity, component=component)
        )
        
    def defer_remove_component(self, entity: int, component_type: type) -> None:
        '''
        Queue component removal.
        '''
        self._remove_components.append(
            RemoveComponentCommand(entity=entity, component_type=component_type)
        )
        
    def defer_add_tag(self, entity: int, tag_type: type) -> None:
        '''
        Queue tag addition.
        '''
        self._add_tags.append(
            AddTagCommand(entity=entity, tag_type=tag_type)
        )
        
    def defer_remove_tag(self, entity: int, tag_type: type) -> None:
        '''
        Queue tag removal.
        '''
        self._remove_tags.append(
            RemoveTagCommand(entity=entity, tag_type=tag_type)
        )

    def has_pending(self) -> bool:
        '''
        True if any deferred commands are queued.
        '''

        return bool(
            self._create_entities
            or self._destroy_entities
            or self._add_componenets
            or self._remove_components
            or self._add_tags
            or self._remove_tags
        )

    def summary(self) -> str:
        '''
        Return a compact summary of queued command counts.
        '''

        return (
            'CommandBuffer('
            f'creates={len(self._create_entities)}'
            f'destroys={len(self._destroy_entities)}'
            f'add_components{len(self._add_componenets)}'
            f'remove_components{len(self._remove_components)}'
            f'add_tags{len(self._add_tags)}'
            f'remove_tags={len(self._remove_tags)}'
            ')'
        )

    def __len__(self) -> int:
        '''
        Total number of queued commands.
        '''
        return (
            len(self._create_entities)
            + len(self._destroy_entities)
            + len(self._add_componenets)
            + len(self._remove_components)
            + len(self._add_tags)
            + len(self._remove_tags)
        )
    
    def resolve_creates(self, create_entity_fn: Callable[[], int]) -> dict[int, int]:
        '''
        Resolves all deferred placeholder entity handles into real entity handles.
        
        Parameters:
            create_entity_fn:
                Callable that immediately creates and returns a real entity handle.
            
        Returns:
            Mapping from placeholder entity handles to real entity handles.
        '''

        placeholder_map: dict[int, int] = {}

        for placeholder in self._create_entities:
            real_entity = create_entity_fn()
            placeholder_map[placeholder] = real_entity

        return placeholder_map

    def clear(self) -> None:
        '''
        Clear all queued commands and reset placeholder allocation.
        '''
        
        self._next_placeholder = -1
        self._create_entities.clear()
        self._destroy_entities.clear()
        self._add_componenets.clear()
        self._remove_components.clear()
        self._add_tags.clear()
        self._remove_tags.clear()

    @property
    def create_entities(self) -> tuple[int, ...]:
        '''
        Return queued placeholder entity handles for deferred creation.
        '''

        return tuple(self._create_entities)

    @property
    def destroy_entities(self) -> tuple[int, ...]:
        '''
        Return queued entity handles for deferred destruction.
        '''

        return tuple(self._destroy_entities)

    @property
    def add_components(self) -> tuple[tuple[int, type], ...]:
        '''
        Return queued component-add as (entity, component_type) pairs.
        '''
        
        return tuple(
            (cmd.entity, cmd.component_type)
            for cmd in self._add_components
        )

    @property
    def remove_components(self) -> tuple[tuple[int, type], ...]:
        '''
        Return queued component-remove as (entity, component_type) pairs.
        '''

        return tuple(
            (cmd.entity, cmd.component_type)
            for cmd in self._remove_components
        )

    @property
    def add_tags(self) -> tuple[tuple[int, type], ...]:
        '''
        Return queued tag-add commands as (entity, tag_type) pairs.
        '''

        return tuple(
            (cmd.entity, cmd.tag_type)
            for cmd in self._add_tags
        )
    
    @property
    def remove_tags(self) -> tuple[tuple[int, type], ...]:
        '''
        Return queued tag-remove commands as (entity, tag_type) pairs.
        '''

        return tuple(
            (cmd.entity, cmd.tag_type)
            for cmd in self._remove_tags
        )