from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FrameSettings:
    enable_rebasing: bool = True
    max_rebase_distance: float = 2048.0