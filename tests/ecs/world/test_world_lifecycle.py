from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.world,
    pytest.mark.unit
]


@dataclass
class Counter:
    value: int


class Player:
    pass


def test_create_entity_returns_alive_entity(world) -> None:
    eid = world.create_entity()

    assert world.is_alive(eid) is True


def test_create_multiple_entities_returns_distinct_entities(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()

    assert e1 != e2
    assert e1 != e3
    assert e2 != e3

    assert world.is_alive(e1) is True
    assert world.is_alive(e2) is True
    assert world.is_alive(e3) is True


def test_entity_count_increases_on_create(world) -> None:
    assert world.entity_count() == 0

    e1 = world.create_entity()
    assert world.entity_count() == 1
    assert world.is_alive(e1)

    e2 = world.create_entity()
    assert world.entity_count() == 2
    assert world.is_alive(e2)


def test_destroy_entity_marks_entity_not_alive(world) -> None:
    eid = world.create_entity()

    world.destroy_entity(eid)

    assert world.is_alive(eid) is False


def test_entity_count_decreases_on_destroy(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    assert world.entity_count() == 2

    world.destroy_entity(e1)
    assert world.entity_count() == 1

    world.destroy_entity(e2)
    assert world.entity_count() == 0


def test_destroy_entity_removes_components(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(10))

    assert list(world.query((Counter,))) != []

    world.destroy_entity(eid)

    assert list(world.query((Counter,))) == []
    assert world.get_component(eid, Counter) is None


def test_destroy_entity_removes_tags(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_tag(eid, Player)

    assert len(list(world.query((Counter,), with_tags=(Player,)))) == 1

    world.destroy_entity(eid)

    assert list(world.query((Counter,), with_tags=(Player,))) == []


def test_destroy_one_entity_does_not_affect_other_entities(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(1))
    world.add_component(e2, Counter(2))

    world.destroy_entity(e1)

    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    assert rows[0][0] == e2
    assert rows[0][1][0].value == 2


def test_create_after_destroy_produces_alive_entity(world) -> None:
    e1 = world.create_entity()
    world.destroy_entity(e1)

    e2 = world.create_entity()

    assert world.is_alive(e1) is False
    assert world.is_alive(e2) is True
    assert world.entity_count() == 1


def test_many_create_destroy_cycles_keep_world_consistent(world) -> None:
    created = [world.create_entity() for _ in range(10)]
    assert world.entity_count() == 10

    for eid in created[:5]:
        world.destroy_entity(eid)

    assert world.entity_count() == 5

    for eid in created[:5]:
        assert world.is_alive(eid) is False

    for eid in created[5:]:
        assert world.is_alive(eid) is True

    new_entities = [world.create_entity() for _ in range(3)]
    assert world.entity_count() == 8

    for eid in new_entities:
        assert world.is_alive(eid) is True


def test_components_can_be_added_to_new_entity_after_lifecycle_changes(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(99))

    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    assert rows[0][0] == new
    assert rows[0][1][0].value == 99


def test_tags_can_be_added_to_new_entity_after_lifecycle_changes(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(5))
    world.add_tag(new, Player)

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert len(rows) == 1
    assert rows[0][0] == new
    assert rows[0][1][0].value == 5


def test_destroy_twice_raises_or_noops_cleanly(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.destroy_entity(eid)
    except Exception:
        return

    assert world.is_alive(eid) is False
    assert world.entity_count() == 0


def test_destroy_invalid_entity_raises_or_noops_cleanly(world) -> None:
    try:
        world.destroy_entity(999999)
    except Exception:
        return

    assert world.entity_count() == 0


def test_component_cleanup_on_destroy_with_multiple_component_types(world) -> None:
    @dataclass
    class Position:
        x: float
        y: float

    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_component(eid, Position(2.0, 3.0))

    assert len(list(world.query((Counter,)))) == 1
    assert len(list(world.query((Position,)))) == 1

    world.destroy_entity(eid)

    assert list(world.query((Counter,))) == []
    assert list(world.query((Position,))) == []


def test_tag_cleanup_on_destroy_with_multiple_tags(world) -> None:
    class Enemy:
        pass

    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_tag(eid, Player)
    world.add_tag(eid, Enemy)

    assert len(list(world.query((Counter,), with_tags=(Player,)))) == 1
    assert len(list(world.query((Counter,), with_tags=(Enemy,)))) == 1

    world.destroy_entity(eid)

    assert list(world.query((Counter,), with_tags=(Player,))) == []
    assert list(world.query((Counter,), with_tags=(Enemy,))) == []


def test_destroy_entity_with_no_components_or_tags_is_safe(world) -> None:
    eid = world.create_entity()

    world.destroy_entity(eid)

    assert world.is_alive(eid) is False
    assert world.entity_count() == 0


def test_live_entities_remain_queryable_after_other_entities_are_destroyed(world) -> None:
    entities = [world.create_entity() for _ in range(5)]

    for i, eid in enumerate(entities):
        world.add_component(eid, Counter(i + 1))

    world.destroy_entity(entities[1])
    world.destroy_entity(entities[3])

    rows = list(world.query((Counter,)))
    result = {eid: counter.value for eid, (counter,) in rows}

    assert result == {
        entities[0]: 1,
        entities[2]: 3,
        entities[4]: 5,
    }


def test_get_component_returns_none_after_destroy(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(7))

    assert world.get_component(eid, Counter) == Counter(7)

    world.destroy_entity(eid)

    assert world.get_component(eid, Counter) is None


def test_recreated_entity_does_not_inherit_old_components(world) -> None:
    e1 = world.create_entity()
    world.add_component(e1, Counter(10))
    world.destroy_entity(e1)

    e2 = world.create_entity()

    if e2 == e1:
        assert world.get_component(e2, Counter) is None
    else:
        assert world.get_component(e2, Counter) is None

    assert world.is_alive(e2) is True


def test_recreated_entity_does_not_inherit_old_tags(world) -> None:
    e1 = world.create_entity()
    world.add_component(e1, Counter(1))
    world.add_tag(e1, Player)
    world.destroy_entity(e1)

    e2 = world.create_entity()
    world.add_component(e2, Counter(2))

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert rows == []


def test_entity_count_matches_number_of_live_entities_across_operations(world) -> None:
    entities = [world.create_entity() for _ in range(6)]
    assert world.entity_count() == 6

    world.destroy_entity(entities[0])
    world.destroy_entity(entities[2])
    assert world.entity_count() == 4

    world.create_entity()
    world.create_entity()
    assert world.entity_count() == 6


def test_is_alive_false_for_unknown_entity(world) -> None:
    assert world.is_alive(999999) is False


def test_create_destroy_create_sequence_keeps_state_consistent(world) -> None:
    e1 = world.create_entity()
    world.add_component(e1, Counter(1))
    world.destroy_entity(e1)

    e2 = world.create_entity()
    world.add_component(e2, Counter(2))

    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    assert rows[0][0] == e2
    assert rows[0][1][0].value == 2


def test_destroy_all_entities_leaves_world_empty(world) -> None:
    entities = [world.create_entity() for _ in range(5)]

    for eid in entities:
        world.destroy_entity(eid)

    assert world.entity_count() == 0
    assert list(world.query((Counter,))) == []


def test_stale_entity_handle_rejected_if_ids_are_reused(world) -> None:
    e1 = world.create_entity()
    world.destroy_entity(e1)
    e2 = world.create_entity()

    if e1 == e2:
        with pytest.raises(Exception):
            world.add_component(e1, Counter(5))
    else:
        assert world.is_alive(e1) is False
        assert world.is_alive(e2) is True