from __future__ import annotations

from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.resources.time import FrameClock


def frame_clock_system(world, dt: float) -> None:
    clock = world.get_resource(FrameClock)
    clock.frame_index += 1
    clock.dt = dt
    clock.elapsed_time += dt


def register_core_systems(scheduler) -> None:
    scheduler.add_system(
        SystemSpec(
            name='core.frame_clock',
            fn=frame_clock_system,
            phase='pre_sim',
        )
    )