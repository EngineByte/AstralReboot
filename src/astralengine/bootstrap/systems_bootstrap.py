from __future__ import annotations

from astralengine.ecs.system_spec import SystemSpec
from astralengine.ecs.world import ECSWorld

from astralengine.input.frame import system_input_begin_frame
from astralengine.renderer.renderer import system_execute_render_pipeline
from astralengine.renderer.submit.submit_camera_system import system_submit_camera
from astralengine.renderer.submit.submit_chunk_system import system_submit_chunks
from astralengine.renderer.submit.submit_debug_system import system_submit_debug
from astralengine.renderer.submit.submit_skybox_system import system_submit_skybox
from astralengine.renderer.submit.upload_mesh_system import system_upload_chunk_meshes
from astralengine.systems.camera.camera_matrices_system import system_update_camera_matrices
from astralengine.systems.camera.parent_follow_system import system_parent_follow
from astralengine.systems.physics.gravity_system import system_gravity
from astralengine.systems.physics.integration_system import system_integration
from astralengine.systems.physics.movement_system import system_movement
from astralengine.systems.player.player_controller_system import system_player_controller
from astralengine.systems.render.update_model_matrices_system import system_update_model_matrices
from astralengine.voxels.systems.chunk_remesh_system import system_chunk_remesh
from astralengine.systems.frames.frame_transform_system import system_frame_transforms
from astralengine.systems.streaming.chunk_streaming_system import system_chunk_streaming
from astralengine.systems.streaming.chunk_activation_system import system_chunk_activation
from astralengine.systems.streaming.chunk_lod_system import system_chunk_lod


def install_core_systems(world: ECSWorld) -> None:
    scheduler = world.scheduler

    scheduler.add_system(
        SystemSpec(
            func=system_input_begin_frame,
            phase="input",
            order=0,
            name="input_begin_frame",
        )
    )

    scheduler.add_system(
        SystemSpec(
            func=system_player_controller,
            phase="update",
            order=10,
            name="player_controller",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_parent_follow,
            phase="update",
            order=20,
            name="parent_follow",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_gravity,
            phase="update",
            order=30,
            name="gravity",
        )
    )

    scheduler.add_system(
        SystemSpec(
            func=system_integration,
            phase='update',
            order=35,
            name='integration'
        )
    )

    scheduler.add_system(
        SystemSpec(
            func=system_movement,
            phase="update",
            order=40,
            name="movement",
        )
    )

    scheduler.add_system(
        SystemSpec(
            func=system_update_camera_matrices,
            phase="post_update",
            order=10,
            name="camera_matrices",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_update_model_matrices,
            phase="post_update",
            order=20,
            name="update_model_matrices",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_chunk_remesh,
            phase="post_update",
            order=30,
            name="chunk_remesh",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_upload_chunk_meshes,
            phase="post_update",
            order=40,
            name="upload_chunk_meshes",
        )
    )

    scheduler.add_system(
        SystemSpec(
            func=system_submit_camera,
            phase="render_submit",
            order=10,
            name="submit_camera",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_submit_skybox,
            phase="render_submit",
            order=20,
            name="submit_skybox",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_submit_chunks,
            phase="render_submit",
            order=30,
            name="submit_chunks",
        )
    )
    scheduler.add_system(
        SystemSpec(
            func=system_submit_debug,
            phase="render_submit",
            order=40,
            name="submit_debug",
        )
    )

    scheduler.add_system(
        SystemSpec(
            func=system_execute_render_pipeline,
            phase="render",
            order=10,
            name="execute_render_pipeline",
        )
    )

    scheduler.add_system(
        SystemSpec(
            func=system_chunk_activation,
            phase='streaming',
            order=51,
            name='chunk_activation'
        )
    )
    
    scheduler.add_system(
        SystemSpec(
            func=system_frame_transforms,
            phase='update',
            order=50,
            name='frame_transforms' 
        )
    )
    
    scheduler.add_system(
        SystemSpec(
            func=system_chunk_streaming,
            phase='streaming',
            order=49,
            name='chunk_streaming' 
        )
    )
    
    scheduler.add_system(
        SystemSpec(
            func=system_chunk_lod,
            phase='streaming',
            order=50,
            name='chunk_lod'            
        )
    )