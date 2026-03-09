from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Tuple, Type, TYPE_CHECKING

from ecs.entity_allocator import EntityId

if TYPE_CHECKING:
    from ecs.world import ECSWorld
    

@dataclass(slots=True)
class _AddComponent:
    eid: EntityId
    component: Any


@dataclass(slots=True)
class _RemoveComponent:
    eid: EntityId
    component_type: Type[Any]


@dataclass(slots=True)
class _AddTag:
    eid: EntityId
    tag_type: Type[Any]


@dataclass(slots=True)
class _RemoveTag:
    eid: EntityId
    tag_type: Type[Any]


@dataclass(slots=True)
class _DestroyEntity:
    eid: EntityId


class CommandBuffer:
    def __init__(self) -> None:
        self._add_components: List[_AddComponent] = []
        self._remove_components: List[_RemoveComponent] = []
        self._add_tags: List[_AddTag] = []
        self._remove_tags: List[_RemoveTag] = []
        self._destroy_entities: List[_DestroyEntity] = []

        self._flushing: bool = False

    def add_component(self, eid: EntityId, component: Any) -> None:
        self._add_components.append(_AddComponent(eid=eid, component=component))

    def remove_component(self, eid: EntityId, component_type: Type[Any]) -> None:
        self._remove_components.append(_RemoveComponent(eid=eid, component_type=component_type))

    def add_tag(self, eid: EntityId, tag_type: Type[Any]) -> None:
        self._add_tags.append(_AddTag(eid=eid, tag_type=tag_type))

    def remove_tag(self, eid: EntityId, tag_type: Type[Any]) -> None:
        self._remove_tags.append(_RemoveTag(eid=eid, tag_type=tag_type))

    def destroy_entity(self, eid: EntityId) -> None:
        self._destroy_entities.append(_DestroyEntity(eid=eid))

    def flush(self, world: 'ECSWorld') -> None:
        if self._flushing:
            raise RuntimeError('CommandBuffer.flush() re-entered')
        self._flushing = True
        try:
            for cmd in self._remove_components:
                if world.is_alive(cmd.eid):
                    world.remove_component(cmd.eid, cmd.component_type)

            for cmd in self._remove_tags:
                if world.is_alive(cmd.eid):
                    world.remove_tag(cmd.eid, cmd.tag_type)

            for cmd in self._add_components:
                if world.is_alive(cmd.eid):
                    world.add_component(cmd.eid, cmd.component)

            for cmd in self._add_tags:
                if world.is_alive(cmd.eid):
                    world.add_tag(cmd.eid, cmd.tag_type)

            for cmd in self._destroy_entities:
                if world.is_alive(cmd.eid):
                    world.destroy_entity(cmd.eid)

        finally:
            self.clear()
            self._flushing = False

    def clear(self) -> None:
        self._add_components.clear()
        self._remove_components.clear()
        self._add_tags.clear()
        self._remove_tags.clear()
        self._destroy_entities.clear()

    def stats(self) -> dict:
        return {
            'add_components': len(self._add_components),
            'remove_components': len(self._remove_components),
            'add_tags': len(self._add_tags),
            'remove_tags': len(self._remove_tags),
            'destroy_entities': len(self._destroy_entities),
        }