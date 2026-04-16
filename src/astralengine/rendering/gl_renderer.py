from __future__ import annotations

import ctypes as ct
from pyglet import gl


class GLRenderer:
    '''
    Minimal OpenGL renderer for a single triangle demo.
    '''

    __slots__ = (
        '_window',
        '_program',
        '_vao',
        '_vbo',
        '_initialized',
    )

    def __init__(self, window) -> None:
        self._window = window
        self._program = gl.GLuint(0)
        self._vao = gl.GLuint(0)
        self._vbo = gl.GLuint(0)
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        self._window.switch_to()
        self._window.set_viewport()

        vertex_source = b'''
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

        fragment_source = b'''
        #version 330 core
        in vec3 v_color;
        out vec4 frag_color;

        void main()
        {
            frag_color = vec4(v_color, 1.0);
        }
        '''

        vertex_shader = self._compile_shader(vertex_source, gl.GL_VERTEX_SHADER)
        fragment_shader = self._compile_shader(fragment_source, gl.GL_FRAGMENT_SHADER)

        self._program = gl.glCreateProgram()
        gl.glAttachShader(self._program, vertex_shader)
        gl.glAttachShader(self._program, fragment_shader)
        gl.glLinkProgram(self._program)

        link_ok = gl.GLint(0)
        gl.glGetProgramiv(self._program, gl.GL_LINK_STATUS, link_ok)
        if link_ok.value != gl.GL_TRUE:
            log_len = gl.GLint(0)
            gl.glGetProgramiv(self._program, gl.GL_INFO_LOG_LENGTH, log_len)
            buffer = ct.create_string_buffer(max(1, log_len.value))
            gl.glGetProgramInfoLog(self._program, log_len, None, buffer)
            raise RuntimeError(f'Program link failed: {buffer.value.decode('utf-8')}')

        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

        vertices = (
            ct.c_float * 15
        )(
            0.0,  0.5, 1.0, 0.0, 0.0,
           -0.5, -0.5, 0.0, 1.0, 0.0,
            0.5, -0.5, 0.0, 0.0, 1.0,
        )

        gl.glGenVertexArrays(1, self._vao)
        gl.glGenBuffers(1, self._vbo)

        gl.glBindVertexArray(self._vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            ct.sizeof(vertices),
            ct.cast(vertices, ct.c_void_p),
            gl.GL_STATIC_DRAW,
        )

        stride = 5 * ct.sizeof(ct.c_float)

        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, stride, ct.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(
            1,
            3,
            gl.GL_FLOAT,
            gl.GL_FALSE,
            stride,
            ct.c_void_p(2 * ct.sizeof(ct.c_float)),
        )
        gl.glEnableVertexAttribArray(1)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

        self._initialized = True

    def begin_frame(self) -> None:
        self._window.switch_to()
        self._window.set_viewport()
        gl.glClearColor(0.08, 0.08, 0.12, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def render_demo_triangle(self) -> None:
        if not self._initialized:
            self.initialize()

        gl.glUseProgram(self._program)
        gl.glBindVertexArray(self._vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)

    def end_frame(self) -> None:
        self._window.swap_buffers()

    def shutdown(self) -> None:
        self._window.switch_to()

        if self._vbo.value:
            gl.glDeleteBuffers(1, self._vbo)
            self._vbo = gl.GLuint(0)

        if self._vao.value:
            gl.glDeleteVertexArrays(1, self._vao)
            self._vao = gl.GLuint(0)

        if self._program is not None:
            gl.glDeleteProgram(self._program)
            self._program = gl.GLuint(0)

        self._initialized = False

    def _compile_shader(self, source: bytes, shader_type: int) -> gl.GLuint:
        shader = gl.glCreateShader(shader_type)

        source_bytes = source
        source_buff = ct.create_string_buffer(source_bytes)
        source_ptr = ct.cast(ct.pointer(ct.pointer(source_buff)), ct.POINTER(ct.POINTER(gl.GLchar)))
        length = gl.GLint(len(source_bytes))

        gl. glShaderSource(shader, 1, source_ptr, ct.byref(length))
        gl.glCompileShader(shader)

        compile_ok = gl.GLint(0)
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ct.byref(compile_ok))
        if compile_ok.value != gl.GL_TRUE:
            log_len = gl.GLint(0)
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ct.byref(log_len))

            if log_len.value > 0:
                buffer = (ct.c_char * log_len.value)()
                gl.glGetShaderInfoLog(shader, log_len, None, buffer)
                message = bytes(buffer).rstrip(b'\x00').decode('utf-8', errors='replace')
            else:
                message = 'unknown shader error'

            raise RuntimeError(f'Shader compile failed: {message}')

        return shader