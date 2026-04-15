from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FrameClock:
    frame_index: int = 0
    elapsed_time: float = 0.0
    dt: float = 0.0


@dataclass(slots=True)
class FrameStats:
    alive_entities: int = 0