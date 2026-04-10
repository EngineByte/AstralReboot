from __future__ import annotations

from dataclasses import dataclass

import pytest

pytestmark = [pytest.mark.ecs, pytest.mark.integration]


@dataclass
class Counter:
    value: int


class Player:
    pass


def test_destroyed_entity_is_not_alive(world) -> None:
    eid = world.create_entity()

    world.destroy_entity(eid)

    assert world.is_alive(eid) is False


def test_destroyed_entity_no_longer_appears_in_component_queries(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    world.destroy_entity(eid)

    assert list(world.query((Counter,))) == []


def test_destroyed_entity_no_longer_appears_in_tag_queries(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))
    world.add_tag(eid, Player)

    world.destroy_entity(eid)

    assert list(world.query((Counter,), with_tags=(Player,))) == []


def test_stale_handle_cannot_add_component_after_destroy(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    with pytest.raises(Exception):
        world.add_component(eid, Counter(99))


def test_stale_handle_cannot_add_tag_after_destroy(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    with pytest.raises(Exception):
        world.add_tag(eid, Player)


def test_stale_handle_get_component_returns_none(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(5))

    world.destroy_entity(eid)

    assert world.get_component(eid, Counter) is None


def test_destroy_then_recreate_does_not_leak_old_component(world) -> None:
    old = world.create_entity()
    world.add_component(old, Counter(10))

    world.destroy_entity(old)
    new = world.create_entity()

    assert world.is_alive(old) is False
    assert world.is_alive(new) is True
    assert world.get_component(new, Counter) is None
    assert list(world.query((Counter,))) == []


def test_destroy_then_recreate_does_not_leak_old_tag(world) -> None:
    old = world.create_entity()
    world.add_component(old, Counter(1))
    world.add_tag(old, Player)

    world.destroy_entity(old)
    new = world.create_entity()
    world.add_component(new, Counter(2))

    assert world.is_alive(old) is False
    assert world.is_alive(new) is True
    assert list(world.query((Counter,), with_tags=(Player,))) == []


def test_reused_entity_slot_can_receive_new_component_without_old_handle_affecting_it(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(7))

    assert world.get_component(new, Counter) == Counter(7)

    with pytest.raises(Exception):
        world.add_component(old, Counter(99))

    assert world.get_component(new, Counter) == Counter(7)


def test_reused_entity_slot_can_receive_new_tag_without_old_handle_affecting_it(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(7))
    world.add_tag(new, Player)

    with pytest.raises(Exception):
        world.add_tag(old, Player)

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert len(rows) == 1
    assert rows[0][0] == new
    assert rows[0][1][0].value == 7


def test_stale_handle_cannot_remove_component_from_new_entity(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(11))

    try:
        world.remove_component(old, Counter)
    except Exception:
        pass

    assert world.get_component(new, Counter) == Counter(11)


def test_stale_handle_cannot_remove_tag_from_new_entity(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(11))
    world.add_tag(new, Player)

    try:
        world.remove_tag(old, Player)
    except Exception:
        pass

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert len(rows) == 1
    assert rows[0][0] == new


def test_multiple_destroy_recreate_cycles_do_not_leak_state(world) -> None:
    for i in range(5):
        eid = world.create_entity()
        world.add_component(eid, Counter(i))
        world.add_tag(eid, Player)
        world.destroy_entity(eid)

    final = world.create_entity()
    world.add_component(final, Counter(100))

    assert world.get_component(final, Counter) == Counter(100)
    assert list(world.query((Counter,), with_tags=(Player,))) == []


def test_old_and_new_handles_are_distinct_after_reuse(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()

    assert old != new


def test_old_handle_stays_dead_after_new_entity_created(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    _new = world.create_entity()

    assert world.is_alive(old) is False


def test_new_handle_is_alive_after_reuse(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()

    assert world.is_alive(new) is True


def test_stale_handle_cannot_be_destroyed_into_affecting_new_entity(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(1))

    try:
        world.destroy_entity(old)
    except Exception:
        pass

    assert world.is_alive(new) is True
    assert world.get_component(new, Counter) == Counter(1)


def test_iter_alive_entities_only_yields_current_live_handles_after_reuse(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()

    alive = tuple(world.iter_alive_entities())

    assert old not in alive
    assert new in alive
    assert len(alive) == 1


def test_deferred_work_with_stale_handle_does_not_affect_new_entity(world) -> None:
    old = world.create_entity()
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(3))

    world.defer_add_component(old, Counter(99))
    world.defer_add_tag(old, Player)
    world.defer_remove_component(old, Counter)
    world.defer_remove_tag(old, Player)
    world.defer_destroy_entity(old)

    world.apply_commands()

    assert world.is_alive(new) is True
    assert world.get_component(new, Counter) == Counter(3)
    assert list(world.query((Counter,), with_tags=(Player,))) == []


def test_query_only_returns_current_generation_entities(world) -> None:
    old = world.create_entity()
    world.add_component(old, Counter(1))
    world.destroy_entity(old)

    new = world.create_entity()
    world.add_component(new, Counter(2))

    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    assert rows[0][0] == new
    assert rows[0][1][0].value == 2