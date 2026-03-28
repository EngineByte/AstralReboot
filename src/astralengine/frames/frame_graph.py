from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FrameNode:
    frame_eid: int
    parent_frame_eid: int


class FrameGraph:
    def __init__(self) -> None: ...
    def bind(self, frame_eid: int, parent_frame_eid: int) -> None: ...
    def unbind(self, frame_eid: int) -> None: ...
    def parent_of(self, frame_eid: int) -> int | None: ...
    def has_frame(self, frame_eid: int) -> bool: ...