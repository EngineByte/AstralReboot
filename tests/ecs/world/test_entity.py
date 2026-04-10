from __future__ import annotations

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.world,
    pytest.mark.unit
]

from astralengine.ecs.core.entity import (
    ENTITY_INDEX_BITS,
    GENERATION_BITS,
    MAX_ENTITY_INDEX,
    MAX_GENERATION,
    EntityHandle,
)


def test_entity_handle_can_be_constructed_from_index_and_generation() -> None:
    eid = EntityHandle(index=3, generation=1)

    assert isinstance(eid, EntityHandle)
    assert eid.index == 3
    assert eid.generation == 1


def test_entity_handle_id_alias_returns_index() -> None:
    eid = EntityHandle(index=7, generation=2)

    assert eid.id == 7


def test_entity_handle_gen_alias_returns_generation() -> None:
    eid = EntityHandle(index=7, generation=2)

    assert eid.gen == 2


def test_entity_handle_equality_for_same_index_and_generation() -> None:
    a = EntityHandle(index=5, generation=1)
    b = EntityHandle(index=5, generation=1)

    assert a == b


def test_entity_handle_inequality_for_different_index() -> None:
    a = EntityHandle(index=5, generation=1)
    b = EntityHandle(index=6, generation=1)

    assert a != b


def test_entity_handle_inequality_for_different_generation() -> None:
    a = EntityHandle(index=5, generation=1)
    b = EntityHandle(index=5, generation=2)

    assert a != b


def test_entity_handle_is_hashable() -> None:
    a = EntityHandle(index=5, generation=1)
    b = EntityHandle(index=5, generation=1)

    d = {a: "alive"}

    assert d[b] == "alive"


def test_entity_handle_can_be_used_in_set() -> None:
    a = EntityHandle(index=1, generation=0)
    b = EntityHandle(index=2, generation=0)
    c = EntityHandle(index=1, generation=0)

    values = {a, b, c}

    assert len(values) == 2


def test_entity_handle_repr_contains_index_generation_and_packed_value() -> None:
    eid = EntityHandle(index=42, generation=3)

    text = repr(eid)

    assert "42" in text
    assert "3" in text
    assert "packed=" in text


def test_entity_handle_to_int_matches_dunder_int() -> None:
    eid = EntityHandle(index=9, generation=4)

    assert eid.to_int() == int(eid)


def test_entity_handle_to_int_packs_correctly() -> None:
    eid = EntityHandle(index=5, generation=2)

    expected = (2 << ENTITY_INDEX_BITS) | 5

    assert eid.to_int() == expected


def test_entity_handle_pack_returns_expected_integer() -> None:
    packed = EntityHandle.pack(index=5, generation=2)

    expected = (2 << ENTITY_INDEX_BITS) | 5

    assert packed == expected


def test_entity_handle_unpack_returns_index_and_generation() -> None:
    packed = EntityHandle.pack(index=11, generation=7)

    index, generation = EntityHandle.unpack(packed)

    assert index == 11
    assert generation == 7


def test_entity_handle_get_index_returns_index_from_packed_id() -> None:
    packed = EntityHandle.pack(index=123, generation=9)

    assert EntityHandle.get_index(packed) == 123


def test_entity_handle_get_generation_returns_generation_from_packed_id() -> None:
    packed = EntityHandle.pack(index=123, generation=9)

    assert EntityHandle.get_generation(packed) == 9


def test_entity_handle_make_constructs_handle() -> None:
    eid = EntityHandle.make(index=10, generation=20)

    assert isinstance(eid, EntityHandle)
    assert eid.index == 10
    assert eid.generation == 20


def test_entity_handle_from_int_round_trips() -> None:
    original = EntityHandle(index=55, generation=12)

    packed = int(original)
    restored = EntityHandle.from_int(packed)

    assert restored == original


def test_entity_handle_iter_supports_tuple_unpacking() -> None:
    eid = EntityHandle(index=8, generation=6)

    index, generation = eid

    assert index == 8
    assert generation == 6


def test_entity_handle_zero_values_are_allowed() -> None:
    eid = EntityHandle(index=0, generation=0)

    assert eid.index == 0
    assert eid.generation == 0
    assert int(eid) == 0


def test_entity_handle_rejects_negative_index() -> None:
    with pytest.raises(ValueError, match="index must be non-negative"):
        EntityHandle(index=-1, generation=0)


def test_entity_handle_rejects_negative_generation() -> None:
    with pytest.raises(ValueError, match="generation must be non-negative"):
        EntityHandle(index=0, generation=-1)


def test_entity_handle_rejects_index_above_maximum() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        EntityHandle(index=MAX_ENTITY_INDEX + 1, generation=0)


def test_entity_handle_rejects_generation_above_maximum() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        EntityHandle(index=0, generation=MAX_GENERATION + 1)


def test_entity_handle_pack_rejects_negative_index() -> None:
    with pytest.raises(ValueError, match="index must be non-negative"):
        EntityHandle.pack(index=-1, generation=0)


def test_entity_handle_pack_rejects_negative_generation() -> None:
    with pytest.raises(ValueError, match="generation must be non-negative"):
        EntityHandle.pack(index=0, generation=-1)


def test_entity_handle_pack_rejects_index_above_maximum() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        EntityHandle.pack(index=MAX_ENTITY_INDEX + 1, generation=0)


def test_entity_handle_pack_rejects_generation_above_maximum() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        EntityHandle.pack(index=0, generation=MAX_GENERATION + 1)


def test_entity_handle_unpack_rejects_negative_packed_id() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        EntityHandle.unpack(-1)


def test_entity_handle_get_index_rejects_negative_packed_id() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        EntityHandle.get_index(-1)


def test_entity_handle_get_generation_rejects_negative_packed_id() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        EntityHandle.get_generation(-1)


def test_entity_handle_from_int_rejects_negative_packed_id() -> None:
    with pytest.raises(ValueError, match="must be non-negative"):
        EntityHandle.from_int(-1)


def test_entity_handle_max_values_pack_and_unpack_correctly() -> None:
    eid = EntityHandle(index=MAX_ENTITY_INDEX, generation=MAX_GENERATION)

    packed = int(eid)
    restored = EntityHandle.from_int(packed)

    assert restored.index == MAX_ENTITY_INDEX
    assert restored.generation == MAX_GENERATION


def test_entity_handle_bit_constants_are_32() -> None:
    assert ENTITY_INDEX_BITS == 32
    assert GENERATION_BITS == 32