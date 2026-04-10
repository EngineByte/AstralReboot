from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict, deque
from time import perf_counter
from typing import Iterable, TYPE_CHECKING

from astralengine.ecs.scheduling.system_spec import SystemSpec
from astralengine.ecs.scheduling.phases import PhaseSpec, DEFAULT_PHASES

if TYPE_CHECKING:
    from astralengine.ecs.core.world import ECSWorld


@dataclass(slots=True)
class SystemTiming:
    '''
    Time measure for a system execution.
    '''
    system_name: str
    phase_name: str
    elapsed_sec: float


@dataclass(slots=True)
class PhaseStats:
    '''
    Summary statistics for one phase execution.
    '''
    name: str
    system_count: int
    elapsed_sec: float
    commit_after: bool


class SystemScheduler:
    '''
    ECS system execution scheduler

    Responsibilities:
        - phase graphing
        - system registration
        - system grouping, graphing, and ordering within phases
        - system cadence checks
        - deferred mutation commits at phase boundaries
        - execution timing
    '''

    __slots__ = (
        '_phase_specs',
        '_phase_order',
        '_systems_by_phase',
        '_systems_by_name',
        '_frame_index',
        '_timings',
        '_phase_stats'
    )

    def __init__(self, phases: Iterable[PhaseSpec] | None = None) -> None:
        phase_specs = tuple(phases) if phases is not None else DEFAULT_PHASES

        if not phase_specs:
            raise ValueError('SystemScheduler requires at least one phase.')
        
        self._phase_specs: dict[str, PhaseSpec] = {}
        self._phase_order: list[str] = []
        self._systems_by_phase: dict[str, list[SystemSpec]] = {}
        self._systems_by_name: dict[str, SystemSpec] = {}

        for phase in phase_specs:
            if phase.name in self._phase_specs:
                raise ValueError(f'Duplicate phase name: {phase.name}.')
            
            self._phase_specs[phase.name] = phase
            self._phase_order.append(phase.name)
            self._systems_by_phase[phase.name] = []

        self._frame_index = 0
        self._timings: list[SystemTiming] = []
        self._phase_stats: list[PhaseStats] = []
    
    @property
    def frame_index(self) -> int:
        '''
        Count of completed run_frame() calls.
        '''
        return self._frame_index
    
    def phase_names(self) -> tuple[str, ...]:
        '''
        Returns phase names in execution order.
        '''
        return tuple(self._phase_order)
    
    def phases(self) -> tuple[PhaseSpec, ...]:
        '''
        Returns phase specs in execution order.
        '''
        return tuple(self._phase_specs[name] for name in self._phase_order)
    
    def systems(self) -> tuple[SystemSpec, ...]:
        '''
        Returns all systems in registration order, grouped by phase.
        '''
        out: list[SystemSpec] = []
        for phase_name in self._phase_order:
            out.extend(self._systems_by_phase[phase_name])
        
        return tuple(out)
    
    def timings(self) -> tuple[SystemTiming, ...]:
        '''
        Returns the per-system timings for the most recent frame or phase run.
        '''
        return tuple(self._timings)

    def phase_stats(self) -> tuple[PhaseStats, ...]:
        '''
        Return per-phase stats for the most recent sim frame run.
        '''        
        return tuple(self._phase_stats)

    def add_system(self, spec: SystemSpec) -> None:
        '''
        Register a system into a phase.
        '''
        if spec.phase not in self._phase_specs:
            raise KeyError(f'Unknown phase: {spec.phase}')
        
        if spec.name in self._systems_by_name:
            raise ValueError(f'Duplicate system name: {spec.name}')
        
        self._systems_by_phase[spec.phase].append(spec)
        self._systems_by_name[spec.name] = spec

    def remove_system(self, name: str) -> None:
        '''
        Remove a system by name.
        '''
        try:
            spec = self._systems_by_name.pop(name)
        except KeyError as exc:
            raise KeyError(f'No system named {name!r} is registered.') from exc
        
        phase_systems = self._systems_by_phase[spec.phase]
        self._systems_by_phase[spec.phase] = [
            existing for existing in phase_systems if existing.name != name
        ]
    
    def get_system(self, name: str) -> SystemSpec:
        '''
        Returns a registered system by name.
        '''
        try: 
            return self._systems_by_name[name]
        except KeyError as exc:
            raise KeyError(f'No System named {name!r} is registered.') from exc
        
    def has_system(self, name: str) -> bool:
        '''
        True if system with name is registered.
        '''
        return name in self._systems_by_name
    
    def enable_system(self, name: str) -> None:
        '''
        Enable a registered system.
        '''
        self.get_system(name).enabled = True

    def disable_system(self, name: str) -> None:
        '''
        Disable a registered system.
        '''
        self.get_system(name).enabled = False

    def run_frame(self, world: ECSWorld, dt: float) -> None:
        '''
        Run all phases for one ECS frame.
        '''
        self._frame_index += 1
        self._timings.clear()
        self._phase_stats.clear()

        for phase_name in self._phase_order:
            self._run_phase_internal(world, phase_name, dt)

    def run_phase(self, world: "ECSWorld", phase: str, dt: float) -> None:
        '''
        Runs a single phase against the ECSWorld.

        For debugging, testing, and controlled execution flow.
        '''
        if phase not in self._phase_specs:
            raise KeyError(f'Unknown phase: {phase}')
        
        self._timings.clear()
        self._phase_stats.clear()
        self._run_phase_internal(world, phase, dt)

    def _run_phase_internal(self, world: ECSWorld, phase_name: str, dt: float) -> None:
        phase = self._phase_specs[phase_name]
        ordered_systems = self._resolve_phase_order(phase_name)

        phase_start = perf_counter()
        ran_count = 0

        for spec in ordered_systems:
            if not spec.enabled:
                continue

            if not self._should_run_this_frame(spec):
                continue

            t0 = perf_counter()
            spec.fn(world, dt)
            elapsed = perf_counter() - t0

            self._timings.append(
                SystemTiming(
                    system_name=spec.name,
                    phase_name=phase_name,
                    elapsed_sec=elapsed
                )
            )
            ran_count += 1

        if phase.commit_after:
            world.apply_commands()

        phase_elapsed = perf_counter() - phase_start
        self._phase_stats.append(
            PhaseStats(
                name=phase_name,
                system_count=ran_count,
                elapsed_sec=phase_elapsed,
                commit_after=phase.commit_after
            )
        )

    def _should_run_this_frame(self, spec: SystemSpec) -> bool:
        '''
        True if a system's cadence allows for it to run in the current sim frame.
        '''
        return (self._frame_index % spec.run_every) == 0
    
    def _resolve_phase_order(self, phase_name: str) -> tuple[SystemSpec, ...]:
        '''
        Resolve the ordering within a phase.

        Dependencies are only applied within the same phase.
        '''
        systems = self._systems_by_phase[phase_name]
        if len(systems) < 2:
            return tuple(systems)
        
        systems_by_name = {spec.name: spec for spec in systems}
        edges: dict[str, set[str]] = defaultdict(set)
        indegree: dict[str, int] = {spec.name: 0 for spec in systems}

        for spec in systems:
            for dep_name in spec.after:
                if dep_name not in systems_by_name:
                    continue

                if spec.name not in edges[dep_name]:
                    edges[dep_name].add(spec.name)
                    indegree[spec.name] += 1

        for spec in systems:
            for dep_name in spec.before:
                if dep_name not in systems_by_name:
                    continue

                if dep_name not in edges[spec.name]:
                    edges[spec.name].add(dep_name)
                    indegree[dep_name] += 1

        registration_order = [spec.name for spec in systems]
        ready = deque(
            name for name in registration_order if indegree[name] == 0
        )

        ordered_names: list[str] = []

        while ready:
            name = ready.popleft()
            ordered_names.append(name)

            for nxt in registration_order:
                if nxt in edges[name]:
                    indegree[nxt] -= 1
                    if indegree[nxt] == 0:
                        ready.append(nxt)

        if len(ordered_names) != len(systems):
            cycle_members = [name for name, degree in indegree.items() if degree > 0]
            raise ValueError(
                f'Cyclic system dependency detected in phase {phase_name!r}: '
                f'{cycle_members}'
            )
        
        return tuple(systems_by_name[name] for name in ordered_names)