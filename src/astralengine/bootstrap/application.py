from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from astralengine.app.startup import ApplicationContext


@dataclass(slots=True, frozen=True)
class FramePhasePlan:
    '''
    Describes which phases should run, and in what order, for one frame.
    '''
    phases: tuple[str, ...] = (
        'input',
        'pre_sim',
        'sim',
        'post_sim',
        'pre_render',
        'render_extract',
        'cleanup',
    )

    @classmethod
    def from_iterable(cls, phases: Iterable[str]) -> 'FramePhasePlan':
        return cls(phases=tuple(phases))


@dataclass(slots=True)
class ApplicationConfig:
    '''
    Runtime execution configuration for a simulation session.
    '''
    startup_phases: tuple[str, ...] = ('startup',)
    frame_plan: FramePhasePlan = field(default_factory=FramePhasePlan)
    shutdown_phases: tuple[str, ...] = ('shutdown',)
    fixed_dt: float = 1.0 / 60.0
    max_frames: int | None = None
    target_fps: float | None = 60.0

    @property
    def frame_duration(self) -> float | None:
        if self.target_fps is None or self.target_fps <= 0.0:
            return None
        return 1.0 / self.target_fps


@dataclass(slots=True)
class ApplicationRuntime:
    '''
    Top-level application runtime container.

    This owns process-level context and execution config.
    It does not itself contain a simulation world.
    '''
    context: ApplicationContext
    config: ApplicationConfig


def build_application_runtime(
    *,
    context: ApplicationContext,
    config: ApplicationConfig | None = None,
) -> ApplicationRuntime:
    '''
    Build the top-level application runtime object.

    No ECS world is created here yet.
    World/session creation happens later when the flow enters simulation.
    '''
    return ApplicationRuntime(
        context=context,
        config=config or ApplicationConfig(),
    )