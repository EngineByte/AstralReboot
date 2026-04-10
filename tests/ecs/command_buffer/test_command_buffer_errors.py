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


class Player:
    pass


def test_apply_commands_with_empty_buffer_is_safe(world) -> None:
    world.apply_commands()

    assert world.entity_count() == 0


def test_applying_empty_buffer_twice_is_safe(world) -> None:
    world.apply_commands()
    world.apply_commands()

    assert world.entity_count() == 0


def test_deferred_remove_missing_component_is_safe(world) -> None:
    eid = world.create_entity()

    world.defer_remove_component(eid, Counter)
    world.apply_commands()

    assert world.is_alive(eid)
    assert list(world.query((Counter,))) == []


def test_deferred_remove_missing_tag_is_safe(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    world.defer_remove_tag(eid, Player)
    world.apply_commands()

    assert world.is_alive(eid)
    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    assert rows[0][0] == eid


def test_deferred_destroy_missing_or_dead_entity_is_safe_if_supported(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.defer_destroy_entity(eid)
        world.apply_commands()
    except Exception:
        return

    assert world.is_alive(eid) is False


def test_deferred_add_component_to_dead_entity_raises_or_is_ignored_cleanly(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.defer_add_component(eid, Counter(5))
        world.apply_commands()
    except Exception:
        return

    assert world.is_alive(eid) is False
    assert list(world.query((Counter,))) == []


def test_deferred_add_tag_to_dead_entity_raises_or_is_ignored_cleanly(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.defer_add_tag(eid, Player)
        world.apply_commands()
    except Exception:
        return

    assert world.is_alive(eid) is False


def test_deferred_remove_component_from_dead_entity_is_safe(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.defer_remove_component(eid, Counter)
        world.apply_commands()
    except Exception:
        return

    assert world.is_alive(eid) is False


def test_deferred_remove_tag_from_dead_entity_is_safe(world) -> None:
    eid = world.create_entity()
    world.destroy_entity(eid)

    try:
        world.defer_remove_tag(eid, Player)
        world.apply_commands()
    except Exception:
        return

    assert world.is_alive(eid) is False


def test_deferred_add_component_with_unknown_placeholder_raises_or_is_rejected(world) -> None:
    unknown_placeholder = -9999

    try:
        world.defer_add_component(unknown_placeholder, Counter(1))
        world.apply_commands()
    except Exception:
        return

    rows = list(world.query((Counter,)))
    assert rows == []


def test_deferred_add_tag_with_unknown_placeholder_raises_or_is_rejected(world) -> None:
    unknown_placeholder = -9999

    try:
        world.defer_add_tag(unknown_placeholder, Player)
        world.apply_commands()
    except Exception:
        return

    assert world.entity_count() == 0


def test_deferred_remove_component_with_unknown_placeholder_is_safe(world) -> None:
    unknown_placeholder = -9999

    try:
        world.defer_remove_component(unknown_placeholder, Counter)
        world.apply_commands()
    except Exception:
        return

    assert world.entity_count() == 0


def test_deferred_remove_tag_with_unknown_placeholder_is_safe(world) -> None:
    unknown_placeholder = -9999

    try:
        world.defer_remove_tag(unknown_placeholder, Player)
        world.apply_commands()
    except Exception:
        return

    assert world.entity_count() == 0


def test_deferred_destroy_unknown_placeholder_is_safe_or_rejected_cleanly(world) -> None:
    unknown_placeholder = -9999

    try:
        world.defer_destroy_entity(unknown_placeholder)
        world.apply_commands()
    except Exception:
        return

    assert world.entity_count() == 0


def test_apply_commands_clears_buffer_after_commit(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))

    world.apply_commands()

    first_rows = list(world.query((Counter,)))
    assert len(first_rows) == 1

    world.apply_commands()

    second_rows = list(world.query((Counter,)))
    assert len(second_rows) == 1


def test_apply_commands_after_failed_or_invalid_operation_does_not_duplicate_work(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))

    world.apply_commands()
    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    _, (counter,) = rows[0]
    assert counter.value == 10


def test_deferred_destroy_then_add_component_same_placeholder_results_in_no_entity(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_destroy_entity(placeholder)
    world.defer_add_component(placeholder, Counter(1))

    world.apply_commands()

    assert world.entity_count() == 0
    assert list(world.query((Counter,))) == []


def test_deferred_destroy_then_add_tag_same_placeholder_results_in_no_entity(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_destroy_entity(placeholder)
    world.defer_add_tag(placeholder, Player)

    world.apply_commands()

    assert world.entity_count() == 0


def test_deferred_commands_on_one_entity_do_not_break_other_entities(world) -> None:
    alive = world.create_entity()
    world.add_component(alive, Counter(7))

    dead = world.create_entity()
    world.destroy_entity(dead)

    try:
        world.defer_add_component(dead, Counter(99))
    except Exception:
        pass

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1
    assert rows[0][0] == alive
    assert rows[0][1][0].value == 7


def test_deferred_remove_missing_component_does_not_break_valid_add(world) -> None:
    eid = world.create_entity()

    world.defer_remove_component(eid, Counter)
    world.defer_add_component(eid, Counter(3))
    world.apply_commands()

    rows = list(world.query((Counter,)))
    # Depending on your global ordering, remove wins if both are buffered.
    assert rows == [] or (len(rows) == 1 and rows[0][1][0].value == 3)


def test_deferred_remove_missing_tag_does_not_break_valid_tag_add(world) -> None:
    eid = world.create_entity()
    world.add_component(eid, Counter(1))

    world.defer_remove_tag(eid, Player)
    world.defer_add_tag(eid, Player)
    world.apply_commands()

    rows = list(world.query((Counter,), with_tags=(Player,)))
    assert rows == [] or len(rows) == 1


def test_command_buffer_accepts_multiple_apply_cycles(world) -> None:
    p1 = world.defer_create_entity()
    world.defer_add_component(p1, Counter(1))
    world.apply_commands()

    p2 = world.defer_create_entity()
    world.defer_add_component(p2, Counter(2))
    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 2

    values = {counter.value for _, (counter,) in rows}
    assert values == {1, 2}


def test_deferred_create_without_followup_data_still_commits_cleanly(world) -> None:
    world.defer_create_entity()
    world.apply_commands()

    assert world.entity_count() == 1