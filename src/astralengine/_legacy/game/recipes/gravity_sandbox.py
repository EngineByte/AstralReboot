from __future__ import annotations

from astralengine.ecs.core.world import ECSWorld
from astralengine.old_code.game.factories.camera_factory import spawn_follow_camera
from astralengine.old_code.game.factories.chunk_factory import spawn_chunk
from astralengine.old_code.game.factories.player_factory import spawn_player
from astralengine.old_code.game.specs.camera_spec import CameraSpec
from astralengine.old_code.game.specs.chunk_spec import ChunkSpec
from astralengine.old_code.game.specs.player_spec import PlayerSpec


def build_gravity_sandbox_scene(world: ECSWorld) -> None:
    player_eid = spawn_player(
        world,
        PlayerSpec(
            position=(0.0, 0.0, -8.0),
            move_speed=10.0,
            look_sensitivity=0.18,
        ),
    )

    spawn_follow_camera(
        world,
        CameraSpec(
            parent_eid=player_eid,
            follow_offset=(0.0, 0.6, 0.0),
            fov=80.0,
            near=0.1,
            far=50_000.0,
        ),
    )

    spawn_chunk(
        world,
        ChunkSpec(
            coord=(0, 0, 0),
            size=16,
            position=(0.0, 0.0, 0.0),
            mass=5000.0,
            gravity_strength=1000.0,
            fill_value=1,
        ),
    )

    spawn_chunk(
        world,
        ChunkSpec(
            coord=(1, 0, 0),
            size=16,
            position=(100.0, 0.0, 0.0),
            linvel=(0.0, 0.0, 2.0),
            mass=2500.0,
            gravity_strength=1000.0,
            fill_value=1,
        ),
    )

    spawn_chunk(
        world,
        ChunkSpec(
            coord=(-1, 0, 0),
            size=16,
            position=(-140.0, 0.0, 0.0),
            linvel=(0.0, 0.0, -1.5),
            angvel=(0.0, 10.0, 0.0),
            mass=4000.0,
            gravity_strength=1000.0,
            fill_value=1,
        ),
    )