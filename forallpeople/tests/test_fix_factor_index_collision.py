"""
Focused regression tests for the factor-index collision fix
(branch: fix_factor_index_collision).

These tests exercise only the behaviour changed on this branch:

  * environment.Environment builds ``_units_by_factor`` by *accumulating*
    every unit that shares a numeric Factor, instead of overwriting so that
    only the last-loaded unit survives.
  * physical_helper_functions._get_units_by_factor resolves a factor key to
    the single candidate whose Dimension matches the queried dims, rather
    than blindly inspecting the first candidate.

The ``test_definitions`` environment contains a deliberate collision:
``lb`` (Dimension [1,1,-2], a force) and ``test_collision_unit`` (Dimension
[1,0,-2], a force-per-length) share the identical Factor
``1/0.45359237/9.80665``.
"""

from fractions import Fraction

import forallpeople as si
import forallpeople.physical_helper_functions as phf

# Push the test environment to the top level so the unit names (lb, ft, ...)
# and the internal factor index are available for these tests.
si.environment("test_definitions", top_level=True)

env_fact = si.environment.units_by_factor

# Dimension vectors used throughout.
FORCE_DIMS = si.Dimensions(1, 1, -2, 0, 0, 0, 0)          # lb
SPRING_DIMS = si.Dimensions(1, 0, -2, 0, 0, 0, 0)         # test_collision_unit
LENGTH_DIMS = si.Dimensions(0, 1, 0, 0, 0, 0, 0)          # no factor match

# lb and test_collision_unit are defined with the identical Factor string.
SHARED_FACTOR = Fraction(1) / Fraction("0.45359237") / Fraction("9.80665")


# ---------------------------------------------------------------------------
# environment.py — factor index accumulation
# ---------------------------------------------------------------------------

def test_factor_index_accumulates_units_with_shared_factor():
    """Both units that share a Factor must coexist under the same key in
    _units_by_factor; neither may silently overwrite the other."""
    bucket = env_fact().get(lb.factor, {})  # noqa: F821 - injected by environment
    assert "lb" in bucket
    assert "test_collision_unit" in bucket


def test_factor_index_key_matches_shared_factor_value():
    """The collision bucket is stored under the shared numeric factor."""
    assert lb.factor == SHARED_FACTOR  # noqa: F821 - injected by environment
    assert SHARED_FACTOR in env_fact()


def test_factor_index_preserves_distinct_definitions():
    """Accumulation must keep each definition intact (correct Dimension and
    Symbol), not merge or clobber their contents."""
    bucket = env_fact().get(SHARED_FACTOR, {})
    assert bucket["lb"]["Dimension"] == FORCE_DIMS
    assert bucket["test_collision_unit"]["Dimension"] == SPRING_DIMS
    assert bucket["test_collision_unit"]["Symbol"] == "tcu"


# ---------------------------------------------------------------------------
# physical_helper_functions.py — dimension-aware factor lookup
# ---------------------------------------------------------------------------

def test_get_units_by_factor_picks_force_on_collision():
    """Querying the shared factor with force dims returns lb, not the
    force-per-length collision unit."""
    result = phf._get_units_by_factor(lb.factor, FORCE_DIMS, env_fact, 1)  # noqa: F821
    assert "lb" in result
    assert "test_collision_unit" not in result


def test_get_units_by_factor_picks_spring_on_collision():
    """Querying the shared factor with force-per-length dims returns the
    collision unit, not lb."""
    result = phf._get_units_by_factor(lb.factor, SPRING_DIMS, env_fact, 1)  # noqa: F821
    assert "test_collision_unit" in result
    assert "lb" not in result


def test_get_units_by_factor_returns_single_entry_on_collision():
    """The lookup narrows a multi-candidate bucket down to exactly one unit."""
    result = phf._get_units_by_factor(lb.factor, SPRING_DIMS, env_fact, 1)  # noqa: F821
    assert len(result) == 1


def test_get_units_by_factor_returns_empty_when_no_dimension_match():
    """A factor that matches the bucket but no candidate's Dimension yields
    an empty dict — accumulation must not create false positives."""
    result = phf._get_units_by_factor(lb.factor, LENGTH_DIMS, env_fact, 1)  # noqa: F821
    assert result == {}


def test_get_units_by_factor_returns_empty_when_factor_unknown():
    """A factor with no bucket at all still resolves to an empty dict."""
    unknown_factor = 1234.5678
    result = phf._get_units_by_factor(unknown_factor, FORCE_DIMS, env_fact, 1)
    assert result == {}


# ---------------------------------------------------------------------------
# End-to-end: repr resolves the correct unit despite the collision
# ---------------------------------------------------------------------------

def test_repr_resolves_force_unit_despite_collision():
    """An lb-dimensioned quantity still renders as lb even though another
    unit shares its factor."""
    quantity = 10 * lb  # noqa: F821 - injected by environment
    assert "lb" in repr(quantity)


def test_repr_resolves_collision_unit_despite_shared_factor():
    """A force-per-length quantity built from the collision unit renders with
    its own symbol, proving the correct branch of the factor index is used."""
    quantity = 10 * test_collision_unit  # noqa: F821 - injected by environment
    assert "tcu" in repr(quantity)
