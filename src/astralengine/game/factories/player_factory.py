from __future__ import annotations

from astralengine.components.acceleration import Acceleration
from astralengine.components.player_controller import PlayerController
from astralengine.components.tags import DirtyMatrices, DirtyRemodel
from astralengine.components.transform import Transform
from astralengine.components.velocity import Velocity
from astralengine.ecs.world import ECSWorld
from astralengine.game.specs.player_spec import PlayerSpec


def spawn_player(world: ECSWorld, spec: PlayerSpec) -> int:
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
        PlayerController(
            move_speed=spec.move_speed,
            look_sensitivity=spec.look_sensitivity,
        ),
    )

    world.add_tag(eid, DirtyMatrices)
    world.add_tag(eid, DirtyRemodel)

    return eid