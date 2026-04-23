from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Parent:
    '''
    Simple parent reference for scene hierarchy.
    '''
    parent: int