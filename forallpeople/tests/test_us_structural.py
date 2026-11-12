"""
Tests for the us_structural environment, Default units and Physical.display().
"""

import json
import math
import pathlib
from fractions import Fraction

import pytest

import forallpeople as si
from forallpeople import Display

ENVIRONMENTS = pathlib.Path(si.__file__).parent / "environments"

# The SI size of each base unit, from its legal definition.
LB = 0.45359237 * 9.80665  # N
KIP = 1000 * LB
IN = 0.0254  # m
FT = 0.3048  # m

# Name -> (force, length, power of length) for the units named for their use.
NAMED = {
    "psi": (LB, IN, -2),
    "psf": (LB, FT, -2),
    "ksi": (KIP, IN, -2),
    "ksf": (KIP, FT, -2),
    "pci": (LB, IN, -3),
    "pcf": (LB, FT, -3),
    "kci": (KIP, IN, -3),
    "kcf": (KIP, FT, -3),
}


def si_size(name: str) -> float:
    """The SI value of 1 of the unit 'name', from the name alone."""
    simple = {"inch": IN, "ft": FT, "lbm": 0.45359237, "lb": LB, "kip": KIP}
    if name in simple:
        return simple[name]
    if name in NAMED:
        force, length, power = NAMED[name]
        return force * length**power
    # e.g. kipin2 (kip·in²) or lb_ft4 (lb/ft⁴)
    force = KIP if name.startswith("kip") else LB
    rest = name.removeprefix("kip").removeprefix("lb")
    length = IN if "in" in rest else FT
    power = int(rest[-1]) if rest[-1].isdigit() else 1
    if rest.startswith("_"):
        power = -power
    return force * length**power


@pytest.fixture
def us():
    si.environment("us_structural")
    yield si
    si.environment("default")


DEFINITIONS = json.loads(
    (ENVIRONMENTS / "us_structural.json").read_text(encoding="utf-8")
)


@pytest.mark.parametrize("name", list(DEFINITIONS))
def test_each_unit(us, name):
    unit = getattr(us, name)
    symbol = DEFINITIONS[name]["Symbol"]
    assert str(unit) == f"1.000 {symbol}"
    assert math.isclose(unit.value, si_size(name), rel_tol=1e-12)
    assert math.isclose(float(unit), 1)
    assert us.parse(f"2.5 {symbol}").value == pytest.approx(2.5 * unit.value)


def test_complete_force_length_assortment():
    # Force times or over length**1 to length**4, for lb and kip, in and ft.
    dims = {tuple(d["Dimension"]) for d in DEFINITIONS.values()}
    for n in range(1, 5):
        assert (1, 1 + n, -2, 0, 0, 0, 0) in dims
        assert (1, 1 - n, -2, 0, 0, 0, 0) in dims
    assert len(DEFINITIONS) == 5 + 4 * 2 * 2 * 2


def test_one_default_per_dimension():
    defaults = [tuple(d["Dimension"]) for d in DEFINITIONS.values() if d.get("Default")]
    assert len(defaults) == len(set(defaults))


@pytest.mark.parametrize(
    "expression, expected",
    [
        (lambda u: 2 * u.kip * (3 * u.ft), "6.000 kip·ft"),
        (lambda u: 4 * u.psi * (3 * u.inch) ** 2, "36.000 lb"),
        (lambda u: 2 * u.ksi * (10 * u.inch) ** 4, "20000.000 kip·in²"),
        (lambda u: 3 * u.lb / u.inch**3, "3.000 pci"),
        (lambda u: 3 * u.kip / u.ft**4, "3.000 kip/ft⁴"),
        (lambda u: 2 * u.kip / u.ft * (20 * u.ft) ** 2 / 8, "100.000 kip·ft"),
    ],
)
def test_products_land_on_defined_units(us, expression, expected):
    assert str(expression(us)) == expected


@pytest.mark.parametrize(
    "expression, expected",
    [
        # in²·ksi / (psi·in): a length, with a ksi/psi factor of 1000 in it
        (
            lambda u: 2.37
            * u.inch**2
            * (60 * u.ksi)
            / (0.85 * 4000 * u.psi * 12 * u.inch),
            "3.485 in",
        ),
        (lambda u: 2 * u.ft * (6 * u.inch), "144.000 in²"),
        (lambda u: 5 * u.psi * (2 * u.ft) ** 2, "2.880 kip"),
        (lambda u: 30 * u.kip / (3 * u.ft * u.inch), "0.833 ksi"),
        (lambda u: 1 * u.kip * u.ft * u.ft / u.inch, "12.000 kip·ft"),
    ],
)
def test_mixed_units_use_the_defaults(us, expression, expected):
    value = expression(us)
    assert str(value) == expected
    assert float(value) == pytest.approx(float(expected.split()[0]), abs=1e-3)


def test_default_unit_powers_are_scaled(us):
    # A length² with the factor of ft (not ft²) is shown in in², the default
    # length squared, with the number scaled to in².
    area = 2 * us.ft * (3 * us.ft) * us.m / us.ft
    assert str(area) == f"{area.value / IN**2:.3f} in²"


def test_si_values_ignore_defaults(us):
    assert str(3 * us.m) == "3.000 m"


class TestDisplay:
    def test_defined_unit(self, us):
        shown = (12 * us.kip * us.ft).display()
        assert shown == Display(pytest.approx(12), "kip·ft", (us.kip * us.ft).factor)
        assert isinstance(shown.factor, Fraction)

    def test_factor_relates_magnitude_to_value(self, us):
        for value in (12 * us.kip * us.ft, 4.5 * us.psf, 300 * us.inch**4):
            shown = value.display()
            assert shown.magnitude == pytest.approx(value.value * float(shown.factor))

    def test_prefix_is_an_exact_power_of_ten(self):
        si.environment("default")
        assert (0.3 * si.m).display() == Display(pytest.approx(300), "mm", 1000)
        assert (0.3 * si.m).display().factor == Fraction(1000)
        assert (5000 * si.kg).display() == Display(
            pytest.approx(5), "Mg", Fraction(1, 1000)
        )
        assert (3 * si.m).display() == Display(3, "m", 1)

    def test_zero(self):
        si.environment("default")
        assert (0 * si.m).display() == Display(0, "m", 1)

    def test_default_unit(self, us):
        a = 2.37 * us.inch**2 * (60 * us.ksi) / (0.85 * 4000 * us.psi * 12 * us.inch)
        shown = a.display()
        assert shown.unit == "in"
        assert shown.factor == Fraction(1) / Fraction("0.0254")

    def test_no_matching_unit_is_si(self, us):
        # A mass with a factor no unit has (lbm/12), and no default mass unit.
        value = 24 * us.lbm * us.ft / us.inch
        shown = value.display()
        assert shown.unit == "kg"
        assert shown.factor == 1
        assert shown.magnitude == pytest.approx(value.value)
        assert float(value) == pytest.approx(value.value)

    def test_templates(self, us):
        assert (2 * us.kip * us.inch**2).display("latex").unit == (
            r"\mathrm{kip} \cdot \mathrm{in²}"
        )
        assert (2 * us.inch**2).display("latex").unit == r"\mathrm{in}^{2}"
        assert (2 * us.inch**2).display("html").unit == "in<sup>2</sup>"
        assert (2 * us.inch**2).display().unit == "in²"

    def test_matches_str(self, us):
        for value in (12 * us.kip * us.ft, 7 * us.inch**3, 0.25 * us.kcf):
            shown = value.display()
            assert str(value) == f"{shown.magnitude:.3f} {shown.unit}"


def test_float_is_the_displayed_number():
    si.environment("default")
    # A compound unit with no symbol is not prefixed, so float() is not either.
    value = 40000 * si.A * si.kg
    assert str(value) == "40000.000 kg·A"
    assert float(value) == 40000


def test_factor_match_tolerance_is_relative():
    from forallpeople.physical_helper_functions import _match_factors

    tiny = Fraction(1, 10**10)
    index = {tiny: {"x": {}}}
    assert _match_factors(tiny * (1 + Fraction(1, 10**12)), index) == {"x": {}}
    # Twice the factor is a different unit, however small both are.
    assert _match_factors(2 * tiny, index) == {}
