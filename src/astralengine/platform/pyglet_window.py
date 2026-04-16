from __future__ import annotations

import pyglet
from pyglet.window import Window


class PygletWindow:
    '''
    Thin wrapper around pyglet.window.Window.
    '''

    __slots__ = (
        '_window',
        '_close_requested',
    )

    def __init__(
        self,
        *,
        width: int = 1280,
        height: int = 720,
        caption: str = 'AstralEngine',
        visible: bool = False,
        resizable: bool = True,
        vsync: bool = True,
    ) -> None:
        self._window = pyglet.window.Window(
            width=width,
            height=height,
            caption=caption,
            visible=visible,
            resizable=resizable,
            vsync=vsync,
        )
        self._close_requested = False

        @self._window.event
        def on_close() -> None:
            self._close_requested = True

    @property
    def native(self) -> Window:
        return self._window

    @property
    def width(self) -> int:
        return self._window.width

    @property
    def height(self) -> int:
        return self._window.height

    def show(self) -> None:
        self._window.set_visible(True)

    def switch_to(self) -> None:
        self._window.switch_to()

    def poll_events(self) -> None:
        '''
        Process one OS event batch without entering pyglet.app.run().
        '''
        self._window.dispatch_events()

    def clear(self) -> None:
        self._window.clear()

    def swap_buffers(self) -> None:
        self._window.flip()

    def should_close(self) -> bool:
        return self._close_requested

    def close(self) -> None:
        if not self._window.has_exit:
            self._window.close()
        self._close_requested = True

    def set_caption(self, caption: str) -> None:
        self._window.set_caption(caption)

    def set_viewport(self) -> None:
        pyglet.gl.glViewport(0, 0, self.width, self.height)