from __future__ import annotations

from dataclasses import dataclass

from astralengine.flow.app_state import AppState


@dataclass(slots=True)
class StateMachine:
    '''
    Simple single-active-state machine.
    '''
    _current: AppState | None = None

    @property
    def current(self) -> AppState | None:
        return self._current

    def change_state(self, app, new_state: AppState) -> None:
        if self._current is not None:
            self._current.on_exit(app)

        self._current = new_state
        self._current.on_enter(app)

    def update(self, app, dt: float) -> None:
        if self._current is None:
            raise RuntimeError('No active application state.')
        self._current.update(app, dt)

    def render(self, app) -> None:
        if self._current is None:
            raise RuntimeError('No active application state.')
        self._current.render(app)