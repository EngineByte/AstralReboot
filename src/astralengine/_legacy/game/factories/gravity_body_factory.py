from astralengine.ecs.core.world import ECSWorld
from astralengine._legacy.components.transform import Transform
from astralengine._legacy.components.velocity import Velocity
from astralengine._legacy.components.acceleration import Acceleration
from astralengine._legacy.components.gravity import GravityWell
from astralengine._legacy.components.mass import Mass
from astralengine._legacy.components.tags import DirtyRemodel
from astralengine._legacy.game.specs.gravity_body_spec import GravityBodySpec


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
