# ecs/world.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Sequence, Tuple, Type, TypeVar

from ecs.scheduler import SystemScheduler
from ecs.command_buffer import CommandBuffer
from ecs.entity_allocator import EntityAllocator
from ecs.store_registry import StoreRegistry
from ecs.event_bus import EventBus
from ecs.resources import ResourceRegistry

T = TypeVar('T')


class ECSWorld:
    def __init__(
        self,
        allocator: EntityAllocator,
        stores: StoreRegistry,
        scheduler: SystemScheduler,
        command_buffer: CommandBuffer,
        event_bus: EventBus,
        resources: ResourceRegistry,
    ) -> None:
        
        self.allocator = allocator
        self.stores = stores
        self.scheduler = scheduler
        self.command_buffer = command_buffer
        self.event_bus = event_bus
        self.resources = resources

        self.frame_index: int = 0
        self.time_seconds: float = 0.0
        self.dt_seconds: float = 0.0

    def create_entity(self) -> int:
        eid = self.allocator.create()
        return eid

    def destroy_entity(self, eid: int) -> None:
        self._require_alive(eid)
        self.stores.remove_all_components(eid)
        self.allocator.destroy(eid)

    def defer_destroy_entity(self, eid: int) -> None:
        self._require_alive(eid)
        self.command_buffer.destroy_entity(eid)

    def is_alive(self, eid: int) -> bool:
        return self.allocator.is_alive(eid)

    def _require_alive(self, eid: int) -> None:
        if not self.allocator.is_alive(eid):
            raise ValueError(f'Entity {eid} is not alive')

    def register_store(self, component_type: Type[T], store: Any) -> None:
        self.stores.register(component_type, store)

    def store(self, component_type: Type[T]) -> Any:
        return self.stores.get(component_type)

    def add_component(self, eid: int, component: Any) -> None:
        self._require_alive(eid)
        self.stores.add_component(eid, component)

    def defer_add_component(self, eid: int, component: Any) -> None:
        self._require_alive(eid)
        self.command_buffer.add_component(eid, component)

    def remove_component(self, eid: int, component_type: Type[T]) -> None:
        self._require_alive(eid)
        self.stores.remove_component(eid, component_type)

    def defer_remove_component(self, eid: int, component_type: Type[T]) -> None:
        self._require_alive(eid)
        self.command_buffer.remove_component(eid, component_type)

    def has_component(self, eid: int, component_type: Type[T]) -> bool:
        return self.stores.has_component(eid, component_type)

    def get_component(self, eid: int, component_type: Type[T]) -> Any:
        self._require_alive(eid)
        return self.stores.get_component(eid, component_type)

    def add_tag(self, eid: int, tag_type: Type[Any]) -> None:
        self._require_alive(eid)
        self.stores.add_tag(eid, tag_type)

    def defer_add_tag(self, eid: int, tag_type: Type[Any]) -> None:
        self._require_alive(eid)
        self.command_buffer.add_tag(eid, tag_type)

    def remove_tag(self, eid: int, tag_type: Type[Any]) -> None:
        self._require_alive(eid)
        self.stores.remove_tag(eid, tag_type)

    def defer_remove_tag(self, eid: int, tag_type: Type[Any]) -> None:
        self._require_alive(eid)
        self.command_buffer.remove_tag(eid, tag_type)

    def has_tag(self, eid: int, tag_type: Type[Any]) -> bool:
        return self.stores.has_tag(eid, tag_type)

    def query(self, include: Sequence[Type[Any]]) -> Iterator[Tuple[int, Tuple[Any, ...]]]:
        return self.stores.query(include)

    def emit(self, event: Any) -> None:
        self.event_bus.emit(event)

    def on(self, event_type: Type[Any], handler: Callable[[Any], None]) -> None:
        self.event_bus.on(event_type, handler)

    def update(self, dt: float) -> None:
        self.dt_seconds = float(dt)
        self.time_seconds += self.dt_seconds
        self.frame_index += 1

        self.scheduler.run_phase('update', self)
        self.command_buffer.flush(self)

        self.scheduler.run_phase('late_update', self)
        self.command_buffer.flush(self)

        self.event_bus.flush()

    def render(self) -> None:
        self.scheduler.run_phase('pre_render', self)
        self.command_buffer.flush(self)
        
        self.scheduler.run_phase('render', self)
        self.command_buffer.flush(self)        

        self.event_bus.flush()

    def stats(self) -> Dict[str, Any]:
        return {
            'frame': self.frame_index,
            'time': self.time_seconds,
            'dt': self.dt_seconds,
            'entities_alive': self.allocator.alive_count(),
            'stores': self.stores.stats(),
        }