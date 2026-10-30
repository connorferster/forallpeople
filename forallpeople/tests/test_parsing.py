"""
Tests for parsing physical quantities from text (si.parse / si.parse_tree).
"""

import builtins
import math

import pytest

import forallpeople as si
from forallpeople.dimensions import DimensionError
from forallpeople.environment import Environment


@pytest.fixture(autouse=True, scope="module")
def structural_environment():
    # Other test modules load "test_definitions" at the top level at import
    # time, so load "structural" only while this module runs, then restore it.
    si.environment("structural")
    yield
    si.environment("test_definitions", top_level=True)


def same(a, b):
    return (
        type(a) is type(b)
        and a == b
        and getattr(a, "factor", None) == getattr(b, "factor", None)
    )


@pytest.mark.parametrize(
    "text, expected",
    [
        ("350 MPa", lambda: 350 * si.MPa),
        ("4.5 kN/m", lambda: 4.5 * si.kN / si.m),
        ("164e6 mm**4", lambda: 164e6 * si.mm**4),
        ("164e6 mm^4", lambda: 164e6 * si.mm**4),
        ("164e6 mm⁴", lambda: 164e6 * si.mm**4),
        ("30 kN·m", lambda: 30 * si.kN * si.m),
        ("30 kN*m", lambda: 30 * si.kN * si.m),
        ("30 kN⋅m", lambda: 30 * si.kN * si.m),
        ("5 kip·ft", lambda: 5 * si.kipft),
        ("4.5 N/m", lambda: 4.5 * si.N_m),
        ("2 ft", lambda: 2 * si.ft),
        ("350MPa", lambda: 350 * si.MPa),
        ("  350   MPa  ", lambda: 350 * si.MPa),
        ("-1.5e3 N", lambda: -1.5e3 * si.N),
        ("1_000 N", lambda: 1000 * si.N),
        (".5 m", lambda: 0.5 * si.m),
        ("7 m/s**2", lambda: 7 * si.m / si.s**2),
        ("7 m·s⁻²", lambda: 7 * si.m / si.s**2),
        ("7 m*s^-2", lambda: 7 * si.m / si.s**2),
        ("7 m*s**(-2)", lambda: 7 * si.m / si.s**2),
        ("2 kN/m/s", lambda: (2 * si.kN / si.m) / si.s),
        ("3 kN·m/(m·s)", lambda: 3 * si.kN * si.m / (si.m * si.s)),
        ("2 (kN·m)^2", lambda: 2 * (si.kN * si.m) ** 2),
        ("4 m⁰'⁵", lambda: 4 * si.m**0.5),
        ("500 μm", lambda: 500e-6 * si.m),
        ("500 um", lambda: 500e-6 * si.m),
        ("500 µm", lambda: 500e-6 * si.m),
        ("3 cm", lambda: 0.03 * si.m),
        ("3 ms", lambda: 0.003 * si.s),
        ("3 g", lambda: 0.003 * si.kg),
        ("3 mg", lambda: 3e-6 * si.kg),
        ("2 kN/m³", lambda: 2000 * si.N_m3),
        ("0.9", lambda: 0.9),
        ("3", lambda: 3.0),
        ("5 m/m", lambda: 5.0),
    ],
)
def test_grammar(text, expected):
    assert same(si.parse(text), expected())


def test_symbol_aliases_keep_factors():
    q = si.parse("5 kip·ft")
    assert q.factor == si.kipft.factor
    assert str(q) == "5.000 kip·ft"
    assert si.parse("12 lb/ft").factor == si.lb_ft.factor
    assert str(si.parse("2 ft")) == "2.000 ft"


@pytest.mark.parametrize(
    "text, display, prefixed, value",
    [
        ("0.6 kPa", "0.600 kPa", "k", 600.0),
        ("4000 mm", "4000.000 mm", "m", 4.0),
        ("1200 mm", "1200.000 mm", "m", 1.2),
        ("350 MPa", "350.000 MPa", "M", 350e6),
        ("12 kN", "12.000 kN", "k", 12000.0),
        ("1.2 kN·m", "1.200 kN·m", "k", 1200.0),
        ("3 um", "3.000 μm", "μ", 3e-6),
        ("500 mg", "500.000 mg", "m", 0.0005),
        ("6 m", "6.000 m", "", 6.0),
        ("500 g", "500.000 g", "", 0.5),
        ("2 kg", "2.000 kg", "", 2.0),
        ("1.2 kN*m", "1.200 kN·m", "", 1200.0),
        ("4.9 kN/m^3", "4.900 kN/m³", "", 4900.0),
        ("164e6 mm^4", "164000000.000 mm⁴", "", 164e-6),
        ("5 kip", "5.000 kip", "", 5 * 4448.2216152605),
        ("2 ft", "2.000 ft", "", 0.6096),
    ],
)
def test_display_keeps_the_authored_prefix(text, display, prefixed, value):
    q = si.parse(text)
    assert str(q) == display
    assert q.prefixed == prefixed
    assert math.isclose(q.value, value)  # .value stays SI


def test_float_follows_the_authored_prefix():
    assert float(si.parse("0.6 kPa")) == pytest.approx(0.6)
    assert float(si.parse("4000 mm")) == pytest.approx(4000.0)
    assert si.parse("0.6 kPa").value == pytest.approx(600.0)


def test_arithmetic_on_a_parsed_prefixed_value():
    area = si.parse("4000 mm") ** 2
    assert isinstance(area, si.Physical)
    assert area == si.parse("16 m^2")
    assert str(area) == "16000000.000 mm²"
    assert str(si.parse("0.6 kPa") * 2) == "1.200 kPa"
    assert str(si.parse("0.6 kPa") * si.parse("4 m")) == "2.400 kN/m"


def test_a_parsed_prefix_survives_serialization():
    q = si.Physical.from_dict(si.parse("0.6 kPa").to_dict())
    assert str(q) == "0.600 kPa"
    assert q.prefixed == "k"


def test_expect_with_a_parsed_prefix():
    assert str(si.parse("0.6 kPa", expect="Pa")) == "0.600 kPa"


def test_parenthesised_number_is_an_error():
    with pytest.raises(si.UnitParseError, match="does not start with a number"):
        si.parse("(6 m)")


def test_power_keeps_units():
    # A prefix set by parse is carried through __pow__ rather than dropping units
    area = si.parse("6 m") ** 2
    assert isinstance(area, si.Physical)
    assert area == 36 * si.m**2
    assert isinstance(si.parse("1200 mm") ** 2, si.Physical)


def test_unknown_unit_with_suggestion():
    with pytest.raises(si.UnitParseError) as err:
        si.parse("30 kNm")
    message = str(err.value)
    assert "'kNm' is not a unit in environment 'structural'" in message
    assert "Did you mean 'kN·m' (Nm)" in message


def test_space_separated_units_rejected_with_hint():
    with pytest.raises(si.UnitParseError, match="use '·' or '\\*'"):
        si.parse("30 kN m")


@pytest.mark.parametrize(
    "text",
    ["3 kN/", "3 kN(m)", "3 (kN", "3 kN)", "3 kN**", "3 kN·*m", "3 kN#", "3 2"],
)
def test_malformed_expressions(text):
    with pytest.raises(si.UnitParseError):
        si.parse(text)


@pytest.mark.parametrize("bad", ["", "MPa", "abc", None, 5])
def test_not_a_quantity(bad):
    with pytest.raises(si.UnitParseError):
        si.parse(bad)


def test_errors_are_value_errors():
    assert issubclass(si.UnitParseError, ValueError)


def test_expect():
    assert si.parse("350 MPa", expect="MPa") == 350 * si.MPa
    assert si.parse("350 kPa", expect="MPa") == 350 * si.kPa
    assert si.parse("350 kPa", expect=si.MPa) == 350 * si.kPa
    assert si.parse("0.9", expect="m/m") == 0.9
    with pytest.raises(DimensionError, match="Expected the dimensions of MPa.*kN"):
        si.parse("350 kN", expect="MPa")
    with pytest.raises(DimensionError, match="dimensionless"):
        si.parse("0.9", expect="MPa")


def test_parse_before_environment_loaded():
    fresh = Environment(si.Physical, builtins, si._the_si_base_units)
    assert same(fresh.parse("5 m/s"), 5 * si.m / si.s)
    assert same(fresh.parse("5 km"), 5000 * si.m)
    with pytest.raises(si.UnitParseError, match="no environment has been loaded"):
        fresh.parse("5 kN")


def test_module_and_environment_methods_agree():
    assert si.environment.parse("4.5 kN/m") == si.parse("4.5 kN/m")


def test_parse_tree():
    data = {
        "material": {"fy": "350 MPa", "grade": "G40.21 350W", "E": "200 GPa"},
        "section": "W310x74",
        "loads": ["4.5 kN/m", {"P": "30 kN"}, 12, None, True],
        "phi": "0.9",
        "n": 3,
        "pair": ("2 m", "x"),
        "350 MPa": "key is not parsed",
    }
    tree = si.parse_tree(data)
    assert same(tree["material"]["fy"], 350 * si.MPa)
    assert tree["material"]["grade"] == "G40.21 350W"
    assert same(tree["material"]["E"], 200 * si.GPa)
    assert tree["section"] == "W310x74"
    assert same(tree["loads"][0], 4.5 * si.kN / si.m)
    assert same(tree["loads"][1]["P"], 30 * si.kN)
    assert tree["loads"][2:] == [12, None, True]
    assert tree["phi"] == 0.9
    assert tree["n"] == 3
    assert isinstance(tree["pair"], tuple) and same(tree["pair"][0], 2 * si.m)
    assert tree["350 MPa"] == "key is not parsed"
    assert data["material"]["fy"] == "350 MPa"  # input is not modified


def test_parse_tree_strict_error_has_path():
    data = {"geometry": {"levels": "2 storeys"}, "loads": ["1 kN", "2 kNm"]}
    with pytest.raises(si.UnitParseError, match=r"^geometry\.levels: '2 storeys'"):
        si.parse_tree(data)
    with pytest.raises(si.UnitParseError, match=r"^loads\[1\]: '2 kNm'"):
        si.parse_tree({"loads": data["loads"]})
    with pytest.raises(si.UnitParseError, match=r"^'2 storeys'"):
        si.parse_tree("2 storeys")


def test_parse_tree_non_strict():
    tree = si.parse_tree({"levels": "2 storeys", "h": "3 m"}, strict=False)
    assert tree["levels"] == "2 storeys"
    assert same(tree["h"], 3 * si.m)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("12", 12.0),
        (" 3.5 ", 3.5),
        ("1e-3", 0.001),
        ("350 MPa", "350.000 MPa"),
        ("4.9 kN/m^3", "4.900 kN/m³"),
        ("164e6 mm^4", "164000000.000 mm⁴"),
        ("000.000.000", "000.000.000"),
        ("2026-014", "2026-014"),
        ("2026-10-29", "2026-10-29"),
        ("1.2.3", "1.2.3"),
        ("38x140", "38x140"),
        ("2x10", "2x10"),
        ("350MPa", "350MPa"),
    ],
)
@pytest.mark.parametrize("strict", [True, False])
def test_parse_tree_quantity_candidates(text, expected, strict):
    # A quantity str is a number, alone or followed by whitespace and unit
    # text; anything glued to the number leaves the str alone.
    tree = si.parse_tree({"site": {"items": [{"v": text}]}}, strict=strict)
    result = tree["site"]["items"][0]["v"]
    if isinstance(expected, float):
        assert result == expected
    elif expected == text:
        assert result == text
    else:
        assert isinstance(result, si.Physical)
        assert str(result) == expected


def test_parse_tree_glued_unit_text_still_parses_with_parse():
    assert str(si.parse("350MPa")) == "350.000 MPa"


def test_parse_tree_a_candidate_that_is_not_a_quantity():
    data = {"site": {"levels": ["2 storeys"]}}
    with pytest.raises(si.UnitParseError, match=r"^site\.levels\[0\]: '2 storeys': "):
        si.parse_tree(data)
    assert si.parse_tree(data, strict=False) == data


@pytest.mark.parametrize(
    "make",
    [
        lambda: 350 * si.MPa,
        lambda: 30.2 * si.kN,
        lambda: 0.5 * si.kN,
        lambda: 4.5 * si.kN / si.m,
        lambda: 164e6 * si.mm**4,
        lambda: 1200 * si.mm,
        lambda: 0.5 * si.mm,
        lambda: 30 * si.kN * si.m,
        lambda: 3 * si.kN * si.m**2,
        lambda: 2 * si.kN / si.m**3,
        lambda: 7 * si.m / si.s**2,
        lambda: 5 * si.kg * si.m / si.s,
        lambda: 0.003 * si.kg,
        lambda: 2000 * si.kg,
        lambda: 2 * si.ft,
        lambda: 2 * si.ft**2,
        lambda: 5 * si.kipft,
        lambda: 5 * si.ksf,
        lambda: 4.5 * si.kip_ft,
        lambda: (4 * si.m).sqrt(),
        lambda: round(1.23456 * si.MPa, 5),
    ],
)
def test_display_round_trip(make):
    q = make()
    parsed = si.parse(str(q))
    assert parsed.dimensions == q.dimensions
    assert str(round(parsed, q.precision)) == str(q)
    # Equal to the displayed precision (lossy by design)
    assert math.isclose(parsed.value, q.value, rel_tol=10 ** -(q.precision - 1))
