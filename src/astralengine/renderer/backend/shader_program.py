from __future__ import annotations

import ctypes as ct
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
from pyglet import gl


Mat4 = npt.NDArray[np.float32]


def _read_shader_log(shader: int) -> str:
    log_len = gl.GLint()
    gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, ct.byref(log_len))
    if log_len.value <= 1:
        return ""
    buf = ct.create_string_buffer(log_len.value)
    gl.glGetShaderInfoLog(shader, log_len, None, buf)
    return buf.value.decode("utf-8", errors="replace")


def _read_program_log(program: int) -> str:
    log_len = gl.GLint()
    gl.glGetProgramiv(program, gl.GL_INFO_LOG_LENGTH, ct.byref(log_len))
    if log_len.value <= 1:
        return ""
    buf = ct.create_string_buffer(log_len.value)
    gl.glGetProgramInfoLog(program, log_len, None, buf)
    return buf.value.decode("utf-8", errors="replace")


def compile_shader(source: str, shader_type: int, *, label: str = "") -> int:
    shader = gl.glCreateShader(shader_type)

    src_bytes = source.encode("utf-8")
    src_buf = ct.create_string_buffer(src_bytes)
    src_ptr = ct.cast(ct.pointer(ct.pointer(src_buf)), ct.POINTER(ct.POINTER(ct.c_char)))
    length = gl.GLint(len(src_bytes))

    gl.glShaderSource(shader, 1, src_ptr, ct.byref(length))
    gl.glCompileShader(shader)

    status = gl.GLint()
    gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, ct.byref(status))
    if not status.value:
        log = _read_shader_log(shader)
        gl.glDeleteShader(shader)
        raise RuntimeError(f"Shader compile failed [{label}]:\n{log}")

    return shader


def link_program(*shader_ids: int, label: str = "") -> int:
    program = gl.glCreateProgram()
    for sid in shader_ids:
        gl.glAttachShader(program, sid)

    gl.glLinkProgram(program)

    status = gl.GLint()
    gl.glGetProgramiv(program, gl.GL_LINK_STATUS, ct.byref(status))
    if not status.value:
        log = _read_program_log(program)
        for sid in shader_ids:
            gl.glDetachShader(program, sid)
            gl.glDeleteShader(sid)
        gl.glDeleteProgram(program)
        raise RuntimeError(f"Program link failed [{label}]:\n{log}")

    for sid in shader_ids:
        gl.glDetachShader(program, sid)
        gl.glDeleteShader(sid)

    return program


@dataclass(slots=True)
class ShaderProgram:
    """
    Linked GL shader program with cached uniform locations.
    """
    program_id: int
    name: str
    _uniform_cache: dict[str, int] = field(default_factory=dict)

    def use(self) -> None:
        gl.glUseProgram(self.program_id)

    def uniform_location(self, name: str) -> int:
        loc = self._uniform_cache.get(name)
        if loc is not None:
            return loc

        loc = gl.glGetUniformLocation(self.program_id, name.encode("utf-8"))
        self._uniform_cache[name] = int(loc)
        return int(loc)

    def set_mat4(self, name: str, value: Mat4) -> None:
        loc = self.uniform_location(name)
        if loc < 0:
            return
        arr = np.asarray(value, dtype=np.float32)
        gl.glUniformMatrix4fv(
            loc,
            1,
            gl.GL_FALSE,
            arr.flatten("F").ctypes.data_as(ct.POINTER(gl.GLfloat)),
        )

    def set_vec3(self, name: str, value: tuple[float, float, float]) -> None:
        loc = self.uniform_location(name)
        if loc < 0:
            return
        gl.glUniform3f(loc, float(value[0]), float(value[1]), float(value[2]))

    def set_float(self, name: str, value: float) -> None:
        loc = self.uniform_location(name)
        if loc < 0:
            return
        gl.glUniform1f(loc, float(value))

    def set_int(self, name: str, value: int) -> None:
        loc = self.uniform_location(name)
        if loc < 0:
            return
        gl.glUniform1i(loc, int(value))

    def delete(self) -> None:
        if self.program_id:
            gl.glDeleteProgram(self.program_id)
            self.program_id = 0