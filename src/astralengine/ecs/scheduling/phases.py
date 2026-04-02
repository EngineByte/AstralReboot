from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    '''
    Immutable description of a system scheduler execution phase.
    
    Fields:
        - 'name': unique phase identifier string
        - 'commit_after': when True, the system scheduler will call
        world.apply_commands() after the phase is completed.
    '''

    name: str
    commit_after: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError('PhaseSpec.name must be a non-empty string.')
        

DEFAULT_PHASES: tuple[PhaseSpec, ...] = (
    PhaseSpec(name='startup', commit_after=True),
    PhaseSpec(name='input', commit_after=False),
    PhaseSpec(name='pre-sim', commit_after=False),
    PhaseSpec(name='sim', commit_after=True),
    PhaseSpec(name='post-sim', commit_after=True),
    PhaseSpec(name='pre-render', commit_after=False),
    PhaseSpec(name='render_extract', commit_after=True),
    PhaseSpec(name='cleanup', commit_after=True),
)