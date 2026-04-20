from __future__ import annotations

from typing import Protocol


class RenderBackend(Protocol):
    '''
    Minimal render backend interface for the engine runtime.
    '''

    def initialize(self) -> None:
        '''
        Create GPU-side resources and prepare the backend for rendering.
        '''
        ...

    def begin_frame(self) -> None:
        '''
        Prepare the current frame for rendering.
        '''
        ...

    def end_frame(self) -> None:
        '''
        Finalize the current frame and present it.
        '''
        ...

    def shutdown(self) -> None:
        '''
        Release GPU-side resources.
        '''
        ...