from astralengine.ecs.core.world import ECSWorld
from astralengine.old_code.components.transform import Transform
from astralengine.old_code.components.velocity import Velocity
from astralengine.old_code.components.acceleration import Acceleration
from astralengine.old_code.components.gravity import GravityWell
from astralengine.old_code.components.mass import Mass
from astralengine.old_code.components.tags import DirtyRemodel
from astralengine.old_code.game.specs.gravity_body_spec import GravityBodySpec


def spawn_gravity_body(world: ECSWorld, spec: GravityBodySpec) -> int:
    '''
    Spawn a non-chunk physical body that has gravity
    '''

    eid = world.create_entity()

    world.add_component(
        eid,
        Transform(
            position=spec.position,
            rotation=spec.rotation
        )
    )

    world.add_component(
        eid,
        Velocity(
            linear=spec.linvel,
            angular=spec.angvel
        )
    )

    world.add_component(
        eid,
        Acceleration(
            linear=(0.0, 0.0, 0.0),
            angular=(0.0, 0.0, 0.0)
        )
    )

    world.add_component(eid, Mass(mass=spec.mass))
    world.add_component(eid, GravityWell(mu=spec.gravity_strength))
    world.add_tag(eid, DirtyRemodel)

    return eid
