from __future__ import annotations

from typing import Set, Tuple

from pyglet.window import key
import numpy as np

from ecs.world import ECSWorld
from ecs.query import Query
from components.player_controller import PlayerController
from components.transform import Transform
from components.velocity import Velocity
from resources.input_state import InputState
from renderer.astralwindow import AstralWindow


def system_player_controller(world: 'ECSWorld', dt: float) -> None:
    inp = world.resources.get(InputState)
    if not inp.enabled:
        return
    
    
    
    tr = world.store(Transform)
    vel = world.store(Velocity)
    ctrl = world.store(PlayerController)
    
    mdx, mdy = inp.mouse_delta
    
    forward = 0.0
    strafe = 0.0
    up = 0.0
    
    if key.W in inp.keys_down:
        forward -= 1.0
        
    if key.A in inp.keys_down:
        strafe += 1.0
        
    if key.S in inp.keys_down:
        forward += 1.0
        
    if key.D in inp.keys_down:
        strafe -= 1.0
        
    if key.SPACE in inp.keys_down:
        up += 1.0
        
    if key.LCTRL in inp.keys_down:
        up -= 1.0
        
    for eid, i_tr, i_v, i_c in Query(world, (Transform, Velocity, PlayerController)):
        inp.begin_frame()
        sens = float(ctrl.mouse_sens[i_c])
        inv = bool(ctrl.invert_y[i_c])
        speed = float(ctrl.move_speed[i_c])
        
        dy_sign = -1.0 if inv else 1.0
        tr.yaw[i_tr] += mdx * sens
        tr.pitch[i_tr] += mdy * sens * dy_sign
        tr.pitch[i_tr] = clamp(tr.pitch[i_tr], -89.9, 89.9)
        
        cy = np.cos(np.radians(tr.yaw[i_tr]))
        sy = np.sin(np.radians(tr.yaw[i_tr]))
        
        fx = -sy
        fz = -cy
        
        rx = cy
        rz = -sy
        
        vel.vx[i_v] = (fx * forward + rx * strafe) * speed
        vel.vy[i_v] = up * speed
        vel.vz[i_v] = (fz * forward + rz * strafe) * speed
        
        
          
def set_mouse_lock(window: 'AstralWindow', world: 'ECSWorld', locked: bool) -> None:
    inp = world.resources.get(InputState)
    inp.mouse_locked = locked
    window.set_exclusive_mouse(locked)

def system_input_begin_frame(world: 'ECSWorld', dt: float) -> None:
    world.resources.get(InputState).begin_frame()

def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x
    