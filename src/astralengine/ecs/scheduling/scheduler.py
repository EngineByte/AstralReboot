from __future__ import annotations

from typing import Dict, List, Tuple, TYPE_CHECKING

from astralengine.ecs.scheduling.system_spec import SystemSpec

if TYPE_CHECKING:
    from astralengine.ecs.core.world import ECSWorld


class SystemScheduler:
    def __init__(self) -> None:
        self._phases: Dict[str, List[SystemSpec]] = {}
        self._insertion_counter: int = 0

        self._sorted_cache: Dict[str, List[SystemSpec]] = {}
        self._dirty: Dict[str, bool] = {}

    def add_phase(self, name: str) -> None:
        if name in self._phases:
            return
        self._phases[name] = []
        self._sorted_cache[name] = []
        self._dirty[name] = True

    def phases(self) -> Tuple[str, ...]:
        return tuple(self._phases.keys())

    def add_system(self, spec: SystemSpec) -> None:
        phase = spec.phase
        if phase not in self._phases:
            self.add_phase(phase)

        self._phases[phase].append(spec)
        self._insertion_counter += 1
        self._dirty[phase] = True

    def remove_system(self, phase: str, name: str) -> bool:
        if phase not in self._phases:
            return False

        lst = self._phases[phase]
        for i, spec in enumerate(lst):
            if spec.system_name() == name:
                del lst[i]
                self._dirty[phase] = True
                return True
        return False

    def clear_phase(self, phase: str) -> None:
        if phase in self._phases:
            self._phases[phase].clear()
            self._dirty[phase] = True

    def set_enabled(self, phase: str, name: str, enabled: bool) -> bool:
        if phase not in self._phases:
            return False

        lst = self._phases[phase]
        for i, spec in enumerate(lst):
            if spec.system_name() == name:
                lst[i] = SystemSpec(
                    func=spec.func,
                    phase=spec.phase,
                    order=spec.order,
                    name=spec.name,
                    enabled=enabled,
                    before=spec.before,
                    after=spec.after,
                )
                self._dirty[phase] = True
                return True
        return False

    def run_phase(self, phase: str, world: "ECSWorld") -> None:
        if phase not in self._phases:
            return

        systems = self._get_sorted_phase(phase)
        dt = getattr(world, "dt_seconds", 0.0)

        for spec in systems:
            if not spec.enabled:
                continue
            spec.func(world, dt)

    def run(self, world: "ECSWorld") -> None:
        for phase in self.phases():
            self.run_phase(phase, world)

    def _get_sorted_phase(self, phase: str) -> List[SystemSpec]:
        if not self._dirty.get(phase, True):
            return self._sorted_cache[phase]

        lst = self._phases[phase]
        sorted_lst = sorted(lst, key=lambda s: s.order)

        self._sorted_cache[phase] = sorted_lst
        self._dirty[phase] = False
        return sorted_lst

    def stats(self) -> Dict[str, object]:
        return {
            "phases": {
                phase: [s.system_name() for s in self._get_sorted_phase(phase)]
                for phase in self._phases.keys()
            }
        }