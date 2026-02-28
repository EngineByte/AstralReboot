from dataclasses import dataclass, field

from typing import Set, Tuple

import pyglet

from ecs.world import ECSWorld
from renderer.astralwindow import AstralWindow


class InputState:
    def __init__(self) -> None:
        self.keys_down: Set[int] = set()
        self.keys_pressed: Set[int] = set()
        self.keys_released: Set[int] = set()
        
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_delta: Tuple[int, int] = (0, 0)
        
        self.scroll_delta: Tuple[int, int] = (0, 0)
        
        self.buttons_down: Set[int] = set()
        self.buttons_pressed: Set[int] = set()
        self.buttons_released: Set[int] = set()
        
        self.mouse_locked: bool = False
        self.enabled: bool = True
    
    def begin_frame(self) -> None:
        self.keys_pressed.clear()
        self.keys_released.clear()
        self.buttons_pressed.clear()
        self.buttons_released.clear()
        self.mouse_delta = (0, 0)
        self.scroll_delta = (0, 0)
        
        
    def clear_all(self) -> None:  
        self.keys_pressed.clear()
        self.keys_down.clear()
        self.keys_released.clear()
        self.buttons_down.clear()
        self.buttons_pressed.clear()
        self.buttons_released.clear()
        self.mouse_delta = (0, 0)
        self.scroll_delta = (0, 0)   


def system_input_begin_frame(world: 'ECSWorld', dt: float) -> None:
    world.resources.get(InputState).begin_frame()

def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x



    
def bind_input(window: 'AstralWindow', world: 'ECSWorld') -> None:
    if not hasattr(world, 'resources'):
        raise AttributeError('ECSWorld must have world.resource(T) -> resource instance')
    
    def I() -> InputState:
        return world.resources.get(InputState)
    
    window.set_exclusive_mouse(True)
    
    @window.event
    def on_key_press(symbol: int, modifiers: int) -> None:
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
        inp.mouse_delta = (mdx - dx, mdy + dy)
        
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
    def on_mouse_release(x: int, y: int, button: int, modifiers: int) -> None:
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

