from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from astralengine.ecs.core.world import ECSWorld
    
SystemFn = Callable[['ECSWorld', float], None]


@dataclass(slots=True)
class SystemSpec:
    '''
    Declarative description of a System as used by ECS System Scheduler.

    A system is a callable function that operates on ECSWorld entities
    within a specified phase step.  The spec will determine:
        - Which sim phase the system operates within
        - enable/disable
        - system run frequency
        - dependencies and order restraints as related to other systems
    '''
    name: str
    fn: SystemFn
    phase: str
    enabled: bool = True
    run_every: int = 1
    before: tuple[str, ...] = field(default_factory=tuple)
    after: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("System name must be a string.")
        
        if not self.name.strip():
            raise ValueError("System name must not be empty or blank.")

        if not isinstance(self.phase, str):
            raise TypeError("System phase must be a string.")
        if not self.phase.strip():
            raise ValueError("System phase must not be empty or blank.")

        if not callable(self.fn):
            raise TypeError("System fn must be callable.")

        if not isinstance(self.run_every, int):
            raise TypeError("run_every must be an integer.")
        
        if self.run_every < 1:
            raise ValueError("run_every must be >= 1.")

        if self.before is None:
            object.__setattr__(self, "before", ())
        else:
            object.__setattr__(self, "before", tuple(self.before))

        if self.after is None:
            object.__setattr__(self, "after", ())
        else:
            object.__setattr__(self, "after", tuple(self.after))