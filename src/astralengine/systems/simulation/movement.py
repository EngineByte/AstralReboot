from __future__ import annotations

import numpy as np

from astralengine.components.velocity import Velocity
from astralengine.components.transform import Transform
from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.math.math_quat import quat_from_axis_angle, quat_mul, quat_normalize


def movement_system(world, dt: float) -> None:
    for _eid, (transform, velocity) in world.query((Transform, Velocity)):
        transform.position += velocity.linaer * dt
        omega = velocity.angular
        omega_mag = np.linalg.norm(omega)

        if omega_mag > 0.0:
            angle = omega_mag * dt
            axis = omega / omega_mag
            dq = quat_from_axis_angle(axis, angle)

            transform.orientation = quat_normalize(quat_mul(transform.orientation, dq))

        transform.invalidate_cached_matrices()

def register_movement_systems(scheduler) -> None:
    scheduler.add_system(
        SystemSpec(
            name='simulation.movement',
            fn=movement_system,
            phase='sim',
        )
    )