from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from astralengine.runtime.app_runner import AppController


class AppState(Protocol):
    '''
    Interface for high-level application states.
    '''

    name: str

    def on_enter(self, app: 'AppController') -> None:
        ...

    def update(self, app: 'AppController', dt: float) -> None:
        ...

    def render(self, app: 'AppController') -> None:
        ...

    def on_exit(self, app: 'AppController') -> None:
        ...