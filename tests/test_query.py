from __future__ import annotations

from .conftest import Active, Counter, Frozen, Position, Velocity


def test_query_single_component(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(value=1))
    world.add_component(e2, Counter(value=2))

    rows = list(world.query((Counter,)))

    found = {entity: counter.value for entity, (counter,) in rows}
    assert found == {e1: 1, e2: 2}


def test_query_multiple_components_returns_only_matching_entities(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()

    world.add_component(e1, Position(x=1, y=2))
    world.add_component(e1, Velocity(x=3, y=4))

    world.add_component(e2, Position(x=10, y=20))

    world.add_component(e3, Velocity(x=30, y=40))

    rows = list(world.query((Position, Velocity)))

    assert len(rows) == 1
    entity, (position, velocity) = rows[0]

    assert entity == e1
    assert position.x == 1
    assert position.y == 2
    assert velocity.x == 3
    assert velocity.y == 4


def test_query_with_tags_filters_correctly(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(value=1))
    world.add_component(e2, Counter(value=2))

    world.add_tag(e1, Active)

    rows = list(world.query((Counter,), with_tags=(Active,)))

    found = {entity: counter.value for entity, (counter,) in rows}
    assert found == {e1: 1}


def test_query_without_tags_filters_correctly(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()

    world.add_component(e1, Counter(value=1))
    world.add_component(e2, Counter(value=2))

    world.add_tag(e2, Frozen)

    rows = list(world.query((Counter,), without_tags=(Frozen,)))

    found = {entity: counter.value for entity, (counter,) in rows}
    assert found == {e1: 1}


def test_query_with_and_without_tags_can_be_combined(world) -> None:
    e1 = world.create_entity()
    e2 = world.create_entity()
    e3 = world.create_entity()

    for eid, value in ((e1, 1), (e2, 2), (e3, 3)):
        world.add_component(eid, Counter(value=value))

    world.add_tag(e1, Active)
    world.add_tag(e2, Active)
    world.add_tag(e2, Frozen)

    rows = list(
        world.query(
            (Counter,),
            with_tags=(Active,),
            without_tags=(Frozen,),
        )
    )

    found = {entity: counter.value for entity, (counter,) in rows}
    assert found == {e1: 1}


def test_query_empty_when_no_entities_match(world) -> None:
    entity = world.create_entity()
    world.add_component(entity, Position(x=1, y=2))

    rows = list(world.query((Velocity,)))

    assert rows == []


def test_query_reflects_component_removal(world) -> None:
    entity = world.create_entity()
    world.add_component(entity, Counter(value=5))

    assert len(list(world.query((Counter,)))) == 1

    world.remove_component(entity, Counter)

    assert list(world.query((Counter,))) == []