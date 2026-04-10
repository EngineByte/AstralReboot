from __future__ import annotations

from dataclasses import dataclass

import pytest

from astralengine.ecs.core.world import ECSWorld
from astralengine.ecs.scheduling.phases import PhaseSpec
from astralengine.ecs.scheduling.scheduler import SystemScheduler
from astralengine.ecs.scheduling.system_spec import SystemSpec

pytestmark = [pytest.mark.ecs, pytest.mark.integration]


@dataclass
class Counter:
    value: int


def test_spawned_entity_not_visible_to_later_system_in_same_phase_before_commit() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=True),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    seen_counts: list[int] = []

    def system_spawn(world, dt: float) -> None:
        placeholder = world.defer_create_entity()
        world.defer_add_component(placeholder, Counter(1))

    def system_observe(world, dt: float) -> None:
        seen_counts.append(len(list(world.query((Counter,)))))

    world.add_system(
        SystemSpec(
            name="spawn",
            fn=system_spawn,
            phase="sim",
        )
    )
    world.add_system(
        SystemSpec(
            name="observe",
            fn=system_observe,
            phase="sim",
            after=("spawn",),
        )
    )

    world.run_phase("sim", 1.0)

    assert seen_counts == [0]
    rows = list(world.query((Counter,)))
    assert len(rows) == 1


def test_spawned_entity_becomes_visible_in_next_phase_after_commit_barrier() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=True),
            PhaseSpec(name="post_sim", commit_after=True),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    seen_counts: list[int] = []

    def system_spawn(world, dt: float) -> None:
        placeholder = world.defer_create_entity()
        world.defer_add_component(placeholder, Counter(1))

    def system_observe(world, dt: float) -> None:
        seen_counts.append(len(list(world.query((Counter,)))))

    world.add_system(
        SystemSpec(
            name="spawn",
            fn=system_spawn,
            phase="sim",
        )
    )
    world.add_system(
        SystemSpec(
            name="observe",
            fn=system_observe,
            phase="post_sim",
        )
    )

    world.run_frame(1.0)

    assert seen_counts == [1]


def test_deferred_destroy_not_visible_to_later_system_in_same_phase_before_commit() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=True),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    seen_counts: list[int] = []

    def system_destroy(world, dt: float) -> None:
        for entity, (_counter,) in world.query((Counter,)):
            world.defer_destroy_entity(entity)

    def system_observe(world, dt: float) -> None:
        seen_counts.append(len(list(world.query((Counter,)))))

    world.add_system(
        SystemSpec(
            name="destroy",
            fn=system_destroy,
            phase="sim",
        )
    )
    world.add_system(
        SystemSpec(
            name="observe",
            fn=system_observe,
            phase="sim",
            after=("destroy",),
        )
    )

    world.run_phase("sim", 1.0)

    assert seen_counts == [1]
    assert list(world.query((Counter,))) == []


def test_deferred_component_add_not_visible_until_commit() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=True),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    eid = world.create_entity()

    seen_counts: list[int] = []

    def system_add_component(world, dt: float) -> None:
        world.defer_add_component(eid, Counter(1))

    def system_observe(world, dt: float) -> None:
        seen_counts.append(len(list(world.query((Counter,)))))

    world.add_system(
        SystemSpec(
            name="add_component",
            fn=system_add_component,
            phase="sim",
        )
    )
    world.add_system(
        SystemSpec(
            name="observe",
            fn=system_observe,
            phase="sim",
            after=("add_component",),
        )
    )

    world.run_phase("sim", 1.0)

    assert seen_counts == [0]
    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    assert rows[0][0] == eid


def test_deferred_component_remove_not_visible_until_commit() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=True),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    seen_counts: list[int] = []

    def system_remove_component(world, dt: float) -> None:
        world.defer_remove_component(eid, Counter)

    def system_observe(world, dt: float) -> None:
        seen_counts.append(len(list(world.query((Counter,)))))

    world.add_system(
        SystemSpec(
            name="remove_component",
            fn=system_remove_component,
            phase="sim",
        )
    )
    world.add_system(
        SystemSpec(
            name="observe",
            fn=system_observe,
            phase="sim",
            after=("remove_component",),
        )
    )

    world.run_phase("sim", 1.0)

    assert seen_counts == [1]
    assert list(world.query((Counter,))) == []


def test_no_commit_after_phase_keeps_deferred_spawn_invisible_until_manual_apply() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=False),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    def system_spawn(world, dt: float) -> None:
        placeholder = world.defer_create_entity()
        world.defer_add_component(placeholder, Counter(1))

    world.add_system(
        SystemSpec(
            name="spawn",
            fn=system_spawn,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.0)

    assert list(world.query((Counter,))) == []

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1


def test_no_commit_after_phase_keeps_deferred_destroy_invisible_until_manual_apply() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="sim", commit_after=False),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    def system_destroy(world, dt: float) -> None:
        world.defer_destroy_entity(eid)

    world.add_system(
        SystemSpec(
            name="destroy",
            fn=system_destroy,
            phase="sim",
        )
    )

    world.run_phase("sim", 1.0)

    rows_before = list(world.query((Counter,)))
    assert len(rows_before) == 1

    world.apply_commands()

    assert list(world.query((Counter,))) == []


def test_same_frame_later_phase_sees_committed_changes_from_earlier_phase() -> None:
    scheduler = SystemScheduler(
        phases=(
            PhaseSpec(name="pre_sim", commit_after=True),
            PhaseSpec(name="sim", commit_after=True),
        )
    )
    world = ECSWorld()
    world.bind_scheduler(scheduler)

    seen_counts: list[int] = []

    def system_spawn(world, dt: float) -> None:
        placeholder = world.defer_create_entity()
        world.defer_add_component(placeholder, Counter(1))

    def system_observe(world, dt: float) -> None:
        seen_counts.append(len(list(world.query((Counter,)))))

    world.add_system(
        SystemSpec(
            name="spawn",
            fn=system_spawn,
            phase="pre_sim",
        )
    )
    world.add_system(
        SystemSpec(
            name="observe",
            fn=system_observe,
            phase="sim",
        )
    )

    world.run_frame(1.0)

    assert seen_counts == [1]