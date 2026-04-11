from __future__ import annotations

import ctypes as ct
from pathlib import Path

from pyglet import gl
import pyglet


_CUBEMAP_TARGETS = (
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X,
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
)


def load_cubemap(face_paths: tuple[str, str, str, str, str, str]) -> int:
    tex_id = gl.GLuint()
    gl.glGenTextures(1, ct.byref(tex_id))
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, tex_id.value)

    for target, path_str in zip(_CUBEMAP_TARGETS, face_paths):
        path = Path(path_str)
        image = pyglet.image.load(str(path))
        image_data = image.get_data("RGBA", image.width * 4)

        gl.glTexImage2D(
            target,
            0,
            gl.GL_RGBA8,
            image.width,
            image.height,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            ct.c_char_p(image_data),
        )

    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, 0)
    return int(tex_id.value)