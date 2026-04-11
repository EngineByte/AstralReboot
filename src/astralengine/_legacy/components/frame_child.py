from __future__ import annotations

from dataclasses import dataclass

from astralengine.old_code.components.frame_anchor import ROOT_FRAME_EID


@dataclass(slots=True)
class FrameChild:
    frame_eid: int = ROOT_FRAME_EID