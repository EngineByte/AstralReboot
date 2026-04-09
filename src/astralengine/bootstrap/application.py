from __future__ import annotations

import time

from astralengine.bootstrap.ecs_bootstrap import create_ecs_world


def run_application() -> None:
    world = create_ecs_world()
    run_main_loop(world)

def run_main_loop(world) -> None:
    target_dt = 1.0 / 60.0

    running = True
    while running:
        start = time.perf_counter()

        world.run_frame(target_dt)

        elapsed = time.perf_counter() - start

        sleep_time = target_dt - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)