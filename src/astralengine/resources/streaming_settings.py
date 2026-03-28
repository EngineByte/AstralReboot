from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StreamingSettings:
    chunk_load_radius: int = 8
    chunk_active_radius: int = 6
    chunk_visible_radius: int = 5
    chunk_unload_radius: int = 10
    max_stream_ops_per_frame: int = 16