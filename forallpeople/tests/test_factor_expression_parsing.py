"""
Regression tests for factor-expression parsing.

``evaluate_factor_expression`` previously scraped numbers and operators out of
the expression with a regex and folded them strictly left to right.  That
ignored operator precedence, silently discarded parentheses, and did not
understand scientific notation, so several *shipped* unit definitions were
loaded with the wrong Factor:

    us_customary/thermal  psi    0.3048**2/12**2/0.45359237/9.80665   10.8x low
    us_customary/thermal  ksi    (same, /1000)                        10.8x low
    structural/us_cust.   pci    0.3048**3/12**3/0.45359237/9.80665  1247x low
    structural/us_cust.   kci    (same, /1000)                       1247x low
    structural            lbft2  1/0.45359237/9.80665/0.3048**2        4.4x high
    structural            kft2   (same, /1000)                         4.4x high
    thermal               bar    1/1e5                            20000x high

The definitions themselves were correct -- only the parser disagreed with
them.  Expressions written purely left to right (``1/0.45359237/9.80665``)
were unaffected, which is why the majority of units were always right and no
existing test caught this.

The expression is now parsed with Python's own grammar via ``ast`` and
evaluated over ``Fraction``, so precedence, parentheses and scientific
notation are honoured and the result stays exact.
"""

from fractions import Fraction

import pytest

import forallpeople as si
from forallpeople.environment import evaluate_factor_expression as ev

si.environment("test_definitions", top_level=True)


# ---------------------------------------------------------------------------
# Operator precedence, parentheses, scientific notation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("1+2*3", Fraction(7)),  # was 9: (1+2)*3
        ("2*3+1", Fraction(7)),  # unchanged, already left-to-right
        ("1-2*3", Fraction(-5)),  # was -3: (1-2)*3
        ("2**3*2", Fraction(16)),
        ("1/(2*3)", Fraction(1, 6)),  # was 3/2: parentheses discarded
        ("(1+1)**3", Fraction(8)),  # was 2: '(1+1)' seen as 1, 1
        ("1/1e5", Fraction(1, 100000)),  # was 1/5: 'e' dropped
        ("2.5e-3", Fraction(1, 400)),
        ("-1/4", Fraction(-1, 4)),
        ("1/2/2", Fraction(1, 4)),  # unchanged
    ],
)
def test_expression_follows_python_arithmetic(expression, expected):
    assert ev(expression) == expected


def test_result_is_exact_not_float():
    """Factors must stay rational so repeated conversion does not drift."""
    result = ev("0.3048**2/12**2/0.45359237/9.80665")
    assert isinstance(result, Fraction)
    # 1 psi == 6894.757293168361 Pa exactly, by definition of lbf and inch
    assert result == Fraction(1290320000, 8896443230521)


def test_plain_numbers_are_accepted():
    """A JSON Factor given as a number, not a string, must not crash."""
    assert ev(0.001) == Fraction(1, 1000)
    assert ev(12) == Fraction(12)
    assert ev("1") == Fraction(1)


# ---------------------------------------------------------------------------
# Shipped definitions now load with their physically correct values
# ---------------------------------------------------------------------------

LBF = Fraction("0.45359237") * Fraction("9.80665")  # N per lbf
INCH = Fraction("0.0254")  # m per inch
FOOT = Fraction("0.3048")  # m per foot


@pytest.mark.parametrize(
    "expression, expected",
    [
        # psi / ksi -- lbf per square inch
        ("0.3048**2/12**2/0.45359237/9.80665", INCH**2 / LBF),
        ("0.3048**2/12**2/0.45359237/9.80665/1000", INCH**2 / LBF / 1000),
        # pci / kci -- lbf per cubic inch
        ("0.3048**3/12**3/0.45359237/9.80665", INCH**3 / LBF),
        ("0.3048**3/12**3/0.45359237/9.80665/1000", INCH**3 / LBF / 1000),
        # lbft2 / kft2 -- lbf times square foot
        ("1/0.45359237/9.80665/0.3048**2", 1 / (LBF * FOOT**2)),
        ("1/0.45359237/9.80665/0.3048**2/1000", 1 / (LBF * FOOT**2) / 1000),
        # bar -- 1e5 Pa
        ("1/1e5", Fraction(1, 100000)),
    ],
)
def test_shipped_factors_match_physical_definitions(expression, expected):
    assert ev(expression) == expected


def test_the_two_psi_spellings_now_agree():
    """structural.json writes psi in inches, us_customary in feet-and-twelfths.

    Both describe the same unit; before the fix only the first parsed correctly.
    """
    in_inches = ev("0.0254**2/0.45359237/9.80665")
    in_feet = ev("0.3048**2/12**2/0.45359237/9.80665")
    assert in_inches == in_feet


def test_left_to_right_expressions_are_unchanged():
    """The majority of shipped factors were already correct; keep them so."""
    assert ev("1/0.3048") == 1 / Fraction("0.3048")
    assert ev("12/0.3048") == 12 / Fraction("0.3048")
    assert ev("1/0.45359237/9.80665") == 1 / LBF
    assert ev("0.3048**2/0.45359237/9.80665") == FOOT**2 / LBF
    assert ev("1/3600/24") == Fraction(1, 86400)


# ---------------------------------------------------------------------------
# Only arithmetic is permitted
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('echo hi')",
        "open('secret')",
        "1 + foo",
        "[1, 2, 3]",
        "{'a': 1}",
        "1 if True else 2",
        "lambda: 1",
    ],
)
def test_non_arithmetic_is_rejected(expression):
    with pytest.raises((ValueError, SyntaxError)):
        ev(expression)


@pytest.mark.parametrize("bad_factor", ["1/", "1 +", "**2", "one/two"])
def test_environment_load_reports_a_bad_factor(tmp_path, bad_factor):
    """A malformed Factor must raise ValueError naming the offending unit.

    ``_load_environment`` is called directly rather than through
    ``si.environment(...)``: Environment is a process-wide singleton that
    strips the previous unit names from the namespace *before* loading, so a
    failed load through the public entry point would leave the rest of the
    suite without its units.
    """
    bad = tmp_path / "bad_env.json"
    bad.write_text(
        '{"widget": {"Dimension": [0,1,0,0,0,0,0], "Factor": "%s", "Symbol": "w"}}'
        % bad_factor,
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        si.environment._load_environment(str(bad)[: -len(".json")])
