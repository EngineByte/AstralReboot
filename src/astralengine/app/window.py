from __future__ import annotations

import pyglet

from astralengine.ecs.world import ECSWorld
from astralengine.resources.input_state import InputState
from astralengine.resources.render_settings import RenderSettings
from astralengine.renderer.renderer import Renderer


class AstralWindow(pyglet.window.Window):
    def __init__(self, world: ECSWorld) -> None:
        self.world = world

        settings = world.resources.get(RenderSettings)

        super().__init__(
            width=settings.viewport_width,
            height=settings.viewport_height,
            caption="AstralEngine",
            resizable=True,
            vsync=settings.vsync,
        )

        self._bind_input()
        pyglet.clock.schedule_interval(self.update, 1.0 / 60.0)

    def _bind_input(self) -> None:
        inp = self.world.resources.get(InputState)
        inp.window = self

    def run(self) -> None:
        pyglet.app.run()

    def update(self, dt: float) -> None:
        self.world.dt_seconds = float(dt)

        # run non-render phases here
        for phase in ("input", "update", "post_update", "render_submit"):
            self.world.scheduler.run_phase(phase, self.world)

        if self.world.command_buffer is not None:
            self.world.command_buffer.flush()

        

    def on_draw(self) -> None:
        self.world.scheduler.run_phase("render", self.world)

    def on_resize(self, width: int, height: int):
        settings = self.world.resources.get(RenderSettings)
        settings.set_viewport(width, height)

        renderer = self.world.resources.get(Renderer)
        renderer.ctx.viewport_width = width
        renderer.ctx.viewport_height = height

        return super().on_resize(width, height)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        inp = self.world.resources.get(InputState)
        inp.keys_down.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        inp = self.world.resources.get(InputState)
        inp.keys_down.discard(symbol)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        inp = self.world.resources.get(InputState)
        inp.mouse_delta = (inp.mouse_delta[0] + dx, inp.mouse_delta[1] + dy)
        inp.mouse_pos = (x, y)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        inp = self.world.resources.get(InputState)
        inp.mouse_delta = (inp.mouse_delta[0] + dx, inp.mouse_delta[1] + dy)
        inp.mouse_pos = (x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        inp = self.world.resources.get(InputState)
        inp.mouse_buttons_down.add(button)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        inp = self.world.resources.get(InputState)
        inp.mouse_buttons_down.discard(button)