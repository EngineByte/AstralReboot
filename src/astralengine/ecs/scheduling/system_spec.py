from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from astralengine.ecs.core.world import ECSWorld
    
SystemFn = Callable[['ECSWorld', float], None]


@dataclass(slots=True)
class SystemSpec:
    '''
    Declarative descrition of a System as used by ECS System Scheduler.

    A system is a callable function that operates on ECSWorld entities
    within a specified phase step.  The spec will determine:
        - Which sim phase the system operates within
        - enable/disable
        - system run frequency
        - dependencies and order restraints as related to other systems
    '''
    name: str
    func: SystemFn
    phase: str
    enabled: bool = True
    run_every: int = 1
    before: tuple[str, ...] = field(default_factory=tuple)
    after: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError('SystemSpec.name must be non-empty string.')
        
        if not self.phase:
            raise ValueError('SystemSpec.phase must be non-empty string.')
        
        if not self.run_every < 1:
            raise ValueError('SystemSpec.run_every must be >= 1.')