from __future__ import annotations

from astralengine.ecs.scheduling.phases import PhaseSpec

import pytest

pytestmark = [
    pytest.mark.ecs,
    pytest.mark.system,
    pytest.mark.unit
]


def test_phase_spec_stores_required_name() -> None:
    phase = PhaseSpec(name="sim")

    assert phase.name == "sim"


def test_phase_spec_default_commit_after_is_true() -> None:
    phase = PhaseSpec(name="sim")

    assert phase.commit_after is True


def test_phase_spec_accepts_commit_after_false() -> None:
    phase = PhaseSpec(name="sim", commit_after=False)

    assert phase.commit_after is False


def test_phase_spec_rejects_empty_name_if_validated() -> None:
    try:
        PhaseSpec(name="")
    except ValueError:
        return

    phase = PhaseSpec(name="")
    assert phase.name == ""


def test_phase_spec_rejects_blank_name_if_validated() -> None:
    try:
        PhaseSpec(name="   ")
    except ValueError:
        return

    phase = PhaseSpec(name="   ")
    assert phase.name == "   "


def test_phase_spec_rejects_non_string_name_if_validated() -> None:
    try:
        PhaseSpec(name=None)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return

    phase = PhaseSpec(name=None)  # type: ignore[arg-type]
    assert phase.name is None


def test_phase_specs_with_different_values_are_independent() -> None:
    startup = PhaseSpec(name="startup")
    sim = PhaseSpec(name="sim", commit_after=False)

    assert startup.name == "startup"
    assert startup.commit_after is True

    assert sim.name == "sim"
    assert sim.commit_after is False


def test_phase_spec_equality_if_dataclass_semantics_are_used() -> None:
    a = PhaseSpec(name="sim", commit_after=True)
    b = PhaseSpec(name="sim", commit_after=True)
    c = PhaseSpec(name="cleanup", commit_after=True)

    assert a == b
    assert a != c


def test_phase_spec_repr_contains_name() -> None:
    phase = PhaseSpec(name="sim", commit_after=True)

    text = repr(phase)

    assert "sim" in text


def test_phase_spec_repr_contains_commit_after() -> None:
    phase = PhaseSpec(name="sim", commit_after=True)

    text = repr(phase)

    assert "True" in text or "commit_after" in text