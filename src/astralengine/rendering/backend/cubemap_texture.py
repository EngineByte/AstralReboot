from __future__ import annotations

import ctypes as ct

from pyglet import gl


class CubemapTexture:
    """
    Lightweight wrapper for an existing GL cubemap texture.
    """

    def __init__(self, texture_id: int) -> None:
        self.texture_id = int(texture_id)

    def bind(self, unit: int = 0) -> None:
        gl.glActiveTexture(gl.GL_TEXTURE0 + int(unit))
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.texture_id)

    def delete(self) -> None:
        if self.texture_id:
            tid = gl.GLuint(self.texture_id)
            gl.glDeleteTextures(1, ct.byref(tid))
            self.texture_id = 0