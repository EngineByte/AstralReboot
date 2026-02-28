from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

from ecs.entity_allocator import EntityId

Float3 = npt.NDArray[np.float32]


@dataclass(slots=True)
class ParentFollow:
    parent: EntityId
    offset: Float3