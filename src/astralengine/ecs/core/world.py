from __future__ import annotations

from typing import Any, TypeVar, Iterable
from dataclasses import dataclass

from astralengine.ecs.core.command_buffer import CommandBuffer
from astralengine.ecs.core.entity_allocator import EntityHandle
from astralengine.ecs.query.query import Query
from astralengine.ecs.resources.resource_registry import ResourceRegistry
from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.ecs.storage.store_registry import StoreRegistry
from astralengine.ecs.storage.tag_store import TagStore

T = TypeVar('T')


@dataclass(slots=True)
class WorldStats:
    created_entities: int
    destroyed_entities: int
    alive_entities: int
    component_store_count: int
    tag_store_count: int
    resource_count: int
    pending_commands: int
    
    
class ECSWorld:
    '''
    Central ECS runtime operations

    Owns:
    - entity lifecycle
    - component and tag storage mutations
    - deferred mutation buffering
    - resource storage
    - query entry point
    - debugging and inspection
    
    Rules:
    - entity ids have index and generation combined
    - ecs mutations can be immediate or deferred
    - data values are mutated in place to maintain congruity
    - tags are handled separately from normal component stores
    '''
    
    __slots__ = (
        '_generations',
        '_alive',
        '_free_indices',
        '_stores',
        '_resources',
        '_commands',
        '_created_entities',
        '_destroyed_entities'
    )

    def __init__(self) -> None:
        self._generations: list[int] = []
        self._alive: list[bool] = []
        self._free_indices: list[int] = []
        self._stores = StoreRegistry()
        self._resources = ResourceRegistry()
        self._commands = CommandBuffer()
        self._created_entities = 0
        self._destroyed_entities = 0
        
    def create_entity(self) -> int:
        '''
        Create a new entity immediately and return its entity handle.
        '''
        if self._free_indices:
            index = self._free_indices.pop()
            generate = self._generations[index]
            self._alive[index] = True
        else:
            index = len(self._generations)
            generation = 0
            self._generations.append(generation)
            self._alive.append(True)
            
        self._created_entities += 1
        return EntityHandle.pack(index=index, generation=generation)
    
    def destroy_entity(self, eid: int) -> None:
        '''
        Destroy an entity immediately.
        
        Removes all components and tags assigned to identity, invalidates 
        old references by incrementing generation, and adds the index to
        the free list.
        '''
        self._require_alive(eid)
        index, generation = EntityHandle.unpack(eid)
        
        for store in self._stores.component_stores():
            store.remove(eid)
            
        for store in self._stores.tag_stores():
            store.remove(eid)
            
        self._alive[index] = False
        self._generations[index] += 1
        self._free_indices.append(index)
        
        self._destroyed_entities += 1
        
    def is_alive(self, eid: int) -> bool:
        '''
        True if entity handle is valid and alive.
        '''
        try: 
            index, generation = EntityHandle.unpack(eid)
        except Exception:
            return False
        
        return self._alive[index] and self._generations[index] == generation
    
    def entity_count(self) -> int:
        '''
        Number of living entities.
        '''
        return sum(self._alive)
    
    def capacity(self) -> int:
        '''
        Number of entity slots allocated.
        '''
        return len(self._alive)

    def register_store(self, component_type: type, store: Any) -> None:
        self._stores.register(component_type, store)

    def has_store(self, component_type: type) -> bool:
        return component_type in self._stores._component_stores.keys()

    def store(self, component_type: type) -> Any:
        return self._stores.get(component_type)

    def store_by_type_name(self, type_name: str) -> Any:
        for component_type, store in self._stores.items():
            if getattr(component_type, "__name__", "") == type_name:
                return store
        raise KeyError(f"No registered component store named '{type_name}'")

    def add_component(self, eid: int, component: object) -> None:
        '''
        Add or replace a component for an entity immediately.
        '''
        self._require_alive(eid)
        component_type = type(component)
        store = self._stores.get_or_create_component_store(component_type)
        store.add(eid, component)

    def remove_component(self, eid: int, component_type: type) -> None:
        '''
        Remove a component from an entity immediately.
        '''
        self._require_alive(eid)
        store = self._stores.get_component_store(component_type)
        if store is not None:
            store.remove(eid)

    def has_component(self, eid: int, component_type: type) -> bool:
        '''
        True if entity has component.
        '''
        if not self.is_alive(eid):
            return False
        
        store = self._stores.get_component_store(component_type)
        
        return store is not None and store.has(eid)
    
    def get_component(self, eid: int, component_type: type[T]) -> T:
        '''
        Returns the component instance for an entity.
        
        Raises:
            KeyError if entity does not have component.
        '''
        self._require_alive(eid)
        store = self._stores.get_component_store(component_type)
        
        if store is None or not store.has(eid):
            raise KeyError(f'Entity {eid} does not have component {component_type.__name__}')
        
        return store.get(eid)
    
    def try_get_component(self, eid: int, component_type: type[T]) -> T | None:
        '''
        Returns the component if available, None if entity does not have component.
        '''
        if not self.is_alive(eid):
            return None
        
        store = self._stores.get_component_store(component_type)
        
        if store is None or not store.has(eid):
            return None
        
        return store.get(eid)

    def register_tag_store(self, tag_type: type) -> None:
        self._tag_stores[tag_type] = TagStore(entity_capacity=self.entity_capacity)

    def has_tag_store(self, tag_type: type) -> bool:
        return tag_type in self._tag_stores

    def tag_store(self, tag_type: type) -> TagStore:
        try:
            return self._tag_stores[tag_type]
        except KeyError as exc:
            raise KeyError(f"No registered tag store for {tag_type}") from exc

    def add_tag(self, eid: int, tag_type: type) -> None:
        '''
        Add a tag to entity immediately.
        '''
        self._require_alive(eid)
        
        store = self._stores.get_or_create_tag_store(tag_type)
        store.add(eid)

    def remove_tag(self, eid: int, tag_type: type) -> None:
        '''
        Remove a tag from an entity immediately.
        '''
        self._require_alive(eid)
        store = self._stores.get_tag_store(tag_type)
        if store is not None:
            store.remove(eid)
            
    def has_tag(self, eid: int, tag_type: type) -> bool:
        '''
        True if entity has the tag.
        '''
        if not self.is_alive(eid):
            return False
        
        store = self._stores.get_tag_store(tag_type)
        
        return store is not None and store.has(eid)

    def remove_all_components(self, eid: int) -> None:
        for store in self._stores.values():
            store.remove(eid)

    def remove_all_tags(self, eid: int) -> None:
        for tag_store in self._tag_stores.values():
            tag_store.remove(eid)
            
    def get_all_components(self, eid: int) -> dict[type, object]:
        '''
        Return all components currently attached to an entity.
        '''
        self._require_alive(eid)
        out: dict[type, object] = {}
        for component_type, store in self._stores._component_store_items():
            if store.has(eid):
                out[component_type] = store.get(eid)
                
        return out
    
    def get_all_tags(self, eid: int) -> tuple[type, ...]:
        '''
        Return all tags currently attached to an entity.
        '''
        self._require_alive(eid)
        out: tuple[type] = ()
        for tag_type, store in self._stores._tag_store_items():
            if store.has(eid):
                out.append(tag_type)
                
        return tuple(out)
    
    def entity_dump(self, eid: int) -> dict[str, Any]:
        '''
        Returns a debug-friendly snapshot of a single entity.
        '''
        self._require_alive(eid)
        return {
            'entity': eid,
            'alive': True,
            'components': {
                component_type.__name__: component for component_type, component in self.get_all_components(eid).items()
            },
            'tags': [tag_type.__name__ for tag_type in self.get_all_tags(eid)]
        }

    def run_frame(self, dt: float) -> None:
        self.dt_seconds = float(dt)
        self.scheduler.run(self)

        if self.command_buffer is not None:
            self.command_buffer.flush()

    def stats(self) -> dict[str, Any]:
        return WorldStats(
            created_entities=self._created_entities,
            destroyed_entities=self._destroyed_entities,
            alive_entities=self.entity_count(),
            component_store_count=self._stores.component_store_count(),
            tag_store_count=self._stores.tag_store_count(),
            resource_count=self._resources.count(),
            pending_commands=len(self._commands)
        )
        
    def summary(self) -> str:
        stats = self.stats()
        return (
            'world('
            f'alive={stats.alive_entities}, '
            f'capacity={self.capacity()}, '
            f'created={stats.created_entities}, '
            f'destroyed={stats.destroyed_entites}, '
            f'component_stores={stats.component_store_count}, '
            f'tag_stores={stats.tag_store_count}, '
            f'resources={stats.resource_count}, '
            f'pending_commands={stats.pending_commands}, '
            ')'
        )
    
    def defer_add_component(self, eid: int, component: object) -> None:
        '''
        Queue component to be added to entity.
        '''
        self._commands.defer_add_component(eid, component)
        
    def defer_remove_component(self, eid: int, component_type: type) -> None:
        '''
        Queue component to be removed from entity.
        '''
        self._commands.defer_remove_component(eid, component_type)
        
    def defer_add_tag(self, eid: int, tag_type: type) -> None:
        '''
        Queue tag to be added to entity.
        '''
        self._commands.defer_add_tag(eid, tag_type)
        
    def defer_remove_tag(self, eid: int, tag_type: type) -> None:
        '''
        Queue tag to be removed from entity.
        '''
        self._commands.defer_remove_tag(eid, tag_type)
        
    def defer_destroy_entity(self, eid: int) -> None:
        '''
        Queue entity destruction.
        '''
        self._commands.defer_destroy(eid)
        
    def defer_create_entity(self) -> int:
        '''
        Queue entity creation and return a placeholder entity handle.
        
        Placeholder handle is replaced during apply_commands().
        '''
        return self._commands.defer_create()
    
    def apply_commands(self) -> None:
        '''
        Apply all queued ECS mutations.
        
        Returns a map from temporary placeholder entity handles to final handles.
        '''
        placeholder_map = self._commands.resolve_creates(self.create_entity)
        
        for eid, component in self._commands.add_components:
            real_eid = placeholder_map.get(eid, eid)
            
            if self.is_alive(real_eid):
                self.add_component(real_eid, component)
                
        for eid, tag_type in self._commands.add_tags:
            real_eid = placeholder_map.get(eid, eid)
            
            if self.is_alive(real_eid):
                self.add_tag(real_eid, tag_type)
                
        for eid, component_type in self._commands.remove_components:
            real_eid = placeholder_map.get(eid, eid)
            
            if self.is_alive(real_eid):
                self.remove_component(real_eid, component_type)
                
        for eid, tag_type in self._commands.remove_tags:
            real_eid = placeholder_map.get(eid, eid)
            
            if self.is_alive(real_eid):
                self.remove_tag(real_eid, tag_type)
                
        for eid in self._commands.destroy_entities:
            real_eid = placeholder_map.get(eid, eid)
            
            if self.is_alive(real_eid):
                self.destroy_entity(real_eid)
                
        self._commands.clear()
        
        return placeholder_map
        
    def query(self, 
        component_types: tuple[type, ...], 
        *, 
        with_tags=(), 
        without_tags=()
    ) -> Any:
        '''
        Create a query object for given component types and flags.
        
        Usage example:
            for eid, (Transform, Velocity) in world.query((Transform, Velocity)): ...
        '''
        return Query(
            world=self,
            component_types=component_types,
            with_tags=with_tags,
            without_tags=without_tags
        )
    
    def entity_components(self, eid: int) -> dict[type, object]:
        self._require_alive(eid)
        out: dict[type, object] = {}
        for component_type, store in self._stores.component_store_items():
            if store.has(eid):
                out[component_type] = store.get(eid)
                
        return out
    
    def entity_tags(self, eid: int) -> tuple[type, ...]:
        self._require_alive(eid)
        out: list[type] = []
        for tag_type, store in self._stores.tag_store_items():
            if store.has(eid):
                out.append(tag_type)
                
        return tuple(out)
    
    def entity_dump(self, eid: int) -> dict[str, Any]:
        self._require_alive(eid)
        return {
            'entity': eid,
            'alive': True,
            'components': {
                component_type.__name__: component for component_type, component in self.get_all_components(eid).items()},
            'tags': [tag_type.__name__ for tag_type in self.get_all_tags(eid)]
        }
    
    def summary(self) -> str:
        raise NotImplementedError
    
    def add_resource(self, resource: object, *, resource_type: type | None = None) -> None:
        '''
        Add or replace a global resource.
        '''
        key = resource_type or type(resource)
        self._resources.add(key, resource)
        
    def get_resource(self, resource_type: type[T]) -> T:
        '''
        Returns the resource according to type.
        
        Raises:
            KeyError if no resource found.
        '''
        return self._resources.get(resource_type)
    
    def try_get_resource(self, resource_type: type[T]) -> T | None:
        '''
        Returns a resource if present, None if not present.
        '''
        return self._resources.try_get(resource_type)
    
    def has_resource(self, resource_type: type) -> bool:
        '''
        True if resource available.
        '''
        return self._resources.has(resource_type)
    
    def remove_resource(self, resource_type: type) -> None:
        '''
        Removes the resource from the registry.
        '''
        self._resources.remove(resource_type)
        
    def _require_alive(self, eid: int) -> None:
        ''''''
        if not self.is_alive(eid):
            raise KeyError(f'Invalid or dead entity handle: {eid}')
        
    @property
    def stores(self) -> StoreRegistry:
        return self._stores
    
    @property
    def resources(self) -> ResourceRegistry:
        return self._resources
    
    @property
    def commands(self) -> CommandBuffer:
        return self._commands
    
    def iter_alive_entiteis(self) -> Iterable[int]:
        for index, alive in enumerate(self._alive):
            if alive: 
                yield EntityHandle.pack(index=index, generation=self._generations[index])