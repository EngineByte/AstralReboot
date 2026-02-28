from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set, Tuple

import pyglet
from pyglet.window import key, mouse
import numpy as np

from ecs.world import ECSWorld
from ecs.query import Query
from components.player_controller import PlayerController
from components.transform import Transform
from components.velocity import Velocity
from resources.input_state import InputState
from renderer.astralwindow import AstralWindow
from systems.movement_system import system_movement


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
        
    if mouse.RIGHT in inp.buttons_pressed:
        set_mouse_lock(world.resources.get(AstralWindow), world, not inp.mouse_locked)
        
    for eid, i_tr, i_v, i_c in Query(world, (Transform, Velocity, PlayerController)):
        sens = float(ctrl.mouse_sens[i_c])
        inv = bool(ctrl.invert_y[i_c])
        speed = float(ctrl.move_speed[i_c])
        
        dy_sign = -1.0 if inv else 1.0
        tr.yaw[i_tr] += mdx * sens
        tr.pitch[i_tr] += mdy * sens * dy_sign
        
        cy = np.cos(np.radians(tr.yaw[i_tr]))
        sy = np.sin(np.radians(tr.yaw[i_tr]))
        
        fx = -sy
        fz = -cy
        
        rx = cy
        rz = -sy
        
        vx = (fx * forward + rx * strafe) * speed
        vz = (fz * forward + rz * strafe) * speed
        vy = up * speed
        
        vel.vx[i_v] = vx
        vel.vy[i_v] = vy
        vel.vz[i_v] = vz
          
def set_mouse_lock(window: 'AstralWindow', world: 'ECSWorld', locked: bool) -> None:
    inp = world.resources.get(InputState)
    inp.mouse_locked = locked
    window.set_exclusive_mouse(locked)

def system_input_begin_frame(world: 'ECSWorld', dt: float) -> None:
    world.resources.get(InputState).begin_frame()

def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x
    
def bind_input(window: 'AstralWindow', world: 'ECSWorld') -> None:
    if not hasattr(world, 'resources'):
        raise AttributeError('ECSWorld must have world.resource(T) -> resource instance')
    
    world.resources.add(InputState)
    
    def I() -> InputState:
        return world.resources.get(InputState)
    
    @window.event
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        inp = I()
        if not inp.enabled:
            return
        if symbol not in inp.keys_down:
            inp.keys_pressed.add(symbol)
        inp.keys_down.add(symbol)
        
    @window.event
    def on_key_release(symbol: int, modifiers: int) -> None:
        inp = I()
        if symbol in inp.keys_down:
            inp.keys_down.remove(symbol)
        inp.keys_released.add(symbol)
        
    @window.event
    def on_mouse_motion(x: int, y: int, dx: int, dy: int) -> None:
        inp = I()
        inp.mouse_pos = (x, y)
        if not inp.enabled:
            return
        mdx, mdy = inp.mouse_delta
        inp.mouse_delta = (mdx + dx, mdy + dy)
        
    @window.event
    def on_mouse_drag(x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        on_mouse_motion(x, y, dx, dy)
        
    @window.event
    def on_mouse_press(x: int, y: int, button: int, modifiers: int) -> None:
        inp = I()
        if not inp.enabled:
            return
        if button not in inp.buttons_down:
            inp.buttons_pressed.add(button)
        inp.buttons_down.add(button)
        
    @window.event
    def on_mouse_release(x: int, y: int, z: int, button: int, modifiers: int) -> None:
        inp = I()
        if button in inp.buttons_down:
            inp.buttons_down.remove(button)
        inp.buttons_released.add(button)
        
    @window.event
    def on_mouse_scroll(s: int, y: int, scroll_x: int, scroll_y: int) -> None:
        inp = I()
        if not inp.enabled:
            return
        sx, sy = inp.scroll_delta
        inp.scroll_delta = (sx + scroll_x, sy + scroll_y)
        
    @window.event
    def on_deactivate() -> None:
        I().clear_all()
        
    @window.event
    def on_activate() -> None:
        pass

