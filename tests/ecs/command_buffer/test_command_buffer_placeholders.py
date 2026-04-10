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
class Lifetime:
    ticks: int


class Player:
    pass


def test_placeholder_entity_is_negative_id(world) -> None:
    placeholder = world.defer_create_entity()

    assert isinstance(placeholder, int)
    assert placeholder < 0


def test_placeholder_resolves_to_real_entity_on_apply(world) -> None:
    placeholder = world.defer_create_entity()

    world.apply_commands()

    # We can't assume exact ID, but entity count should increase
    assert world.entity_count() == 1


def test_placeholder_with_component_resolves_correctly(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1

    eid, (counter,) = rows[0]
    assert counter.value == 10
    assert eid >= 0  # real entity


def test_placeholder_with_multiple_components(world) -> None:
    placeholder = world.defer_create_entity()

    world.defer_add_component(placeholder, Counter(5))
    world.defer_add_component(placeholder, Lifetime(3))

    world.apply_commands()

    rows = list(world.query((Counter, Lifetime)))
    assert len(rows) == 1

    _, (counter, lifetime) = rows[0]
    assert counter.value == 5
    assert lifetime.ticks == 3


def test_placeholder_with_tag(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_tag(placeholder, Player)

    world.apply_commands()

    rows = list(world.query(tuple())) if False else []  # avoid empty query
    # instead check via registry behavior
    # safer approach: use a component to confirm existence

    # so combine tag + component
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(1))
    world.defer_add_tag(placeholder, Player)

    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert len(rows) == 1


def test_multiple_placeholders_resolve_to_distinct_entities(world) -> None:
    p1 = world.defer_create_entity()
    p2 = world.defer_create_entity()

    world.defer_add_component(p1, Counter(1))
    world.defer_add_component(p2, Counter(2))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 2

    values = {c.value for _, (c,) in rows}
    assert values == {1, 2}


def test_placeholder_can_be_destroyed_before_commit(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_destroy_entity(placeholder)

    world.apply_commands()

    assert world.entity_count() == 0


def test_placeholder_destroy_after_component_add(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))
    world.defer_destroy_entity(placeholder)

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert rows == []


def test_placeholder_operations_order_is_respected(world) -> None:
    placeholder = world.defer_create_entity()

    world.defer_add_component(placeholder, Counter(1))
    world.defer_remove_component(placeholder, Counter)

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert rows == []


def test_placeholder_can_add_then_remove_tag(world) -> None:
    placeholder = world.defer_create_entity()

    world.defer_add_tag(placeholder, Player)
    world.defer_remove_tag(placeholder, Player)

    world.apply_commands()

    # validate by combining with component
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(1))
    world.defer_add_tag(placeholder, Player)
    world.defer_remove_tag(placeholder, Player)

    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert rows == []


def test_placeholder_ids_do_not_leak_after_commit(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(5))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1

    eid, _ = rows[0]

    assert eid >= 0
    assert eid != placeholder  # placeholder must not survive


def test_nested_placeholders_do_not_conflict(world) -> None:
    p1 = world.defer_create_entity()
    p2 = world.defer_create_entity()

    world.defer_add_component(p1, Counter(1))
    world.defer_add_component(p2, Counter(2))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 2

    ids = {eid for eid, _ in rows}
    assert all(eid >= 0 for eid in ids)
    assert len(ids) == 2


def test_placeholder_can_be_used_across_multiple_commands(world) -> None:
    p = world.defer_create_entity()

    world.defer_add_component(p, Counter(1))
    world.defer_add_component(p, Lifetime(2))
    world.defer_add_tag(p, Player)

    world.apply_commands()

    rows = list(world.query((Counter, Lifetime), with_tags=(Player,)))
    assert len(rows) == 1

    _, (counter, lifetime) = rows[0]
    assert counter.value == 1
    assert lifetime.ticks == 2