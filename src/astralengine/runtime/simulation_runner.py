from __future__ import annotations

import logging
from time import perf_counter, sleep
from typing import Sequence

from astralengine.app.logging_setup import get_logger
from astralengine.bootstrap.simulation import SimulationSession


def _run_phases(world, phases: Sequence[str], dt: float) -> None:
    for phase in phases:
        world.run_phase(phase, dt)


class SimulationRunner:
    '''
    Executes one simulation session.
    '''

    def __init__(self, session: SimulationSession) -> None:
        self._session = session
        self._logger = get_logger('runtime.simulation')
        self._started = False
        self._frame_index = 0

    @property
    def frame_index(self) -> int:
        return self._frame_index

    def startup(self) -> None:
        if self._started:
            return

        _run_phases(
            self._session.world,
            self._session.config.startup_phases,
            0.0,
        )
        self._started = True
        self._logger.info('Simulation session startup complete.')

    def run_one_frame(self) -> None:
        if not self._started:
            self.startup()

        cfg = self._session.config
        frame_start = perf_counter()

        self._session.world.run_frame(cfg.fixed_dt)
        self._frame_index += 1

        frame_duration = cfg.frame_duration
        if frame_duration is not None:
            elapsed = perf_counter() - frame_start
            remaining = frame_duration - elapsed
            if remaining > 0.0:
                sleep(remaining)

    def shutdown(self) -> None:
        if not self._started:
            return

        try:
            _run_phases(
                self._session.world,
                self._session.config.shutdown_phases,
                0.0,
            )
        except Exception:
            logging.getLogger('astralengine.runtime.simulation').exception(
                'Unhandled exception during simulation shutdown.'
            )
            raise
        finally:
            self._logger.info(
                'Simulation session shutdown after %d frame(s).',
                self._frame_index,
            )
            self._started = False