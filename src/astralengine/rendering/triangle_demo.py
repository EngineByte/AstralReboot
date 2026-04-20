from __future__ import annotations

from ctypes import byref, c_float, c_void_p, sizeof

from pyglet import gl

from astralengine.rendering.shader import ShaderProgram


_VERTEX_SOURCE = b'''
#version 330 core
layout (location = 0) in vec2 a_pos;
layout (location = 1) in vec3 a_color;

out vec3 v_color;

void main()
{
    gl_Position = vec4(a_pos, 0.0, 1.0);
    v_color = a_color;
}
'''

_FRAGMENT_SOURCE = b'''
#version 330 core
in vec3 v_color;
out vec4 frag_color;

void main()
{
    frag_color = vec4(v_color, 1.0);
}
'''


class TriangleDemo:
    '''
    Hardcoded first-triangle demo pipeline.

    Owns:
    - shader program
    - one VAO
    - one VBO
    '''

    __slots__ = (
        '_program',
        '_vao',
        '_vbo',
        '_initialized',
    )

    def __init__(self) -> None:
        self._program: ShaderProgram | None = None
        self._vao = gl.GLuint(0)
        self._vbo = gl.GLuint(0)
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        self._program = ShaderProgram(_VERTEX_SOURCE, _FRAGMENT_SOURCE)

        vertices = (
            c_float * 15
        )(
             0.0,  0.5, 1.0, 0.0, 0.0,
            -0.5, -0.5, 0.0, 1.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0,
        )

        gl.glGenVertexArrays(1, byref(self._vao))
        gl.glGenBuffers(1, byref(self._vbo))

        gl.glBindVertexArray(self._vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            sizeof(vertices),
            vertices,
            gl.GL_STATIC_DRAW,
        )

        stride = 5 * sizeof(c_float)

        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(
            1,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            stride,
            c_void_p(2 * sizeof(c_float)),
        )
        gl.glEnableVertexAttribArray(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        self._initialized = True

    def draw(self) -> None:
        if not self._initialized:
            self.initialize()

        if self._program is None:
            raise RuntimeError('TriangleDemo shader program is not initialized.')

        self._program.use()
        gl.glBindVertexArray(self._vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        gl.glBindVertexArray(0)
        self._program.stop()

    def shutdown(self) -> None:
        if self._vbo.value:
            gl.glDeleteBuffers(1, byref(self._vbo))
            self._vbo = gl.GLuint(0)

        if self._vao.value:
            gl.glDeleteVertexArrays(1, byref(self._vao))
            self._vao = gl.GLuint(0)

        if self._program is not None:
            self._program.delete()
            self._program = None

        self._initialized = False