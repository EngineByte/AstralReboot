from __future__ import annotations

from dataclasses import dataclass

from astralengine.ecs.storage.dense_store import DenseStore

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.storage,
    pytest.mark.unit
]


@dataclass
class Counter:
    value: int


@dataclass
class Position:
    x: float
    y: float


def test_add_and_get_component() -> None:
    store = DenseStore()
    component = Counter(10)

    store.add(1, component)

    assert store.has(1) is True
    assert store.get(1) is component
    assert len(store) == 1


def test_has_returns_false_for_missing_entity() -> None:
    store = DenseStore()

    assert store.has(999) is False
    assert 999 not in store


def test_get_missing_entity_returns_none() -> None:
    store = DenseStore()

    assert store.get(123) is None


def test_remove_existing_entity_deletes_component() -> None:
    store = DenseStore()
    store.add(1, Counter(5))

    store.remove(1)

    assert store.has(1) is False
    assert len(store) == 0
    assert store.get(1) is None


def test_remove_last_entity_deletes_component() -> None:
    store = DenseStore()
    store.add(1, Counter(5))
    store.add(2, Counter(7))

    store.remove(2)

    assert store.has(2) is False
    assert store.get(2) is None
    assert store.has(1) is True
    assert store.get(1) == Counter(5)
    assert len(store) == 1


def test_adding_same_entity_twice_replaces_component() -> None:
    store = DenseStore()
    first = Counter(1)
    second = Counter(2)

    store.add(1, first)
    store.add(1, second)

    assert len(store) == 1
    assert store.has(1) is True
    assert store.get(1) is second


def test_len_tracks_number_of_entries() -> None:
    store = DenseStore()

    assert len(store) == 0

    store.add(1, Counter(1))
    assert len(store) == 1

    store.add(2, Counter(2))
    assert len(store) == 2

    store.remove(1)
    assert len(store) == 1

    store.remove(2)
    assert len(store) == 0


def test_swap_remove_keeps_store_compact() -> None:
    store = DenseStore()

    store.add(10, Counter(10))
    store.add(20, Counter(20))
    store.add(30, Counter(30))

    store.remove(20)

    assert len(store) == 2
    assert store.has(20) is False

    remaining_entities = set(store.entities())
    assert remaining_entities == {10, 30}

    remaining_values = {store.get(eid).value for eid in remaining_entities}
    assert remaining_values == {10, 30}


def test_swap_remove_updates_moved_entity_lookup() -> None:
    store = DenseStore()

    store.add(1, Counter(100))
    store.add(2, Counter(200))
    store.add(3, Counter(300))

    store.remove(2)

    assert store.has(3) is True
    component = store.get(3)
    assert component is not None
    assert component.value == 300


def test_entities_returns_all_live_entity_ids() -> None:
    store = DenseStore()

    store.add(4, Counter(4))
    store.add(5, Counter(5))
    store.add(6, Counter(6))

    entities = set(store.entities())
    assert entities == {4, 5, 6}


def test_items_returns_entity_component_pairs() -> None:
    store = DenseStore()

    c1 = Counter(11)
    c2 = Counter(22)

    store.add(1, c1)
    store.add(2, c2)

    rows = store.items()

    assert len(rows) == 2
    result = {eid: component.value for eid, component in rows}
    assert result == {1: 11, 2: 22}


def test_values_returns_all_components() -> None:
    store = DenseStore()

    c1 = Counter(11)
    c2 = Counter(22)

    store.add(1, c1)
    store.add(2, c2)

    values = store.values()

    assert len(values) == 2
    assert set(v.value for v in values) == {11, 22}


def test_store_accepts_multiple_component_instances() -> None:
    store = DenseStore()

    p1 = Position(1.0, 2.0)
    p2 = Position(3.0, 4.0)

    store.add(100, p1)
    store.add(200, p2)

    assert store.get(100) is p1
    assert store.get(200) is p2
    assert len(store) == 2


def test_removing_first_entity_leaves_store_consistent() -> None:
    store = DenseStore()

    store.add(1, Counter(1))
    store.add(2, Counter(2))

    store.remove(1)

    assert store.has(1) is False
    assert store.get(1) is None
    assert store.has(2) is True

    component = store.get(2)
    assert component is not None
    assert component.value == 2
    assert len(store) == 1


def test_clear_resets_store() -> None:
    store = DenseStore()

    store.add(1, Counter(1))
    store.add(2, Counter(2))

    store.clear()

    assert len(store) == 0
    assert store.has(1) is False
    assert store.has(2) is False
    assert store.get(1) is None
    assert store.get(2) is None
    assert store.entities() == ()
    assert store.values() == ()
    assert store.items() == ()


def test_store_allows_any_component_object() -> None:
    store = DenseStore()

    counter = Counter(9)
    position = Position(1.0, 2.0)

    store.add(1, counter)
    store.add(2, position)

    assert store.get(1) is counter
    assert store.get(2) is position


def test_entities_and_components_remain_in_sync_after_multiple_mutations() -> None:
    store = DenseStore()

    store.add(1, Counter(10))
    store.add(2, Counter(20))
    store.add(3, Counter(30))
    store.remove(2)
    store.add(4, Counter(40))
    store.remove(1)

    remaining_entities = set(store.entities())
    assert remaining_entities == {3, 4}

    result = {}
    for eid in remaining_entities:
        component = store.get(eid)
        assert component is not None
        result[eid] = component.value

    assert result == {
        3: 30,
        4: 40,
    }


def test_summary_reports_size() -> None:
    store = DenseStore()
    assert store.summary() == "DenseStore(size=0)"

    store.add(1, Counter(1))
    assert store.summary() == "DenseStore(size=1)"