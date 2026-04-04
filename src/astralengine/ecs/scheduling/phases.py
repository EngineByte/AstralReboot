from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    '''
    Immutable description of a system scheduler execution phase.
    
    Fields:
        - 'name': unique phase identifier string

        - 'commit_after': when True, the system scheduler will call
        world.apply_commands() after all systems in this phase have finished.
        This is a key structural mutation safety barrier.
    '''

    name: str
    commit_after: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError('PhaseSpec.name must be a non-empty string.')
        
        if ' ' in self.name:
            raise ValueError('PhaseSpec.name must not contain spaces.')
        

DEFAULT_PHASES: tuple[PhaseSpec, ...] = (
    PhaseSpec(name='startup', commit_after=True),
    PhaseSpec(name='input', commit_after=False),
    PhaseSpec(name='pre-sim', commit_after=False),
    PhaseSpec(name='sim', commit_after=True),
    PhaseSpec(name='post-sim', commit_after=True),
    PhaseSpec(name='pre-render', commit_after=False),
    PhaseSpec(name='render-extract', commit_after=True),
    PhaseSpec(name='cleanup', commit_after=True),
)

PHASE_INDEX = {p.name: i for i, p in enumerate(DEFAULT_PHASES)}