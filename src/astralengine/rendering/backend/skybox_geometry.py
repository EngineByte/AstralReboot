from __future__ import annotations

import ctypes as ct

import numpy as np
from pyglet import gl


class SkyboxGeometry:
    """
    Cube geometry for skybox rendering.
    """

    def __init__(self) -> None:
        self.vao = gl.GLuint()
        self.vbo = gl.GLuint()
        self.vertex_count = 36

        verts = np.array([
            -1,  1, -1,  -1, -1, -1,   1, -1, -1,
             1, -1, -1,   1,  1, -1,  -1,  1, -1,

            -1, -1,  1,  -1, -1, -1,  -1,  1, -1,
            -1,  1, -1,  -1,  1,  1,  -1, -1,  1,

             1, -1, -1,   1, -1,  1,   1,  1,  1,
             1,  1,  1,   1,  1, -1,   1, -1, -1,

            -1, -1,  1,  -1,  1,  1,   1,  1,  1,
             1,  1,  1,   1, -1,  1,  -1, -1,  1,

            -1,  1, -1,   1,  1, -1,   1,  1,  1,
             1,  1,  1,  -1,  1,  1,  -1,  1, -1,

            -1, -1, -1,  -1, -1,  1,   1, -1, -1,
             1, -1, -1,  -1, -1,  1,   1, -1,  1,
        ], dtype=np.float32)

        gl.glGenVertexArrays(1, ct.byref(self.vao))
        gl.glGenBuffers(1, ct.byref(self.vbo))

        gl.glBindVertexArray(self.vao.value)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo.value)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            verts.nbytes,
            verts.ctypes.data_as(ct.POINTER(gl.GLfloat)),
            gl.GL_STATIC_DRAW,
        )
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 12, ct.c_void_p(0))
        gl.glBindVertexArray(0)

    def draw(self) -> None:
        gl.glBindVertexArray(self.vao.value)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.vertex_count)
        gl.glBindVertexArray(0)