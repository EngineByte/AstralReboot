from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class ResourceRegistry:
    def __init__(self) -> None:
        self._resources: Dict[Type[Any], Any] = {}

    def add(self, typ: Type[T], value: T) -> None:
        self._resources[typ] = value

    def get(self, typ: Type[T]) -> T:
        try:
            return self._resources[typ]
        except KeyError as e:
            raise KeyError(f"Resource not found: {typ}") from e

    def try_get(self, typ: Type[T]) -> Optional[T]:
        v = self._resources.get(typ)
        return v
    def remove(self, typ: Type[Any]) -> None:
        self._resources.pop(typ, None)

    def has(self, typ: Type[Any]) -> bool:
        return typ in self._resources

    def clear(self) -> None:
        self._resources.clear()

    def stats(self) -> Dict[str, Any]:
        return {"resources": [t.__name__ for t in self._resources.keys()]}