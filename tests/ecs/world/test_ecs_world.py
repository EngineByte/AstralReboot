from __future__ import annotations

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.world,
    pytest.mark.unit
]

from conftest import Active, Counter, Position


def test_create_entity_returns_alive_entity(world) -> None:
    entity = world.create_entity()

    assert isinstance(entity, int)
    assert world.is_alive(entity)


def test_create_multiple_entities_returns_distinct_ids(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    assert e1 != e2
    assert world.is_alive(e1)
    assert world.is_alive(e2)


def test_destroy_entity_marks_entity_not_alive(world) -> None:
    entity = world.create_entity()

    world.destroy_entity(entity)

    assert not world.is_alive(entity)


def test_add_and_get_component(world) -> None:
    entity = world.create_entity()
    position = Position(x=10.0, y=20.0)

    world.add_component(entity, position)

    retrieved = world.get_component(entity, Position)

    assert retrieved is position
    assert retrieved.x == 10.0
    assert retrieved.y == 20.0


def test_get_missing_component_returns_none(world) -> None:
    entity = world.create_entity()

    retrieved = world.get_component(entity, Position)

    assert retrieved is None


def test_remove_component_makes_it_unavailable(world) -> None:
    entity = world.create_entity()
    world.add_component(entity, Position(x=1.0, y=2.0))

    world.remove_component(entity, Position)

    assert world.get_component(entity, Position) is None


def test_add_component_overwrites_existing_component_of_same_type(world) -> None:
    entity = world.create_entity()

    world.add_component(entity, Counter(value=1))
    world.add_component(entity, Counter(value=99))

    counter = world.get_component(entity, Counter)

    assert counter is not None
    assert counter.value == 99


def test_add_and_remove_tag(world) -> None:
    entity = world.create_entity()

    world.add_tag(entity, Active)
    assert world.has_tag(entity, Active)

    world.remove_tag(entity, Active)
    assert not world.has_tag(entity, Active)


def test_destroy_entity_removes_components_and_tags(world) -> None:
    entity = world.create_entity()
    world.add_component(entity, Position(x=3.0, y=4.0))
    world.add_tag(entity, Active)

    world.destroy_entity(entity)

    assert not world.is_alive(entity)
    assert world.get_component(entity, Position) is None
    assert not world.has_tag(entity, Active)


def test_destroy_unknown_or_dead_entity_is_safe(world) -> None:
    entity = world.create_entity()
    world.destroy_entity(entity)

    # Should not raise if your ECS is designed defensively
    world.destroy_entity(entity)

    assert not world.is_alive(entity)


@pytest.mark.parametrize(
    ("count",),
    [(1,), (10,), (100,)],
)
def test_can_create_many_entities(world, count: int) -> None:
    entities = [world.create_entity() for _ in range(count)]

    assert len(set(entities)) == count
    assert all(world.is_alive(eid) for eid in entities)