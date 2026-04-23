from __future__ import annotations

from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.systems.rendering.extract_camera import (
    register_render_camera_systems,
)
from astralengine.systems.rendering.extract_meshes import (
    register_render_mesh_systems,
)


def register_render_extract_systems(scheduler: SystemScheduler) -> None:
    register_render_camera_systems(scheduler)
    register_render_mesh_systems(scheduler)