from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChunkLoadRequest:
    frame_eid: int
    coord: tuple[int, int, int]
    lod_level: int


@dataclass(slots=True)
class ChunkUnloadRequest:
    frame_eid: int
    coord: tuple[int, int, int]


class ChunkRequestQueue:
    def __init__(self) -> None: ...
    def request_load(self, req: ChunkLoadRequest) -> None: ...
    def request_unload(self, req: ChunkUnloadRequest) -> None: ...
    def pop_loads(self, limit: int) -> list[ChunkLoadRequest]: ...
    def pop_unloads(self, limit: int) -> list[ChunkUnloadRequest]: ...