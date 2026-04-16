from __future__ import annotations

from astralengine.app.startup import ApplicationContext
from astralengine.platform.pyglet_window import PygletWindow
from astralengine.rendering.gl_renderer import GLRenderer


def bootstrap_graphics(context: ApplicationContext) -> None:
    '''
    Create window and renderer services and attach them to the application context.
    '''
    if context.headless:
        return

    window = PygletWindow(
        width=1280,
        height=720,
        caption='AstralEngine',
        visible=False,
        resizable=True,
        vsync=True,
    )
    renderer = GLRenderer(window)

    renderer.initialize()
    window.show()

    context.window = window
    context.renderer = renderer