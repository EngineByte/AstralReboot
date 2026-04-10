from __future__ import annotations

from .conftest import Active, Counter, Position


def test_deferred_create_entity_becomes_alive_after_apply(world) -> None:
    before = world.entity_count()

    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Counter(10))

    world.apply_commands()

    rows = list(world.query((Counter,)))
    assert len(rows) == 1

    eid, (counter,) = rows[0]

    assert world.is_alive(eid)
    assert counter.value == 10
    assert world.entity_count() == before + 1


def test_deferred_add_component_applies_after_commit(world) -> None:
    entity = world.create_entity()

    world.defer_add_component(entity, Counter(value=10))

    assert world.get_component(entity, Counter) is None

    world.apply_commands()

    counter = world.get_component(entity, Counter)
    assert counter is not None
    assert counter.value == 10


def test_deferred_remove_component_applies_after_commit(world) -> None:
    entity = world.create_entity()
    world.add_component(entity, Counter(value=10))

    world.defer_remove_component(entity, Counter)

    assert world.get_component(entity, Counter) is not None

    world.apply_commands()

    assert world.get_component(entity, Counter) is None


def test_deferred_add_tag_applies_after_commit(world) -> None:
    entity = world.create_entity()

    world.defer_add_tag(entity, Active)

    assert not world.has_tag(entity, Active)

    world.apply_commands()

    assert world.has_tag(entity, Active)


def test_deferred_remove_tag_applies_after_commit(world) -> None:
    entity = world.create_entity()
    world.add_tag(entity, Active)

    world.defer_remove_tag(entity, Active)

    assert world.has_tag(entity, Active)

    world.apply_commands()

    assert not world.has_tag(entity, Active)


def test_deferred_destroy_entity_applies_after_commit(world) -> None:
    entity = world.create_entity()

    world.defer_destroy_entity(entity)

    assert world.is_alive(entity)

    world.apply_commands()

    assert not world.is_alive(entity)


def test_deferred_mutations_can_target_placeholder_entity(world) -> None:
    placeholder = world.defer_create_entity()
    world.defer_add_component(placeholder, Position(x=1.0, y=2.0))
    world.defer_add_tag(placeholder, Active)

    world.apply_commands()

    rows = list(world.query((Position,), with_tags=(Active,)))
    assert len(rows) == 1

    entity, (position,) = rows[0]
    assert world.is_alive(entity)
    assert position.x == 1.0
    assert position.y == 2.0