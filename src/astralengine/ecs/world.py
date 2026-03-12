from __future__ import annotations

from typing import Any

from astralengine.ecs.command_buffer import CommandBuffer
from astralengine.ecs.entity_allocator import EntityAllocator, EntityId
from astralengine.ecs.resources import ResourceRegistry
from astralengine.ecs.scheduler import SystemScheduler
from astralengine.ecs.store_registry import StoreRegistry
from astralengine.ecs.tag_store import TagStore


class ECSWorld:
    """
    Central ECS façade.

    Owns:
    - entity allocation
    - component stores
    - tag stores
    - global resources
    - scheduler
    - optional command buffer
    """

    def __init__(
        self,
        entity_capacity: int,
        *,
        enable_command_buffer: bool = True,
    ) -> None:
        self.entity_capacity = int(entity_capacity)

        self.entities = EntityAllocator(entity_capacity=self.entity_capacity)
        self._stores = StoreRegistry()
        self._tag_stores: dict[type, TagStore] = {}

        self.resources = ResourceRegistry()
        self.scheduler = SystemScheduler()

        self.command_buffer: CommandBuffer | None = (
            CommandBuffer(self) if enable_command_buffer else None
        )

        self.dt_seconds: float = 0.0

    # ------------------------------------------------------------------
    # Entity lifecycle
    # ------------------------------------------------------------------

    def create_entity(self) -> EntityId:
        return self.entities.create()

    def destroy_entity(self, eid: EntityId) -> None:
        for store in self._stores.values():
            store.remove(eid)

        for tag_store in self._tag_stores.values():
            tag_store.remove(eid)

        self.entities.destroy(eid)

    def entity_exists(self, eid: EntityId) -> bool:
        return self.entities.is_alive(eid)

    # ------------------------------------------------------------------
    # Component stores
    # ------------------------------------------------------------------

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

    def add_component(self, eid: EntityId, component: Any) -> None:
        component_type = type(component)
        self.store(component_type).add(eid, component)

    def remove_component(self, eid: EntityId, component_type: type) -> None:
        self.store(component_type).remove(eid)

    def has_component(self, eid: EntityId, component_type: type) -> bool:
        return self.store(component_type).has(eid)

    # ------------------------------------------------------------------
    # Tag stores
    # ------------------------------------------------------------------

    def register_tag_store(self, tag_type: type) -> None:
        self._tag_stores[tag_type] = TagStore(entity_capacity=self.entity_capacity)

    def has_tag_store(self, tag_type: type) -> bool:
        return tag_type in self._tag_stores

    def tag_store(self, tag_type: type) -> TagStore:
        try:
            return self._tag_stores[tag_type]
        except KeyError as exc:
            raise KeyError(f"No registered tag store for {tag_type}") from exc

    def add_tag(self, eid: EntityId, tag_type: type) -> None:
        self.tag_store(tag_type).add(eid)

    def remove_tag(self, eid: EntityId, tag_type: type) -> None:
        self.tag_store(tag_type).remove(eid)

    def has_tag(self, eid: EntityId, tag_type: type) -> bool:
        return self.tag_store(tag_type).has(eid)

    # ------------------------------------------------------------------
    # Bulk helpers
    # ------------------------------------------------------------------

    def remove_all_components(self, eid: EntityId) -> None:
        for store in self._stores.values():
            store.remove(eid)

    def remove_all_tags(self, eid: EntityId) -> None:
        for tag_store in self._tag_stores.values():
            tag_store.remove(eid)

    # ------------------------------------------------------------------
    # Frame/update
    # ------------------------------------------------------------------

    def run_frame(self, dt: float) -> None:
        self.dt_seconds = float(dt)
        self.scheduler.run(self)

        if self.command_buffer is not None:
            self.command_buffer.flush()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        return {
            "entity_capacity": self.entity_capacity,
            "component_stores": {
                getattr(component_type, "__name__", repr(component_type)): store.stats()
                for component_type, store in self._stores.items()
            },
            "tag_stores": {
                getattr(tag_type, "__name__", repr(tag_type)): tag_store.stats()
                for tag_type, tag_store in self._tag_stores.items()
            },
        }
    
    # ------------------------------------------------------------------
    # Deferred operations (CommandBuffer helpers)
    # ------------------------------------------------------------------

    def defer_add_component(self, eid: EntityId, component: Any) -> None:
        if self.command_buffer is None:
            self.add_component(eid, component)
        else:
            self.command_buffer.add_component(eid, component)

    def defer_remove_component(self, eid: EntityId, component_type: type) -> None:
        if self.command_buffer is None:
            self.remove_component(eid, component_type)
        else:
            self.command_buffer.remove_component(eid, component_type)

    def defer_add_tag(self, eid: EntityId, tag_type: type) -> None:
        if self.command_buffer is None:
            self.add_tag(eid, tag_type)
        else:
            self.command_buffer.add_tag(eid, tag_type)

    def defer_remove_tag(self, eid: EntityId, tag_type: type) -> None:
        if self.command_buffer is None:
            self.remove_tag(eid, tag_type)
        else:
            self.command_buffer.remove_tag(eid, tag_type)

    def defer_destroy_entity(self, eid: EntityId) -> None:
        if self.command_buffer is None:
            self.destroy_entity(eid)
        else:
            self.command_buffer.destroy_entity(eid)    