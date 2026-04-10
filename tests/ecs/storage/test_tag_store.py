from __future__ import annotations

from astralengine.ecs.storage.tag_store import TagStore

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.storage,
    pytest.mark.unit
]


def test_add_and_has_tag_membership() -> None:
    store = TagStore()

    store.add(1)

    assert store.has(1) is True
    assert len(store) == 1


def test_has_returns_false_for_missing_entity() -> None:
    store = TagStore()

    assert store.has(999) is False


def test_adding_same_entity_twice_does_not_duplicate_membership() -> None:
    store = TagStore()

    store.add(1)
    store.add(1)

    assert store.has(1) is True
    assert len(store) == 1
    assert store.entities() == (1,)


def test_remove_existing_entity_deletes_membership() -> None:
    store = TagStore()
    store.add(1)

    store.remove(1)

    assert store.has(1) is False
    assert len(store) == 0
    assert store.entities() == ()


def test_remove_last_entity_leaves_store_consistent() -> None:
    store = TagStore()

    store.add(1)
    store.add(2)

    store.remove(2)

    assert store.has(2) is False
    assert store.has(1) is True
    assert len(store) == 1
    assert store.entities() == (1,)


def test_remove_first_entity_leaves_store_consistent() -> None:
    store = TagStore()

    store.add(1)
    store.add(2)

    store.remove(1)

    assert store.has(1) is False
    assert store.has(2) is True
    assert len(store) == 1
    assert store.entities() == (2,)


def test_swap_remove_updates_remaining_entity_lookup() -> None:
    store = TagStore()

    store.add(10)
    store.add(20)
    store.add(30)

    store.remove(20)

    assert store.has(10) is True
    assert store.has(30) is True
    assert store.has(20) is False
    assert set(store.entities()) == {10, 30}
    assert len(store) == 2


def test_entities_returns_all_live_entities() -> None:
    store = TagStore()

    store.add(4)
    store.add(5)
    store.add(6)

    assert set(store.entities()) == {4, 5, 6}


def test_clear_resets_store() -> None:
    store = TagStore()

    store.add(1)
    store.add(2)

    store.clear()

    assert len(store) == 0
    assert store.has(1) is False
    assert store.has(2) is False
    assert store.entities() == ()


def test_multiple_mutations_keep_entities_in_sync() -> None:
    store = TagStore()

    store.add(1)
    store.add(2)
    store.add(3)
    store.remove(2)
    store.add(4)
    store.remove(1)

    assert set(store.entities()) == {3, 4}
    assert store.has(3) is True
    assert store.has(4) is True
    assert store.has(1) is False
    assert store.has(2) is False
    assert len(store) == 2


def test_summary_reports_size_if_supported() -> None:
    store = TagStore()

    if not hasattr(store, "summary"):
        return

    assert store.summary() == "TagStore(size=0)"

    store.add(1)
    assert store.summary() == "TagStore(size=1)"