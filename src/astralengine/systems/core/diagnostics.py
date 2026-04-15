from __future__ import annotations

from astralengine.app.logging_setup import get_logger
from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.resources.diagnostics import (
    DiagnosticStats,
    PhaseTimingSnapshot,
)
from astralengine.resources.time import FrameClock


logger = get_logger('systems.core.diagnostics')


def _count_alive_entities(world) -> int:
    '''
    Best-effort alive entity count.

    Uses the world's internal entity state if available.
    Adjust this if you later expose a formal public API for counts.
    '''
    if hasattr(world, '_entity_count'):
        return world.entity_count()

    if hasattr(world, '_alive'):
        try:
            return len(world._alive)
        except TypeError:
            pass

    return 0


def collect_diagnostic_stats_system(world, dt: float) -> None:
    '''
    Snapshot the frame clock, alive entity count, and latest phase stats.
    '''
    stats = world.get_resource(DiagnosticStats)
    clock = world.get_resource(FrameClock)

    stats.current_frame_index = clock.frame_index
    stats.elapsed_time = clock.elapsed_time
    stats.dt = clock.dt
    stats.alive_entities = world.entity_count()

    phase_timings: list[PhaseTimingSnapshot] = []
    scheduler = world.scheduler
    if scheduler is not None:
        for phase in scheduler.phase_stats():
            phase_timings.append(
                PhaseTimingSnapshot(
                    name=phase.name,
                    system_count=phase.system_count,
                    elapsed_sec=phase.elapsed_sec,
                    commit_after=phase.commit_after,
                )
            )

    stats.phase_timings = phase_timings


def log_diagnostic_stats_system(world, dt: float) -> None:
    '''
    Emit a periodic diagnostic summary.
    '''
    stats = world.get_resource(DiagnosticStats)
    stats.frames_since_log += 1

    if stats.log_every_n_frames <= 0:
        return

    if stats.frames_since_log < stats.log_every_n_frames:
        return

    stats.frames_since_log = 0

    if stats.phase_timings:
        phase_summary = ', '.join(
            f'{phase.name}={phase.elapsed_sec * 1000.0:.3f}ms/{phase.system_count}sys'
            for phase in stats.phase_timings
        )
    else:
        phase_summary = 'no phase data'

    logger.info(
        'frame=%d elapsed=%.3fs dt=%.4f alive=%d phases=[%s]',
        stats.current_frame_index,
        stats.elapsed_time,
        stats.dt,
        stats.alive_entities,
        phase_summary,
    )


def register_diagnostic_systems(scheduler) -> None:
    scheduler.add_system(
        SystemSpec(
            name='core.collect_diagnostics',
            fn=collect_diagnostic_stats_system,
            phase='cleanup',
        )
    )
    scheduler.add_system(
        SystemSpec(
            name='core.log_diagnostics',
            fn=log_diagnostic_stats_system,
            phase='cleanup',
            after=('core.collect_diagnostics',),
        )
    )