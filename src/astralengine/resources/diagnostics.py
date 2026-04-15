from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PhaseTimingSnapshot:
    name: str
    system_count: int
    elapsed_sec: float
    commit_after: bool


@dataclass(slots=True)
class DiagnosticStats:
    '''
    Rolling diagnostic data for the active simulation session.
    '''
    frames_since_log: int = 0
    log_every_n_frames: int = 60

    current_frame_index: int = 0
    elapsed_time: float = 0.0
    dt: float = 0.0

    alive_entities: int = 0
    phase_timings: list[PhaseTimingSnapshot] = field(default_factory=list)