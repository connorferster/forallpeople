"""
Defined units display as their unit alone ("kN", not "1 kN"), from 4.0, with
a temporary escape hatch (legacy_unit_repr, FORALLPEOPLE_LEGACY_UNIT_REPR).
"""

import os
import subprocess
import sys
import warnings

import pytest

import forallpeople as si
from forallpeople.dimensions import Dimensions


@pytest.fixture(autouse=True)
def structural():
    si.environment("structural")
    yield
    si.legacy_unit_repr(False)


def test_defined_units_are_flagged():
    assert si.kN.is_unit and si.mm.is_unit and si.MPa.is_unit
    assert si.m.is_unit and si.kg.is_unit  # the SI base units


@pytest.mark.parametrize(
    "unit, text, latex, html",
    [
        ("kN", "kN", "\\mathrm{kN}", "kN"),
        ("mm", "mm", "\\mathrm{mm}", "mm"),
        ("MPa", "MPa", "\\mathrm{MPa}", "MPa"),
        ("m", "m", "\\mathrm{m}", "m"),
    ],
)
def test_a_defined_unit_displays_bare(unit, text, latex, html):
    physical = getattr(si, unit)
    assert repr(physical) == str(physical) == text
    assert physical.latex == latex
    assert physical.html == html
    assert f"{physical:.2f}" == text


@pytest.mark.parametrize(
    "expression",
    [
        lambda: 1 * si.kN,
        lambda: si.kN * 1,
        lambda: si.kN / 1,
        lambda: si.kN + 0 * si.kN,
        lambda: -(-si.kN),
        lambda: abs(si.kN),
        lambda: si.kN * si.m / si.m,
    ],
)
def test_a_calculated_value_shows_its_number(expression):
    result = expression()
    assert not result.is_unit
    assert repr(result) == "1.000 kN"


def test_a_product_of_units_shows_its_number():
    assert repr(si.kN * si.m) == "1.000 kN·m"


def test_prefix_and_round_keep_the_flag():
    assert repr(round(si.kN, 1)) == "kN"
    assert si.kN.prefix("k").is_unit
    # Shown in another unit, the number is not 1, so it is shown.
    assert repr(si.kN.prefix("unity")) == "1000.000 N"


def test_a_defined_constant_keeps_its_number():
    g = si.Physical(9.81, Dimensions(0, 1, -2, 0, 0, 0, 0), 1, is_unit=True)
    assert repr(g) == "9.810 m·s⁻²"


def test_the_flag_is_not_part_of_the_quantity():
    assert si.kN == 1 * si.kN
    assert hash(si.kN) == hash(1 * si.kN)
    data = si.kN.to_dict()
    assert "is_unit" not in data
    assert not si.Physical.from_dict(data).is_unit


def test_display_and_float_are_unchanged():
    assert si.kN.display().magnitude == 1
    assert si.kN.display().unit == "kN"
    assert float(si.kN) == 1


def test_legacy_unit_repr():
    with pytest.warns(FutureWarning, match="removed in forallpeople 5.0"):
        si.legacy_unit_repr(True)
    assert repr(si.kN) == "1.000 kN"
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        si.legacy_unit_repr(False)
    assert repr(si.kN) == "kN"


def test_legacy_unit_repr_environment_variable():
    code = (
        "import warnings; warnings.simplefilter('always')\n"
        "import forallpeople as si\n"
        "si.environment('structural')\n"
        "print(repr(si.kN))\n"
    )
    env = dict(os.environ, FORALLPEOPLE_LEGACY_UNIT_REPR="1")
    result = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True
    )
    assert result.stdout.strip() == "1.000 kN"
    assert "FutureWarning" in result.stderr
