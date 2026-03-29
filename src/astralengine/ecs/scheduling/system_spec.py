from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from astralengine.ecs.core.world import ECSWorld
    
SystemFn = Callable[['ECSWorld', float], None]


@dataclass(frozen=True, slots=True)
class SystemSpec:
    func: SystemFn
    phase: str = 'update'
    order: int = 0
    name: Optional[str] = None
    enabled: bool = True

    before: Sequence[str] = field(default_factory=tuple)
    after: Sequence[str] = field(default_factory=tuple)

    def system_name(self) -> str:
        return self.name or getattr(self.func, '__name__', 'system')