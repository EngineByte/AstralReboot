from __future__ import annotations

from astralengine.components.acceleration import Acceleration
from astralengine.components.frame import Frame
from astralengine.components.gravity import GravityWell
from astralengine.components.mass import Mass
from astralengine.components.model_matrix import ModelMatrix
from astralengine.components.tags import DirtyRemodel
from astralengine.components.transform import Transform
from astralengine.components.velocity import Velocity
from astralengine.ecs.world import ECSWorld
from astralengine.game.specs.frame_spec import FrameSpec
from astralengine.frames.frame_map import FrameMap
from astralengine.frames.frame_pool import FramePool


def spawn_frame(world: ECSWorld, spec: FrameSpec) -> int:
    frame_pool = world.resources.get(FramePool)
    frame_map = world.resources.get(FrameMap)

    frame_handle = frame_pool.alloc(
        size=spec.size,
        fill=spec.fill_value,
    )

    eid = world.create_entity()

    world.add_component(
        eid,
        Transform(
            position=spec.position,
            rotation=spec.rotation,
            scale=(1.0, 1.0, 1.0),
        ),
    )
    
    world.add_component(
        eid,
        Velocity(
            linear=spec.linvel,
            angular=spec.angvel,
        ),
    )
    
    world.add_component(
        eid,
        Acceleration(
            linear=(0.0, 0.0, 0.0),
            angular=(0.0, 0.0, 0.0),
        ),
    )
    
    world.add_component(
        eid,
        Frame(
            size=spec.size,
            frame_handle=frame_handle,
        ),
    )
    
    world.add_component(
        eid,
        ModelMatrix.identity(),
    )
    
    world.add_component(
        eid,
        Mass(mass=spec.mass),
    )

    if spec.gravity_strength != 0.0:
        world.add_component(
            eid,
            GravityWell(mu=spec.gravity_strength),
        )

    if spec.mark_dirty_remodel:
        world.add_tag(eid, DirtyRemodel)

    return eid