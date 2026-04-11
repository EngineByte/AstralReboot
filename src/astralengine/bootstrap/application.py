from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter, sleep
from typing import Iterable, Sequence

from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.ecs.scheduling.phases import DEFAULT_PHASES


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
    Runtime control for the application loop.

    Attributes:
        startup_phases:
            Phases to run once before entering the main loop.
        frame_plan:
            The ordered phases that run every frame.
        fixed_dt:
            Delta time passed into each frame.
        max_frames:
            Optional frame cap for tests, smoke runs, and deterministic execution.
            None means run until interrupted.
        target_fps:
            Optional frame limiter. If None, runs as fast as possible.
    '''
    startup_phases: tuple[str, ...] = ('startup',)
    frame_plan: FramePhasePlan = field(default_factory=FramePhasePlan)
    fixed_dt: float = 1.0 / 60.0
    max_frames: int | None = None
    target_fps: float | None = 60.0

    @property
    def frame_duration(self) -> float | None:
        if self.target_fps is None or self.target_fps <= 0.0:
            return None
        return 1.0 / self.target_fps


def build_world() -> ECSWorld:
    '''
    Compose and return the application ECS world.

    This is the place to:
    - instantiate the world
    - register resources
    - register phases / scheduler config
    - register systems
    '''
    world = ECSWorld()

    scheduler = SystemScheduler(phases=DEFAULT_PHASES)

    world.bind_scheduler(scheduler)

    return world


def _run_phases(world: ECSWorld, phases: Sequence[str], dt: float) -> None:
    '''
    Run a sequence of named phases in order.
    '''
    for phase in phases:
        world.run_phase(phase, dt)


def run_application(
    world: ECSWorld | None = None,
    config: ApplicationConfig | None = None,
) -> int:
    '''
    Run the application.

    Returns:
        Exit code integer.
    '''
    cfg = config or ApplicationConfig()
    ecs_world = world or build_world()

    if ecs_world._scheduler is None:
        raise RuntimeError("Application world has no scheduler. Did you forget build_world()?") 
    
    ecs_world.run_frame(cfg.fixed_dt)

    frame_index = 0

    try:
        while cfg.max_frames is None or frame_index < cfg.max_frames:
            frame_start = perf_counter()

            _run_phases(
                ecs_world,
                cfg.frame_plan.phases,
                cfg.fixed_dt,
            )

            frame_index += 1

            frame_duration = cfg.frame_duration
            if frame_duration is not None:
                elapsed = perf_counter() - frame_start
                remaining = frame_duration - elapsed
                if remaining > 0.0:
                    sleep(remaining)

    except KeyboardInterrupt:
        print("\nShutting down application...")
        return 0

    print("\nMax frames reached. Ending application...")
    return 0