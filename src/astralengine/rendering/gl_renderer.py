from __future__ import annotations

from pyglet.gl import (
    GL_COLOR_BUFFER_BIT,
    glClear,
    glClearColor,
)

from astralengine.rendering.backend import RenderBackend
from astralengine.rendering.triangle_demo import TriangleDemo


class GLRenderer(RenderBackend):
    '''
    Minimal OpenGL renderer for the current engine slice.

    Responsibilities:
    - own frame begin/end operations
    - own render demos/pipelines
    - coordinate rendering against the active window/context
    '''

    __slots__ = (
        '_window',
        '_triangle_demo',
        '_initialized',
    )

    def __init__(self, window) -> None:
        self._window = window
        self._triangle_demo = TriangleDemo()
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        self._window.switch_to()
        self._window.set_viewport()

        self._triangle_demo.initialize()
        self._initialized = True

    def begin_frame(self) -> None:
        self._window.switch_to()
        self._window.set_viewport()

        glClearColor(0.08, 0.08, 0.12, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def render_demo_triangle(self) -> None:
        if not self._initialized:
            self.initialize()

        self._triangle_demo.draw()

    def end_frame(self) -> None:
        self._window.swap_buffers()

    def shutdown(self) -> None:
        self._window.switch_to()

        self._triangle_demo.shutdown()
        self._initialized = False