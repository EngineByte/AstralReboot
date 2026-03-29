from __future__ import annotations

from typing import Any, TypeVar


T = TypeVar("T")


class ResourceRegistry:
    """
    Registry for singleton-style global resources.

    Resources are stored by concrete type. Typical examples:
    - InputState
    - RenderSettings
    - SkySettings
    - AssetManager
    - Renderer
    - MeshPool

    Example:
        registry.add(RenderSettings())
        settings = registry.get(RenderSettings)
    """

    def __init__(self) -> None:
        self._resources: dict[type, Any] = {}

    def add(self, resource: Any) -> None:
        """
        Register or replace a resource by its concrete type.
        """
        self._resources[type(resource)] = resource

    def set(self, resource: Any) -> None:
        """
        Alias for add().
        """
        self.add(resource)

    def get(self, resource_type: type[T]) -> T:
        """
        Retrieve a resource by type.

        Raises:
            KeyError: if the resource type is not registered
        """
        try:
            return self._resources[resource_type]
        except KeyError as exc:
            raise KeyError(
                f"Resource not found: {getattr(resource_type, '__name__', resource_type)}"
            ) from exc

    def try_get(self, resource_type: type[T]) -> T | None:
        """
        Retrieve a resource by type, or None if absent.
        """
        return self._resources.get(resource_type)

    def remove(self, resource_type: type) -> None:
        """
        Remove a resource by type.

        Raises:
            KeyError: if the resource type is not registered
        """
        del self._resources[resource_type]

    def has(self, resource_type: type) -> bool:
        """
        Return True if the resource type is registered.
        """
        return resource_type in self._resources

    def clear(self) -> None:
        """
        Remove all registered resources.
        """
        self._resources.clear()

    def types(self) -> tuple[type, ...]:
        return tuple(self._resources.keys())

    def items(self) -> tuple[tuple[type, Any], ...]:
        return tuple(self._resources.items())

    def values(self) -> tuple[Any, ...]:
        return tuple(self._resources.values())

    def __contains__(self, resource_type: object) -> bool:
        return isinstance(resource_type, type) and resource_type in self._resources

    def __len__(self) -> int:
        return len(self._resources)

    def stats(self) -> dict[str, Any]:
        return {
            "count": len(self._resources),
            "types": [
                getattr(resource_type, "__name__", repr(resource_type))
                for resource_type in self._resources
            ],
        }