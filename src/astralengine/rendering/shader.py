from __future__ import annotations

import ctypes as ct

from pyglet import gl


def compile_shader(source_bytes: bytes, shader_type: int) -> gl.GLuint:
    '''
    Compile a GLSL shader and return its OpenGL handle.
    '''
    shader = gl.glCreateShader(shader_type)

    source_c = ct.create_string_buffer(source_bytes)
    source_ptr = ct.cast(ct.pointer(ct.pointer(source_c)), ct.POINTER(ct.POINTER(gl.GLchar)))
    source_len = gl.GLint(len(source_bytes))

    gl.glShaderSource(shader, 1, source_ptr, source_len)
    gl.glCompileShader(shader)

    compile_ok = gl.GLint(0)
    gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ct.byref(compile_ok))
    if compile_ok.value != gl.GL_TRUE:
        log_len = gl.GLint(0)
        gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ct.byref(log_len))

        if log_len.value > 0:
            buffer = (ct.c_char * log_len.value)()
            gl.glGetShaderInfoLog(shader, log_len, None, buffer)
            message = bytes(buffer).rstrip(b'\x00').decode(
                'utf-8',
                errors='replace',
            )
        else:
            message = 'unknown shader compilation error'

        raise RuntimeError(f'Shader compile failed: {message}')

    return shader


def link_program(vertex_shader: gl.GLuint, fragment_shader: gl.GLuint) -> gl.GLuint:
    '''
    Link a vertex/fragment shader pair into a program and return its handle.
    '''
    program = gl.glCreateProgram()
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)

    link_ok = gl.GLint(0)
    gl.glGetProgramiv(program, gl.GL_LINK_STATUS, ct.byref(link_ok))
    if link_ok.value != gl.GL_TRUE:
        log_len = gl.GLint(0)
        gl.glGetProgramiv(program, gl.GL_INFO_LOG_LENGTH, ct.byref(log_len))

        if log_len.value > 0:
            buffer = (ct.c_char * log_len.value)()
            gl.glGetProgramInfoLog(program, log_len, None, buffer)
            message = bytes(buffer).rstrip(b'\x00').decode(
                'utf-8',
                errors='replace',
            )
        else:
            message = 'unknown program link error'

        raise RuntimeError(f'Program link failed: {message}')

    return program


class ShaderProgram:
    '''
    Small wrapper around an OpenGL shader program.
    '''

    __slots__ = ('_program',)

    def __init__(self, vertex_source: bytes, fragment_source: bytes) -> None:
        vertex_shader = compile_shader(vertex_source, gl.GL_VERTEX_SHADER)
        fragment_shader = compile_shader(fragment_source, gl.GL_FRAGMENT_SHADER)

        try:
            self._program = link_program(vertex_shader, fragment_shader)
        finally:
            gl.glDeleteShader(vertex_shader)
            gl.glDeleteShader(fragment_shader)

    @property
    def handle(self) -> gl.GLuint:
        return self._program

    def use(self) -> None:
        gl.glUseProgram(self._program)

    def stop(self) -> None:
        gl.glUseProgram(0)

    def delete(self) -> None:
        if self._program is not None:
            gl.glDeleteProgram(self._program)
            self._program = gl.GLuint(0)