from __future__ import annotations

import numpy as np

from ecs.world import ECSWorld
from ecs.system_spec import SystemSpec

from components.transform import Transform
from components.velocity import Velocity
from components.camera import Camera
from components.camera_matrices import CameraMatrices
from components.tags import DirtyMatrices, DirtyRemesh
from components.chunk import Chunk
from components.mesh import Mesh
from components.parent_follow import ParentFollow
from components.player_controller import PlayerController

from systems.movement_system import system_movement
from systems.camera_system import system_update_camera_matrices
from systems.render_system import system_render
from systems.chunk_remesh_system import system_chunk_remesh
from systems.chunk_draw_system import system_chunk_render
from systems.parent_follow_system import system_parent_follow
from systems.player_controller_system import system_player_controller

from resources.voxels.chunk_map import ChunkMap
from resources.voxels.voxel_pool import VoxelPool
from resources.input_state import InputState, bind_input

from renderer.renderer import Renderer
from renderer.mesh_pool import MeshPool
from renderer.astralwindow import AstralWindow


def setup_game_world(world: ECSWorld) -> None:
    renderer = Renderer()
    world.resources.add(Renderer, renderer)

    player = world.create_entity()

    world.add_component(player, Transform(
        position=np.array([0.0, 0.0, -5.0], dtype=np.float32),
        rotation=np.array([0.0, 0.0, 0.0], dtype=np.float32),
        scale=np.array([1.0, 1.0, 1.0], dtype=np.float32),
    ))

    world.add_component(player, Velocity(
        linear=np.zeros(3, dtype=np.float32)
    ))

    world.add_component(player, PlayerController(
        move_speed=6.0,
        mouse_sens=0.15,
        invert_y=False 
    ))

    camera = world.create_entity()

    world.add_component(camera, Transform(
        position=np.array([0.0, 1.8, -5.0], dtype=np.float32),
        rotation=np.array([0.0, 0.0, 0.0], dtype=np.float32),
        scale=np.array([1.0, 1.0, 1.0], dtype=np.float32),
    ))

    world.add_component(camera, Camera(
        fov=75.0,
        near=0.1,
        far=5000.0,
        aspect=1280.0 / 720.0,
    ))
    
    world.add_component(camera, ParentFollow(
        parent=player,
        offset=np.array([0.0, 1.8, 0.0], dtype=np.float32)
    ))

    def construct_view_matrix(y, p, r, px, py, pz):
        yaw=np.radians(y+180.0)
        pitch=np.radians(p)
        roll=np.radians(r)

        cy, sy = np.cos(yaw), np.sin(yaw)
        cp, sp = np.cos(pitch), np.sin(pitch)
        cr, sr = np.cos(roll), np.sin(roll)
        
        mtx_yaw = np.identity(4, dtype=np.float32)
        mtx_pitch = np.identity(4, dtype=np.float32)
        mtx_roll = np.identity(4, dtype=np.float32)

        mtx_yaw[0, 0], mtx_yaw[2, 2] = cy, cy
        mtx_yaw[0, 2], mtx_yaw[2, 0] = -sy, sy
        
        mtx_pitch[1, 1], mtx_pitch[2, 2] = cp, cp
        mtx_pitch[1, 2], mtx_pitch[2, 1] = sp, -sp
        
        mtx_roll[0, 0], mtx_roll[1, 1] = cr, cr
        mtx_roll[0, 1], mtx_roll[1, 0] = -sr, sr

        mtx_pos = np.identity(4, dtype=np.float32)
        mtx_pos[:3, 3] = (-px, -py, -pz)
        mtx_rot = mtx_roll @ mtx_pitch @ mtx_yaw
        view = mtx_rot @ mtx_pos

        return view
        
    def construct_proj_matrix(fov, zn, zf, aspect):
        proj = np.identity(4, dtype=np.float32)

        f_factor = 1 / np.tan(0.5 * np.radians(fov))
        z_factor = (zn + zf) / (zf - zn)
        z_offset = 2.0 * zn * zf / (zn - zf)

        proj[0, 0] = f_factor / aspect
        proj[1, 1] = f_factor
        proj[2, 2] = z_factor
        proj[2, 3] = z_offset
        proj[3, 2] = -1.0

        return proj

    view = construct_view_matrix(
        y=0.0, 
        p=0.0, 
        r=0.0, 
        px=0.0, 
        py=1.8, 
        pz=-5.0
    )

    proj = construct_proj_matrix(
        fov=60.0, 
        zn=0.1, 
        zf=5000.0, 
        aspect=1280.0 / 720.0
    )

    world.add_component(camera, CameraMatrices(
        view=view,
        projection=proj,
    ))

    world.add_tag(camera, DirtyMatrices)

    world.scheduler.add_system(
        SystemSpec(
            func=system_movement,
            phase='update',
            name='movement'
        )
    )

    world.scheduler.add_system(
        SystemSpec(
            func=system_update_camera_matrices,
            phase="late_update",
            name='update_camera_matrices'
        )
    )

    world.scheduler.add_system(
        SystemSpec(
            func=system_render,
            phase="render",
            name='render'
        )
    )

    world.scheduler.add_system(
        SystemSpec(
            func=system_chunk_remesh,
            phase='update', 
            order=50,
            name='chunk_remesh'
        )
    )

    world.scheduler.add_system(
        SystemSpec(
            func=system_chunk_render,
            phase='render', 
            order=50,
            name='chunk_render'
        )
    )
    
    world.scheduler.add_system(
        SystemSpec(
            func=system_parent_follow,
            phase='update',
            order=50,
            name='parent_follow'
        )
    )

    world.scheduler.add_system(
        SystemSpec(
            func=system_player_controller,
            phase='update',
            order=50,
            name='player_controller'
        )
    )

    world.resources.add(VoxelPool, VoxelPool())
    world.resources.add(ChunkMap, ChunkMap())
    world.resources.add(MeshPool, MeshPool())
    world.resources.add(InputState, InputState())
    window = world.resources.get(AstralWindow)
    bind_input(window, world)

    voxel_pool = world.resources.get(VoxelPool)
    chunk_map = world.resources.get(ChunkMap)
    inputstate = world.resources.get(InputState)

    size = 32
    handle = voxel_pool.alloc(size=size, fill=0)

    block = voxel_pool.block(handle)

    def idx(x, y, z): return x + size*(y + size*z)

    for z in range(10, 14):
        for x in range(10, 14):
            block.data[idx(x, 10, z)] = 1

    chunk_eid = world.create_entity()
    world.add_component(chunk_eid, Chunk(coord=np.array([0,0,0], dtype=np.int32), size=size, voxel_handle=handle))
    world.add_component(chunk_eid, Mesh(mesh_id=-1))
    world.add_tag(chunk_eid, DirtyRemesh) 

    chunk_map.set((0,0,0), chunk_eid)