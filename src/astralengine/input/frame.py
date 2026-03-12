from __future__ import annotations

from astralengine.ecs.world import ECSWorld
from astralengine.resources.input_state import InputState


def system_input_begin_frame(world: ECSWorld, dt: float) -> None:
    _ = dt
    inp = world.resources.get(InputState)
    inp.mouse_delta = (0.0, 0.0)