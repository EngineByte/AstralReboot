from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.query,
    pytest.mark.unit
]


@dataclass
class Counter:
    value: int


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Velocity:
    dx: float
    dy: float


class Player:
    pass


class Enemy:
    pass


class Dead:
    pass


def test_query_missing_component_store_returns_empty(world) -> None:
    rows = list(world.query((Counter,)))
    assert rows == []


def test_query_missing_one_of_multiple_component_stores_returns_empty(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    rows = list(world.query((Counter, Position)))
    assert rows == []


def test_query_component_store_exists_but_is_empty_returns_empty(world) -> None:
    store = world.stores.get_or_create_component_store(Counter)
    assert len(store) == 0

    rows = list(world.query((Counter,)))
    assert rows == []


def test_query_tag_store_exists_but_has_no_matching_entities_returns_empty(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.stores.get_or_create_tag_store(Player)

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert rows == []


def test_query_requires_all_with_tags(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(1))
    world.add_component(e2, Counter(2))

    world.add_tag(e1, Player)

    world.add_tag(e2, Player)
    world.add_tag(e2, Enemy)

    rows = list(world.query((Counter,), with_tags=(Player, Enemy)))

    assert len(rows) == 1
    eid, (counter,) = rows[0]
    assert eid == e2
    assert counter.value == 2


def test_query_without_tags_excludes_if_any_excluded_tag_present(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()

    world.add_component(e1, Counter(1))
    world.add_component(e2, Counter(2))
    world.add_component(e3, Counter(3))

    world.add_tag(e2, Dead)
    world.add_tag(e3, Enemy)

    rows = list(world.query((Counter,), without_tags=(Dead, Enemy)))

    result = {eid: counter.value for eid, (counter,) in rows}
    assert result == {e1: 1}


def test_query_with_and_without_same_tag_returns_empty(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_tag(eid, Player)

    rows = list(world.query((Counter,), with_tags=(Player,), without_tags=(Player,)))
    assert rows == []


def test_query_after_component_store_becomes_empty_returns_empty(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(1))
    world.add_component(e2, Counter(2))

    world.remove_component(e1, Counter)
    world.remove_component(e2, Counter)

    rows = list(world.query((Counter,)))
    assert rows == []


def test_query_after_tag_removed_no_longer_matches_tag_filter(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_tag(eid, Player)

    before = list(world.query((Counter,), with_tags=(Player,)))
    assert len(before) == 1

    world.remove_tag(eid, Player)

    after = list(world.query((Counter,), with_tags=(Player,)))
    assert after == []


def test_query_materialized_twice_reflects_latest_state(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    query = world.query((Counter,))

    rows1 = list(query)
    assert len(rows1) == 1

    world.remove_component(eid, Counter)

    rows2 = list(query)
    assert rows2 == []


def test_query_result_reflects_in_place_component_mutation(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    rows1 = list(world.query((Counter,)))
    assert len(rows1) == 1
    _, (counter1,) = rows1[0]
    assert counter1.value == 1

    counter1.value = 99

    rows2 = list(world.query((Counter,)))
    assert len(rows2) == 1
    _, (counter2,) = rows2[0]
    assert counter2.value == 99


def test_query_same_entity_in_different_component_orders(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Position(1.0, 2.0))
    world.add_component(eid, Velocity(3.0, 4.0))

    rows_a = list(world.query((Position, Velocity)))
    rows_b = list(world.query((Velocity, Position)))

    assert len(rows_a) == 1
    assert len(rows_b) == 1

    eid_a, (position, velocity) = rows_a[0]
    eid_b, (velocity_b, position_b) = rows_b[0]

    assert eid_a == eid
    assert eid_b == eid

    assert position.x == 1.0
    assert position.y == 2.0
    assert velocity.dx == 3.0
    assert velocity.dy == 4.0

    assert velocity_b.dx == 3.0
    assert velocity_b.dy == 4.0
    assert position_b.x == 1.0
    assert position_b.y == 2.0


def test_query_returns_all_matches_even_if_driver_store_is_not_first_requested(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()

    world.add_component(e1, Counter(1))
    world.add_component(e1, Position(1.0, 1.0))

    world.add_component(e2, Counter(2))
    world.add_component(e2, Position(2.0, 2.0))

    world.add_component(e3, Counter(3))

    rows = list(world.query((Position, Counter)))

    result = {eid: (position.x, counter.value) for eid, (position, counter) in rows}
    assert result == {
        e1: (1.0, 1),
        e2: (2.0, 2),
    }


def test_query_excludes_destroyed_entity(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    before = list(world.query((Counter,)))
    assert len(before) == 1

    world.destroy_entity(eid)

    after = list(world.query((Counter,)))
    assert after == []


def test_query_with_tag_filter_after_destroy_excludes_entity(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_tag(eid, Player)

    before = list(world.query((Counter,), with_tags=(Player,)))
    assert len(before) == 1

    world.destroy_entity(eid)

    after = list(world.query((Counter,), with_tags=(Player,)))
    assert after == []


def test_query_multiple_entities_with_same_components_and_tags(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(10))
    world.add_component(e2, Counter(20))

    world.add_tag(e1, Player)
    world.add_tag(e2, Player)

    rows = list(world.query((Counter,), with_tags=(Player,)))

    result = {eid: counter.value for eid, (counter,) in rows}
    assert result == {
        e1: 10,
        e2: 20,
    }


def test_query_no_match_when_required_tag_missing_after_component_match(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(1))
    world.add_component(e2, Counter(2))
    world.add_tag(e2, Player)

    rows = list(world.query((Counter,), with_tags=(Player,)))

    assert len(rows) == 1
    assert rows[0][0] == e2
    assert rows[0][1][0].value == 2


def test_query_excludes_entities_with_excluded_tag_even_if_required_tags_match(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(1))
    world.add_component(e2, Counter(2))

    world.add_tag(e1, Player)

    world.add_tag(e2, Player)
    world.add_tag(e2, Dead)

    rows = list(world.query((Counter,), with_tags=(Player,), without_tags=(Dead,)))

    assert len(rows) == 1
    assert rows[0][0] == e1
    assert rows[0][1][0].value == 1


def test_query_raises_for_empty_component_tuple(world) -> None:
    try:
        list(world.query(tuple()))
    except ValueError:
        return

    assert False, "Expected ValueError for empty component query."