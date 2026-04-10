from __future__ import annotations

from typing import Any


class ResourceRegistry:
    '''
    Stores one resource instance per concrete type.

    Design:
        - Keyed by exact type (no inheritance lookup)
        - O(1) add/get/remove
        - Deterministic, simple behavior

    Core API:
        add(resource)
        get(type) -> resource | None
        has(type) -> bool
        remove(type)
        clear()

    Optional API:
        get_required(type)
        pop(type)
        items(), values(), types()
        summary(), stats()
    '''

    __slots__ = ('_resources',)

    def __init__(self) -> None:
        self._resources: dict[type[Any], Any] = {}

    def add(self, resource: Any) -> None:
        '''
        Add or replace a resource by its concrete type.
        '''
        if resource is None:
            raise ValueError('Resource cannot be None.')

        self._resources[type(resource)] = resource

    def get(self, resource_type: type[Any]) -> Any | None:
        '''
        Returns resource instance or None if not present.
        '''
        return self._resources.get(resource_type)

    def has(self, resource_type: type[Any]) -> bool:
        '''
        True if resource type is present.
        '''
        return resource_type in self._resources

    def remove(self, resource_type: type[Any]) -> None:
        '''
        Remove a resource by type.

        Raises:
            KeyError if resource not present.
        '''
        if resource_type not in self._resources:
            raise KeyError(f'Resource not found: {resource_type.__name__}')

        del self._resources[resource_type]

    def clear(self) -> None:
        '''
        Remove all resources.
        '''
        self._resources.clear()

    def count(self) -> int:
        '''
        Number of registered resource types.
        '''
        return len(self._resources)

    def is_empty(self) -> bool:
        return not self._resources

    def get_required(self, resource_type: type[Any]) -> Any:
        '''
        Returns resource or raises KeyError if missing.
        '''
        try:
            return self._resources[resource_type]
        except KeyError:
            raise KeyError(f'Required resource missing: {resource_type.__name__}')

    def pop(self, resource_type: type[Any]) -> Any:
        '''
        Remove and return resource.

        Raises:
            KeyError if not present.
        '''
        return self._resources.pop(resource_type)

    def items(self) -> tuple[tuple[type[Any], Any], ...]:
        return iter(self._resources.items())

    def values(self) -> tuple[Any, ...]:
        return iter(self._resources.values())

    def types(self) -> tuple[type[Any], ...]:
        return iter(self._resources.keys())

    def __contains__(self, resource_type: type[Any]) -> bool:
        return resource_type in self._resources

    def __len__(self) -> int:
        return len(self._resources)

    def summary(self) -> str:
        '''
        Human-readable summary.
        '''
        types = ', '.join(sorted(t.__name__ for t in self._resources))
        return f'ResourceRegistry(count={len(self._resources)}, types=[{types}])'

    def stats(self) -> dict[str, Any]:
        '''
        Structured debug info.
        '''
        return {
            'count': len(self._resources),
            'types': sorted(t.__name__ for t in self._resources),
        }