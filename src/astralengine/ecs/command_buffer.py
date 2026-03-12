from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from astralengine.ecs.entity_allocator import EntityId


@dataclass(slots=True)
class _QueuedCommand:
    fn: Callable[[], None]
    label: str = ""


class CommandBuffer:
    """
    Deferred ECS mutation buffer.

    Use this when systems should not mutate the world immediately while queries
    are in progress. Commands are recorded during update and applied at the end
    of the frame via `flush()`.

    Supported deferred operations:
    - create entity
    - destroy entity
    - add/remove component
    - add/remove tag
    - custom callback
    """

    def __init__(self, world: Any) -> None:
        self.world = world
        self._commands: list[_QueuedCommand] = []
        self._is_flushing: bool = False

    def __len__(self) -> int:
        return len(self._commands)

    def is_empty(self) -> bool:
        return len(self._commands) == 0

    def clear(self) -> None:
        self._commands.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "queued_commands": len(self._commands),
            "is_flushing": self._is_flushing,
        }

    def queue(self, fn: Callable[[], None], *, label: str = "") -> None:
        self._commands.append(_QueuedCommand(fn=fn, label=label))

    def create_entity(self) -> EntityId:
        """
        Create an entity immediately and return the eid, while still allowing
        its components/tags to be added later through deferred commands.

        This mirrors a common ECS pattern: reserve identity now, mutate later.
        """
        return self.world.create_entity()

    def destroy_entity(self, eid: EntityId) -> None:
        self.queue(
            lambda eid=eid: self.world.destroy_entity(eid),
            label=f"destroy_entity({int(eid)})",
        )

    def add_component(self, eid: EntityId, component: Any) -> None:
        self.queue(
            lambda eid=eid, component=component: self.world.add_component(eid, component),
            label=f"add_component({int(eid)}, {type(component).__name__})",
        )

    def remove_component(self, eid: EntityId, component_type: type) -> None:
        self.queue(
            lambda eid=eid, component_type=component_type: self.world.remove_component(
                eid, component_type
            ),
            label=f"remove_component({int(eid)}, {component_type.__name__})",
        )

    def add_tag(self, eid: EntityId, tag_type: type) -> None:
        self.queue(
            lambda eid=eid, tag_type=tag_type: self.world.add_tag(eid, tag_type),
            label=f"add_tag({int(eid)}, {tag_type.__name__})",
        )

    def remove_tag(self, eid: EntityId, tag_type: type) -> None:
        self.queue(
            lambda eid=eid, tag_type=tag_type: self.world.remove_tag(eid, tag_type),
            label=f"remove_tag({int(eid)}, {tag_type.__name__})",
        )

    def custom(self, fn: Callable[[], None], *, label: str = "") -> None:
        self.queue(fn, label=label or "custom")

    def flush(self) -> None:
        """
        Execute all queued commands in FIFO order.

        Commands queued during flush are deferred to the next pass through the
        while-loop, allowing chained command generation in a controlled way.
        """
        if self._is_flushing:
            raise RuntimeError("CommandBuffer.flush() called re-entrantly.")

        self._is_flushing = True
        try:
            while self._commands:
                batch = self._commands
                self._commands = []

                for cmd in batch:
                    cmd.fn()
        finally:
            self._is_flushing = False