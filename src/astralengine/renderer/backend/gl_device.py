from __future__ import annotations

from pyglet import gl


class GLDevice:
    """
    Thin helper around common global GL state transitions.
    """

    def set_viewport(self, width: int, height: int) -> None:
        gl.glViewport(0, 0, int(width), int(height))

    def clear(self, color: tuple[float, float, float, float]) -> None:
        gl.glClearColor(*color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def set_depth_test(self, enabled: bool) -> None:
        if enabled:
            gl.glEnable(gl.GL_DEPTH_TEST)
        else:
            gl.glDisable(gl.GL_DEPTH_TEST)

    def set_cull_faces(self, enabled: bool) -> None:
        if enabled:
            gl.glEnable(gl.GL_CULL_FACE)
        else:
            gl.glDisable(gl.GL_CULL_FACE)

    def set_blend(self, enabled: bool) -> None:
        if enabled:
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        else:
            gl.glDisable(gl.GL_BLEND)

    def set_wireframe(self, enabled: bool) -> None:
        mode = gl.GL_LINE if enabled else gl.GL_FILL
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, mode)

    def set_depth_mask(self, enabled: bool) -> None:
        gl.glDepthMask(gl.GL_TRUE if enabled else gl.GL_FALSE)