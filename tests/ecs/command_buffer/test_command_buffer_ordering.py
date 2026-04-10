from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.command_buffer,
    pytest.mark.unit
]


@dataclass
class Counter:
    value: int


@dataclass
class Velocity:
    dx: float
    dy: float


class Player:
    pass


class Dead:
    pass


def test_create_then_add_component_results_in_present_component(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1

    _, (counter,) = rows[0]
    assert counter.value == 10


def test_create_then_add_multiple_components_results_in_all_components(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(1))
    world.defer_add_component(placeholder, Velocity(2.0, 3.0))

    world.apply_commands()

    rows = list(world.query((Counter, Velocity)))
    assert len(rows) == 1

    _, (counter, velocity) = rows[0]
    assert counter.value == 1
    assert velocity.dx == 2.0
    assert velocity.dy == 3.0


def test_create_then_add_tag_results_in_present_tag(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(1))
    world.defer_add_tag(placeholder, Player)

    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert len(rows) == 1

    _, (counter,) = rows[0]
    assert counter.value == 1


def test_add_then_remove_component_same_commit_results_in_absent_component(world) -> None:
    eid = world.create_entity()
    world.defer_add_component(eid, Counter(5))
    world.defer_remove_component(eid, Counter)

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert rows == []


def test_add_then_remove_tag_same_commit_results_in_absent_tag(world) -> None:
    eid = world.create_entity()
    world.defer_add_component(eid, Counter(5))
    world.defer_add_tag(eid, Player)
    world.defer_remove_tag(eid, Player)

    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert rows == []


def test_existing_component_remove_then_add_same_commit_results_in_absent_component(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    world.defer_remove_component(eid, Counter)
    world.defer_add_component(eid, Counter(99))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert rows == []


def test_existing_tag_remove_then_add_same_commit_results_in_absent_tag(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_tag(eid, Player)

    world.defer_remove_tag(eid, Player)
    world.defer_add_tag(eid, Player)

    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert rows == []


def test_destroy_happens_after_component_add_and_removes_entity(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))
    world.defer_destroy_entity(placeholder)

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert rows == []
    assert world.entity_count() == 0


def test_destroy_happens_after_tag_add_and_removes_entity(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))
    world.defer_add_tag(placeholder, Player)
    world.defer_destroy_entity(placeholder)

    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert rows == []
    assert world.entity_count() == 0


def test_create_add_remove_destroy_same_commit_ends_with_no_entity(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))
    world.defer_remove_component(placeholder, Counter)
    world.defer_destroy_entity(placeholder)

    world.apply_commands()

    assert world.entity_count() == 0
    assert list(world.query((Counter,))) == []


def test_multiple_entities_ordering_is_independent(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.defer_add_component(e1, Counter(1))
    world.defer_add_component(e2, Counter(2))
    world.defer_remove_component(e1, Counter)

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1

    eid, (counter,) = rows[0]
    assert eid == e2
    assert counter.value == 2


def test_placeholder_and_real_entity_commands_can_mix_safely(world) -> None:
    real = world.create_entity()
    placeholder = world.defer_create_entity()

    world.defer_add_component(real, Counter(1))
    world.defer_add_component(placeholder, Counter(2))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 2

    values = {counter.value for _, (counter,) in rows}
    assert values == {1, 2}


def test_remove_nonexistent_component_does_not_break_other_buffered_work(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.defer_remove_component(e1, Counter)
    world.defer_add_component(e2, Counter(7))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1

    eid, (counter,) = rows[0]
    assert eid == e2
    assert counter.value == 7


def test_remove_nonexistent_tag_does_not_break_other_buffered_work(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e2, Counter(9))

    world.defer_remove_tag(e1, Player)
    world.defer_add_tag(e2, Player)

    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert len(rows) == 1
    assert rows[0][0] == e2


def test_component_removal_applies_after_multiple_adds_in_same_commit(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(1))
    world.defer_add_component(placeholder, Counter(2))
    world.defer_remove_component(placeholder, Counter)

    world.apply_commands()

    assert list(world.query((Counter,))) == []


def test_tag_removal_applies_after_multiple_adds_in_same_commit(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(1))
    world.defer_add_tag(placeholder, Player)
    world.defer_add_tag(placeholder, Player)
    world.defer_remove_tag(placeholder, Player)

    world.apply_commands()

    assert list(world.query((Counter,), with_tags=(Player,))) == []


def test_destroy_overrides_component_and_tag_presence(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(3))
    world.defer_add_tag(placeholder, Player)
    world.defer_destroy_entity(placeholder)

    world.apply_commands()

    assert list(world.query((Counter,))) == []
    assert list(world.query((Counter,), with_tags=(Player,))) == []
    assert world.entity_count() == 0


def test_ordering_with_existing_entity_add_tag_remove_component(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(4))

    world.defer_add_tag(eid, Player)
    world.defer_remove_component(eid, Counter)

    world.apply_commands()

    assert list(world.query((Counter,), with_tags=(Player,))) == []
    assert list(world.query((Counter,))) == []


def test_ordering_with_existing_entity_add_component_remove_tag(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(4))
    world.add_tag(eid, Player)

    world.defer_add_component(eid, Velocity(1.0, 2.0))
    world.defer_remove_tag(eid, Player)

    world.apply_commands()

    rows = list(world.query((Counter, Velocity)))
    assert len(rows) == 1

    _, (counter, velocity) = rows[0]
    assert counter.value == 4
    assert velocity.dx == 1.0
    assert velocity.dy == 2.0

    assert list(world.query((Counter,), with_tags=(Player,))) == []