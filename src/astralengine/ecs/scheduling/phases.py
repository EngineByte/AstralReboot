from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PhaseSpec:
    '''
    Describes one scheduler phase.

    Attributes:
        name:
            Unique phase name.
        commit_after:
            If True, deferred world commands are applied after the phase.
        is_frame_phase:
            If True, this phase participates in normal per-frame execution.
            Lifecycle phases like startup/shutdown should set this to False.
    '''
    name: str
    commit_after: bool = True
    is_frame_phase: bool = True


STARTUP_PHASE = PhaseSpec(
    name='startup',
    commit_after=True,
    is_frame_phase=False,
)

FRAME_PHASES: tuple[PhaseSpec, ...] = (
    PhaseSpec(
        name='input',
        commit_after=True,
        is_frame_phase=True,
    ),
    PhaseSpec(
        name='pre_sim',
        commit_after=True,
        is_frame_phase=True,
    ),
    PhaseSpec(
        name='sim',
        commit_after=True,
        is_frame_phase=True,
    ),
    PhaseSpec(
        name='post_sim',
        commit_after=True,
        is_frame_phase=True,
    ),
    PhaseSpec(
        name='pre_render',
        commit_after=True,
        is_frame_phase=True,
    ),
    PhaseSpec(
        name='render_extract',
        commit_after=True,
        is_frame_phase=True,
    ),
    PhaseSpec(
        name='cleanup',
        commit_after=True,
        is_frame_phase=True,
    ),
)

SHUTDOWN_PHASE = PhaseSpec(
    name='shutdown',
    commit_after=True,
    is_frame_phase=False,
)

ALL_PHASES: tuple[PhaseSpec, ...] = (
    STARTUP_PHASE,
    *FRAME_PHASES,
    SHUTDOWN_PHASE,
)

DEFAULT_PHASES: tuple[PhaseSpec, ...] = ALL_PHASES