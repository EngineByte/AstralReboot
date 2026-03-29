from astralengine.ecs.core.world import ECSWorld
from astralengine.game.factories.camera_factory import spawn_follow_camera
from astralengine.game.factories.player_factory import spawn_player
from astralengine.game.specs.camera_spec import CameraSpec
from astralengine.game.specs.player_spec import PlayerSpec


def build_skybox_test_scene(world: ECSWorld) -> None:
    player_eid = spawn_player(
        world,
        PlayerSpec(
            position=(0.0, 0.0, 0.0),
            move_speed=6.0,
            look_sensitivity=0.15
        )
    )

    spawn_follow_camera(
        world,
        CameraSpec(
            parent_eid=player_eid,
            fov=60.0,
            near=0.1,
            far=10_000.0
        )
    )