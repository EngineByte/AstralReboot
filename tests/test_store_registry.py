from __future__ import annotations

from dataclasses import dataclass

import pytest

from astralengine.ecs.storage.dense_store import DenseStore
from astralengine.ecs.storage.store_registry import StoreRegistry
from astralengine.ecs.storage.tag_store import TagStore


@dataclass
class Counter:
    value: int


@dataclass
class Position:
    x: float
    y: float


class Player:
    pass


class Enemy:
    pass


def test_get_component_store_returns_none_when_not_registered() -> None:
    registry = StoreRegistry()

    store = registry.get_component_store(Counter)

    assert store is None


def test_get_or_create_component_store_creates_and_returns_dense_store() -> None:
    registry = StoreRegistry()

    store = registry.get_or_create_component_store(Counter)

    assert isinstance(store, DenseStore)
    assert registry.get_component_store(Counter) is store


def test_get_component_store_returns_same_instance_for_same_type() -> None:
    registry = StoreRegistry()

    store1 = registry.get_or_create_component_store(Counter)
    store2 = registry.get_component_store(Counter)

    assert store1 is store2


def test_get_or_create_component_store_returns_same_instance_for_same_type() -> None:
    registry = StoreRegistry()

    store1 = registry.get_or_create_component_store(Counter)
    store2 = registry.get_or_create_component_store(Counter)

    assert store1 is store2


def test_get_or_create_component_store_returns_different_instances_for_different_types() -> None:
    registry = StoreRegistry()

    counter_store = registry.get_or_create_component_store(Counter)
    position_store = registry.get_or_create_component_store(Position)

    assert counter_store is not position_store


def test_register_component_store_registers_explicit_store() -> None:
    registry = StoreRegistry()
    store = DenseStore()

    registry.register_component_store(Counter, store)

    assert registry.get_component_store(Counter) is store


def test_register_component_store_duplicate_raises_value_error() -> None:
    registry = StoreRegistry()

    registry.register_component_store(Counter, DenseStore())

    with pytest.raises(ValueError, match="already registered"):
        registry.register_component_store(Counter, DenseStore())


def test_has_component_store_reflects_registration_state() -> None:
    registry = StoreRegistry()

    assert registry.has_component_store(Counter) is False

    registry.get_or_create_component_store(Counter)

    assert registry.has_component_store(Counter) is True


def test_remove_component_store_removes_registered_store() -> None:
    registry = StoreRegistry()
    registry.get_or_create_component_store(Counter)

    registry.remove_component_store(Counter)

    assert registry.has_component_store(Counter) is False
    assert registry.get_component_store(Counter) is None


def test_remove_component_store_missing_raises_keyerror() -> None:
    registry = StoreRegistry()

    with pytest.raises(KeyError, match="No component store registered"):
        registry.remove_component_store(Counter)


def test_component_store_count_tracks_registered_component_stores() -> None:
    registry = StoreRegistry()

    assert registry.component_store_count() == 0

    registry.get_or_create_component_store(Counter)
    assert registry.component_store_count() == 1

    registry.get_or_create_component_store(Position)
    assert registry.component_store_count() == 2


def test_component_stores_returns_registered_component_stores() -> None:
    registry = StoreRegistry()

    counter_store = registry.get_or_create_component_store(Counter)
    position_store = registry.get_or_create_component_store(Position)

    stores = registry.component_stores()

    assert len(stores) == 2
    assert counter_store in stores
    assert position_store in stores


def test_component_store_items_returns_type_store_pairs() -> None:
    registry = StoreRegistry()

    counter_store = registry.get_or_create_component_store(Counter)
    position_store = registry.get_or_create_component_store(Position)

    items = dict(registry.component_store_items())

    assert items[Counter] is counter_store
    assert items[Position] is position_store


def test_get_tag_store_returns_none_when_not_registered() -> None:
    registry = StoreRegistry()

    store = registry.get_tag_store(Player)

    assert store is None


def test_get_or_create_tag_store_creates_and_returns_tag_store() -> None:
    registry = StoreRegistry()

    store = registry.get_or_create_tag_store(Player)

    assert isinstance(store, TagStore)
    assert registry.get_tag_store(Player) is store


def test_get_tag_store_returns_same_instance_for_same_type() -> None:
    registry = StoreRegistry()

    store1 = registry.get_or_create_tag_store(Player)
    store2 = registry.get_tag_store(Player)

    assert store1 is store2


def test_get_or_create_tag_store_returns_same_instance_for_same_tag_type() -> None:
    registry = StoreRegistry()

    store1 = registry.get_or_create_tag_store(Player)
    store2 = registry.get_or_create_tag_store(Player)

    assert store1 is store2


def test_get_or_create_tag_store_returns_different_instances_for_different_tag_types() -> None:
    registry = StoreRegistry()

    player_store = registry.get_or_create_tag_store(Player)
    enemy_store = registry.get_or_create_tag_store(Enemy)

    assert player_store is not enemy_store


def test_register_tag_store_registers_explicit_store() -> None:
    registry = StoreRegistry()
    store = TagStore()

    registry.register_tag_store(Player, store)

    assert registry.get_tag_store(Player) is store


def test_register_tag_store_duplicate_raises_value_error() -> None:
    registry = StoreRegistry()

    registry.register_tag_store(Player, TagStore())

    with pytest.raises(ValueError, match="already registered"):
        registry.register_tag_store(Player, TagStore())


def test_has_tag_store_reflects_registration_state() -> None:
    registry = StoreRegistry()

    assert registry.has_tag_store(Player) is False

    registry.get_or_create_tag_store(Player)

    assert registry.has_tag_store(Player) is True


def test_remove_tag_store_removes_registered_store() -> None:
    registry = StoreRegistry()
    registry.get_or_create_tag_store(Player)

    registry.remove_tag_store(Player)

    assert registry.has_tag_store(Player) is False
    assert registry.get_tag_store(Player) is None


def test_remove_tag_store_missing_raises_keyerror() -> None:
    registry = StoreRegistry()

    with pytest.raises(KeyError, match="No tag store registered"):
        registry.remove_tag_store(Player)


def test_tag_store_count_tracks_registered_tag_stores() -> None:
    registry = StoreRegistry()

    assert registry.tag_store_count() == 0

    registry.get_or_create_tag_store(Player)
    assert registry.tag_store_count() == 1

    registry.get_or_create_tag_store(Enemy)
    assert registry.tag_store_count() == 2


def test_tag_stores_returns_registered_tag_stores() -> None:
    registry = StoreRegistry()

    player_store = registry.get_or_create_tag_store(Player)
    enemy_store = registry.get_or_create_tag_store(Enemy)

    stores = registry.tag_stores()

    assert len(stores) == 2
    assert player_store in stores
    assert enemy_store in stores


def test_tag_store_items_returns_type_store_pairs() -> None:
    registry = StoreRegistry()

    player_store = registry.get_or_create_tag_store(Player)
    enemy_store = registry.get_or_create_tag_store(Enemy)

    items = dict(registry.tag_store_items())

    assert items[Player] is player_store
    assert items[Enemy] is enemy_store


def test_add_component_requires_registered_store() -> None:
    registry = StoreRegistry()

    with pytest.raises(KeyError, match="No component store registered"):
        registry.add_component(1, Counter(10))


def test_add_component_adds_to_registered_component_store() -> None:
    registry = StoreRegistry()
    registry.get_or_create_component_store(Counter)

    registry.add_component(1, Counter(10))

    assert registry.has_component(1, Counter) is True
    store = registry.get_component_store(Counter)
    assert store is not None
    assert store.get(1) == Counter(10)


def test_remove_component_on_missing_store_is_noop() -> None:
    registry = StoreRegistry()

    registry.remove_component(1, Counter)

    assert registry.has_component(1, Counter) is False


def test_remove_component_removes_from_registered_store() -> None:
    registry = StoreRegistry()
    registry.get_or_create_component_store(Counter)

    registry.add_component(1, Counter(10))
    registry.remove_component(1, Counter)

    assert registry.has_component(1, Counter) is False


def test_has_component_false_when_store_not_registered() -> None:
    registry = StoreRegistry()

    assert registry.has_component(1, Counter) is False


def test_add_tag_requires_registered_store() -> None:
    registry = StoreRegistry()

    with pytest.raises(KeyError, match="No tag store registered"):
        registry.add_tag(1, Player)


def test_add_tag_adds_to_registered_tag_store() -> None:
    registry = StoreRegistry()
    registry.get_or_create_tag_store(Player)

    registry.add_tag(1, Player)

    assert registry.has_tag(1, Player) is True
    store = registry.get_tag_store(Player)
    assert store is not None
    assert store.has(1) is True


def test_remove_tag_on_missing_store_is_noop() -> None:
    registry = StoreRegistry()

    registry.remove_tag(1, Player)

    assert registry.has_tag(1, Player) is False


def test_remove_tag_removes_from_registered_store() -> None:
    registry = StoreRegistry()
    registry.get_or_create_tag_store(Player)

    registry.add_tag(1, Player)
    registry.remove_tag(1, Player)

    assert registry.has_tag(1, Player) is False


def test_has_tag_false_when_store_not_registered() -> None:
    registry = StoreRegistry()

    assert registry.has_tag(1, Player) is False


def test_clear_removes_all_registered_stores() -> None:
    registry = StoreRegistry()

    registry.get_or_create_component_store(Counter)
    registry.get_or_create_component_store(Position)
    registry.get_or_create_tag_store(Player)

    registry.clear()

    assert registry.component_store_count() == 0
    assert registry.tag_store_count() == 0
    assert registry.is_empty() is True


def test_is_empty_reflects_registry_state() -> None:
    registry = StoreRegistry()

    assert registry.is_empty() is True

    registry.get_or_create_component_store(Counter)
    assert registry.is_empty() is False


def test_summary_reports_counts() -> None:
    registry = StoreRegistry()

    assert registry.summary() == "StoreRegistry(component_stores=0, tag_stores=0)"

    registry.get_or_create_component_store(Counter)
    registry.get_or_create_tag_store(Player)

    assert registry.summary() == "StoreRegistry(component_stores=1, tag_stores=1)"