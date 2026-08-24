"""
Regression tests for the display of factored quantities that land on a
dimension the environment has no symbol for.

``Physical._repr_template_`` builds the unit string in three branches.  When
the environment has no symbol for the quantity's dimensions and those
dimensions are not a multiple of a single basis vector, the unit string falls
back to plain SI base units (``kg.m.s^-3``).  That branch is not eligible for
a prefix, so ``prefix_bool`` is False and the displayed value was left as
``val * factor`` -- a value scaled into a unit that is not the one printed
beside it.

    >>> si.environment("test_definitions", top_level=True)
    >>> 100 * lb / (2 * s)
    50.000 kg.m.s^-3        # the quantity is 222.411 N/s

The stored ``.value`` was always correct; only the rendering was wrong, which
makes it the worst kind of failure for a calculation sheet -- a plausible
number with authoritative-looking units.

Branches that DO find a symbol (``N/m``, ``kN.m^2``, ``lb``) recompute the
display value from ``val`` and were always correct, which is why this went
unnoticed: it only bites on dimensions the environment does not name.

The fix displays the base-unit value against a base-unit string.
"""

import builtins

import pytest

import forallpeople as si

si.environment("test_definitions", top_level=True)

lb = builtins.lb
sec = builtins.s
mtr = builtins.m
kgm = builtins.kg


# ---------------------------------------------------------------------------
# The bug
# ---------------------------------------------------------------------------


def test_factored_quantity_on_unnamed_dimension_shows_base_unit_value():
    """lb/s has no symbol in the environment, so it renders in base units."""
    q = 100 * lb / (2 * sec)
    # 100 lb = 444.822 N; over 2 s that is 222.411 N/s
    assert q.value == pytest.approx(222.41108076302504)
    assert repr(q).startswith("222.411")
    assert "50.000" not in repr(q)


def test_matches_the_equivalent_unfactored_quantity():
    """The same physical quantity must print the same number either way."""
    from_lb = 100 * lb / (2 * sec)
    from_si = 222.41108076302504 * builtins.N / sec
    assert from_lb.value == pytest.approx(from_si.value)
    assert repr(from_lb) == repr(from_si)


# ---------------------------------------------------------------------------
# Everything that already worked must keep working
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "quantity, expected",
    [
        # a factored unit whose own dimension IS named
        (lambda: 100 * lb, "100.000 lb"),
        # factored, lands on a dimension the environment DOES name: the
        # factor is applied, and must still be (test_collision_unit, 'tcu',
        # shares lb's factor by design -- see test_fix_factor_index_collision)
        (lambda: 100 * lb / (2 * mtr), "50.000 tcu"),
        # unfactored, prefix machinery
        (lambda: 2 * kgm, "2.000 kg"),
        (lambda: 35267 * kgm, "35.267 Mg"),
        # explicit prefix on a mass (the PR #124 path)
        (lambda: (35267 * kgm).prefix("k"), "35267.000 kg"),
        # unfactored on an unnamed dimension -- unchanged by this fix
        (lambda: 7850 * kgm / mtr**3, "7850.000 kg·m⁻³"),
        # single-basis-vector multiple, prefix branch
        (lambda: 2 * mtr**2, "2.000 m²"),
    ],
)
def test_unaffected_paths_are_unchanged(quantity, expected):
    assert repr(quantity()) == expected


def test_latex_and_html_templates_agree_with_repr():
    q = 100 * lb / (2 * sec)
    assert "222.411" in q.latex
    assert "222.411" in q.html
    assert "50.000" not in q.latex
    assert "50.000" not in q.html


def test_format_spec_is_respected():
    q = 100 * lb / (2 * sec)
    assert f"{q:.1f}".startswith("222.4")
    assert f"{q:.3f}".startswith("222.411")
