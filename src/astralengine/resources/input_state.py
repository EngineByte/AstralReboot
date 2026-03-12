from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class InputState:
    enabled: bool = True

    keys_down: set[int] = field(default_factory=set)
    mouse_buttons_down: set[int] = field(default_factory=set)

    mouse_pos: tuple[float, float] = (0.0, 0.0)
    mouse_delta: tuple[float, float] = (0.0, 0.0)

    window: Any | None = None