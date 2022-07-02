#   Copyright 2020 Connor Ferster

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from fractions import Fraction
import math
import pytest
import forallpeople as si
import forallpeople.physical_helper_functions as phf

si.environment("test_definitions", top_level=True)


### TODO: add Ohms to definitions for testing

### Testing parameters ###
env_dims = si.environment.units_by_dimension
env_fact = si.environment.units_by_factor
units = {
    "A": 0.05 * kg,
    "B": 3.2e-3 * m,
    "C": 1000 * ft,
    "D": 1e6 * N,
    "E": 0.2 * kip,
    "F": 5 * N * 1e3 * kip,
}
parameters = [
    (value, phf._powers_of_derived(value.dimensions, env_dims))
    for value in units.values()
]

### Tests of the Physical class ###

## Testing "._repr_" methods in order of appearance in ._repr_template_() ##
def test__evaluate_dims_and_factor():
    func = phf._evaluate_dims_and_factor
    assert func(
        si.Dimensions(1, 1, -2, 0, 0, 0, 0),
        1 / Fraction("0.45359237") / Fraction("9.80665"),
        1,
        env_fact,
        env_dims,
    ) == ("lb", False)
    assert func(si.Dimensions(1, 1, -2, 0, 0, 0, 0), 1, 2, env_fact, env_dims) == (
        "N",
        True,
    )
    assert func(si.Dimensions(1, 1, -2, 0, 0, 0, 0), 1, 1, env_fact, env_dims) == (
        "N",
        True,
    )
    assert func(
        si.Dimensions(0, 1, 0, 0, 0, 0, 0),
        Fraction(1) / Fraction("0.3048"),
        1,
        env_fact,
        env_dims,
    )
    assert func(si.Dimensions(1, 0, 0, 0, 0, 0, 0), 1, 3, env_fact, env_dims) == (
        "",
        True,
    )
    assert func(si.Dimensions(1, 1, 1, 0, 0, 0, 0), 1, 1, env_fact, env_dims) == (
        "",
        False,
    )


def test__get_units_by_factor():
    ftlb = lb * ft
    ft2 = ft**2
    func = phf._get_units_by_factor
    assert func(ft.factor, ft.dimensions, env_fact, 1) == {
        "ft": {
            "Dimension": si.Dimensions(kg=0, m=1, s=0, A=0, cd=0, K=0, mol=0),
            "Symbol": "ft",
            "Factor": Fraction(1) / Fraction("0.3048"),
        }
    }
    assert func(ft2.factor, ft.dimensions, env_fact, 2) == {
        "ft": {
            "Dimension": si.Dimensions(kg=0, m=1, s=0, A=0, cd=0, K=0, mol=0),
            "Symbol": "ft",
            "Factor": Fraction(1) / Fraction("0.3048"),
        }
    }
    assert func(ftlb.factor, ftlb.dimensions, env_fact, 1) == {
        "lbft": {
            "Dimension": si.Dimensions(kg=1, m=2, s=-2, A=0, cd=0, K=0, mol=0),
            "Symbol": "lb·ft",
            "Factor": Fraction(1)
            / Fraction("0.45359237")
            / Fraction("9.80665")
            / Fraction("0.3048"),
        }
    }
    assert func((ftlb * ft).factor, (ftlb * ft).dimensions, env_fact, 1) == dict()


def test__get_unit_components_from_dims():
    func = phf._get_unit_components_from_dims
    assert func(si.Dimensions(1, 1, -2, 0, 0, 0, 0)) == [("kg", 1), ("m", 1), ("s", -2)]
    assert func(si.Dimensions(1, 2, 3, 4, 5, 6, 7)) == [
        ("kg", 1),
        ("m", 2),
        ("s", 3),
        ("A", 4),
        ("cd", 5),
        ("K", 6),
        ("mol", 7),
    ]
    assert func(si.Dimensions(0, 0, 0, 0, 0, 0, 0)) == []


# TODO: Complete these tests

# def test__format_symbol():
#     assert False


# def test__format_exponent():
#     assert False


def test_nan_pass_through():
    assert math.isnan(5 * kg * float("nan"))
    assert math.isnan(float("nan") * ft)


def test__get_unit_string():
    func = phf._get_unit_string
    assert func([("kg", 1), ("m", 1), ("s", -2)], "") == "kg·m·s⁻²"
    assert (
        func([("kg", 1), ("m", 1), ("s", -2)], "html")
        == "kg&#8901;m&#8901;s<sup>-2</sup>"
    )
    assert (
        func([("kg", 1), ("m", 1), ("s", -2)], "latex")
        == "\\mathrm{kg} \\cdot \\mathrm{m} \\cdot \\mathrm{s}^{-2}"
    )
    assert func([("m", 2)], "html") == "m<sup>2</sup>"


def test__get_superscript_string():
    func = phf._get_superscript_string
    assert func("-2") == "⁻²"
    assert func("1.39") == "¹'³⁹"
    assert func("-0.10") == "⁻⁰'¹⁰"


def test_latex():
    assert MPa.latex == "$1.000\\ \\mathrm{MPa}$"
    assert (
        2.5 * kg * m**2.5
    ).latex == "$2.500\\ \\mathrm{kg} \\cdot \\mathrm{m}^{2.5}$"


def test_repr():
    assert (
        MPa.repr
        == "Physical(value=1000000.0, dimensions="
        + "Dimensions(kg=1, m=-1, s=-2, A=0, cd=0, K=0, mol=0), "
        + "factor=1, precision=3, _prefixed=)"
    )
    assert (
        ft.repr
        == "Physical(value=0.3048, dimensions="
        + "Dimensions(kg=0, m=1, s=0, A=0, cd=0, K=0, mol=0), "
        + "factor=3.2808, precision=3, _prefixed=)"
    )


def test_html():
    assert (25 * m**2).html == "25.000 m<sup>2</sup>"
    assert (units["A"]).html == "50.000 g"


def test_prefixed():
    assert (25 * m**2).prefix("c").html == "250000.000 cm<sup>2</sup>"


def test_round():
    with pytest.raises(PendingDeprecationWarning):
        assert repr((25.2398783 * N).round(4)) == "25.2399 N"
    assert repr(round((25.2398783 * N), 4)) == "25.2399 N"


def test_split():
    assert units["C"].split()[0] == pytest.approx(1000)
    assert units["C"].split()[1] == ft


def test_sqrt():
    assert (25 * m / s).sqrt() == 5 * (m**0.5 / (s**0.5))


def test_in_units():
    # assert ft.to('m').factor == 1
    assert m.to("ft").factor == 1 / Fraction("0.3048")
    assert kip.to("lb").factor == (1000 * lb).factor
    assert ((10 * lb) ** 2).to("kip").factor == (0.1 * kip * kip).factor


def test__check_dims_parallel():
    assert phf._check_dims_parallel((3, 2, 1, 0), (6, 4, 2, 0))
    assert phf._check_dims_parallel(
        si.Dimensions(1, 2, -2, 0, 0, 0, 0), si.Dimensions(-1, -2, 2, 0, 0, 0, 0)
    )


def test__get_derived_unit():
    func = phf._get_derived_unit
    assert func(si.Dimensions(1, 1, -2, 0, 0, 0, 0), env_dims) == {
        "N": {
            "Dimension": si.Dimensions(kg=1, m=1, s=-2, A=0, cd=0, K=0, mol=0),
            "Factor": 1,
        }
    }
    assert func(si.Dimensions(1, 0, 0, 0, 0, 0, 0), env_dims) == {}
    assert func(si.Dimensions(1, 0, -2, 0, 0, 0, 0), env_dims) == {
        "N_m": {
            "Dimension": si.Dimensions(kg=1, m=0, s=-2, A=0, cd=0, K=0, mol=0),
            "Factor": 1,
            "Symbol": "N/m",
        }
    }
    assert func(si.Dimensions(1, 1, 1, 1, 1, 1, 1), env_dims) == {}


def test__dims_quotient():
    func = phf._dims_quotient
    assert func(si.Dimensions(1, 1, -2, 0, 0, 0, 0), env_dims) == si.Dimensions(
        1, 1, 1, 0, 0, 0, 0
    )
    assert func(si.Dimensions(3, 3, -6, 0, 0, 0, 0), env_dims) == si.Dimensions(
        3, 3, 3, 0, 0, 0, 0
    )
    assert func(si.Dimensions(1, 2, -2, 0, 0, 0, 0), env_dims) == si.Dimensions(
        1, 1, 1, 0, 0, 0, 0
    )


def test__dims_basis_multiple():
    func = phf._dims_basis_multiple
    assert func(si.Dimensions(0, 1, 0, 0, 0, 0, 0)) == si.Dimensions(
        0, 1, 0, 0, 0, 0, 0
    )
    assert func(si.Dimensions(0, 4, 0, 0, 0, 0, 0)) == si.Dimensions(
        0, 4, 0, 0, 0, 0, 0
    )
    assert func(si.Dimensions(0, 0, 2.5, 0, 0, 0, 0)) == si.Dimensions(
        0, 0, 2.5, 0, 0, 0, 0
    )
    assert func(si.Dimensions(0, 1, 2.5, 0, 0, 0, 0)) == None
    assert func(si.Dimensions(1, 1, -2, 0, 0, 0, 0)) == None


def test__powers_of_derived():
    func = phf._powers_of_derived
    dims = si.Dimensions
    assert func(dims(0, 1, 0, 0, 0, 0, 0), env_dims) == (1, dims(0, 1, 0, 0, 0, 0, 0))
    assert func(dims(1, 1, -2, 0, 0, 0, 0), env_dims) == (1, dims(1, 1, -2, 0, 0, 0, 0))
    assert func(dims(3, 3, -6, 0, 0, 0, 0), env_dims) == (3, dims(1, 1, -2, 0, 0, 0, 0))
    assert func(dims(1, 2, -2, 0, 0, 0, 0), env_dims) == (1, dims(1, 2, -2, 0, 0, 0, 0))
    assert func(dims(0, 4, 0, 0, 0, 0, 0), env_dims) == (4, dims(0, 1, 0, 0, 0, 0, 0))
    assert func(dims(0, 0, 2.5, 0, 0, 0, 0), env_dims) == (
        2.5,
        dims(0, 0, 1, 0, 0, 0, 0),
    )
    assert func(dims(3.6, 3.6, -7.2, 0, 0, 0, 0), env_dims) == (
        3.6,
        dims(1, 1, -2, 0, 0, 0, 0),
    )


def test__auto_prefix():
    func = phf._auto_prefix
    assert func(1500, 1) == "k"
    assert func(1500, 2) == ""
    assert func(1.5e6, 2) == "k"
    assert func(1.5e6, 1) == "M"
    assert func(1.5e-3, 1) == "m"
    assert func(1.5e-6, 2) == "m"


def test__auto_prefix_kg():
    func = phf._auto_prefix_kg
    assert func(1500, 1) == "M"
    assert func(1500, 2) == "k"
    assert func(1.5e6, 2) == "M"
    assert func(1.5e6, 1) == "G"
    assert func(1.5e-3, 1) == ""
    assert func(1.5e-6, 2) == ""
    assert func(1.5e-6, 1) == "m"


def test__auto_prefix_value():
    func = phf._auto_prefix_value
    assert func(1500, 1, "k") == 1.5
    assert func(1500, 2, "") == 1500
    assert func(52500, 1, "k") == 52.5
    assert func(1.5e6, 2, "k") == 1.5
    assert func(1.5e6, 1, "M") == 1.5
    assert func(1.5e-6, 2, "m") == 1.5
    assert func(1.5e-5, 1, "μ") == pytest.approx(15)
    assert func(1.5e-5, 2, "m") == pytest.approx(15)


def test___eq__():
    assert m == m
    assert m == 1
    assert N == 1
    assert Pa == 1
    assert kg == 1
    with pytest.raises(ValueError):
        kg == m
        N == Pa


def test___gt__():
    assert m > ft
    assert MPa > Pa
    assert (5 * m > 5 * m) == False
    assert 5 * kip > 30 * N
    with pytest.raises(ValueError):
        5 * kg > 3 * m


def test___ge__():
    assert m >= ft
    assert MPa >= Pa
    assert 5 * m >= 5 * m
    assert 5 * kN >= 5000 * N
    with pytest.raises(ValueError):
        5 * kg >= 5 * m


def test___lt__():
    assert ft < m
    assert Pa < MPa
    assert (5 * m < 5 * m) == False
    assert 5 * N < 5001 * kN
    with pytest.raises(ValueError):
        5 * kg < 5 * m


def test___le__():
    assert ft <= m
    assert Pa <= MPa
    assert 5 * m <= 5 * m
    assert 5000 * N <= 5 * kN
    with pytest.raises(ValueError):
        5 * kg <= 5 * m


def test___add__():
    assert kg + kg == si.Physical(2, si.Dimensions(1, 0, 0, 0, 0, 0, 0), 1)
    assert m + ft == si.Physical(1.3048, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1)
    assert ft + m == si.Physical(1.3048, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1 / 0.3048)
    assert N + lb == si.Physical(
        5.4482216152605005, si.Dimensions(1, 1, -2, 0, 0, 0, 0), 1
    )
    assert lb + N == si.Physical(
        5.4482216152605005, si.Dimensions(1, 1, -2, 0, 0, 0, 0), 0.22480894309971047
    )
    assert ft + 3 == si.Physical(1.2192, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1 / 0.3048)
    with pytest.raises(ValueError):
        kg + m
        N + psf


# def test___iadd__():
#     with pytest.raises(ValueError):
#         m += 3


def test___sub__():
    assert kg - kg == 0.0
    assert m - ft == si.Physical(0.6952, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1)
    assert ft - m == si.Physical(
        -0.6952, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1 / 0.3048
    )
    assert N - lb == si.Physical(
        -3.4482216152605005, si.Dimensions(1, 1, -2, 0, 0, 0, 0), 1
    )
    assert lb - N == si.Physical(
        3.4482216152605005, si.Dimensions(1, 1, -2, 0, 0, 0, 0), 0.22480894309971047
    )
    assert (ft - 3).value == pytest.approx(
        si.Physical(-0.6096, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1 / 0.3048).value
    )
    with pytest.raises(ValueError):
        kg - m
        N - psf


def test___rsub__():
    assert 2 - ft == si.Physical(0.3048, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1 / 0.3048)
    assert 10 - N == si.Physical(9, si.Dimensions(1, 1, -2, 0, 0, 0, 0), 1)


# def test___isub__():
#     with pytest.raises(ValueError):
#         m -= 3


def test___mul__():
    assert m * m == si.Physical(1, si.Dimensions(0, 2, 0, 0, 0, 0, 0), 1)
    assert m * kg == si.Physical(1, si.Dimensions(1, 1, 0, 0, 0, 0, 0), 1)
    assert ft * m == si.Physical(0.3048, si.Dimensions(0, 2, 0, 0, 0, 0, 0), 1 / 0.3048)
    assert N * m == si.Physical(1, si.Dimensions(1, 2, -2, 0, 0, 0, 0), 1)
    assert psf * m * m == si.Physical(
        47.88025898033584, si.Dimensions(1, 1, -2, 0, 0, 0, 0), 0.02088543423315013
    )
    assert 2 * ft == si.Physical(0.6096, si.Dimensions(0, 1, 0, 0, 0, 0, 0), 1 / 0.3048)
    assert (
        si.Physical(10, si.Dimensions(-1, -1, 0, 0, 0, 0, 0), 1)
        * si.Physical(2, si.Dimensions(1, 1, 0, 0, 0, 0, 0), 1)
    ) == 20
    assert (10 * ksf) * (5 * ft) * (2 * ft) == 100 * kip  # TODO: Fix this gotcha
    assert m * ft == si.Physical(0.3048, si.Dimensions(0, 2, 0, 0, 0, 0, 0), 1.0)


# def test___imul__():
#     with pytest.raises(ValueError):
#         m *= 3


def test___truediv__():
    assert m / m == 1
    assert m / s == si.Physical(1, si.Dimensions(0, 1, -1, 0, 0, 0, 0), 1)
    assert kN / m / m == kPa
    assert (5 * kN) / 2 == 2.5 * kN
    assert (kip / (2 * ft * 5 * ft)).value == pytest.approx((0.100 * ksf).value)


def test___rtruediv__():
    assert 2 / m == si.Physical(2, si.Dimensions(0, -1, 0, 0, 0, 0, 0), 1)
    assert 10 / N == si.Physical(10, si.Dimensions(-1, -1, 2, 0, 0, 0, 0), 1)
    assert 1 / kip == si.Physical(
        value=0.00022480894309971045,
        dimensions=si.Dimensions(kg=-1, m=-1, s=2, A=0, cd=0, K=0, mol=0),
        factor=4448.221615260501,
        precision=3,
    )


def test___pow__():
    assert N**2 == si.Physical(1, si.Dimensions(2, 2, -4, 0, 0, 0, 0), 1)
    assert ft**3 == si.Physical(
        0.3048**3, si.Dimensions(0, 3, 0, 0, 0, 0, 0), (1 / 0.3048) ** 3
    )


def test___abs__():
    assert abs(-1 * m) == m
    assert abs(-10 * ft**2) == 10 * ft**2
    assert abs(1 * kip) == 1 * kip


def test___float__():
    assert float(6.7 * ft) == pytest.approx(6.7)
    assert float((52.5 * kN)) == pytest.approx(52.5)
    assert float(34 * kg * A * m) == pytest.approx(34)


def test__format__():
    value = 432.92393
    assert "{:.3f}".format(value * MPa) == "432.924 MPa"
    assert "{:.2e}".format(value * MPa) == "4.33e+02 MPa"
    assert "{:.2eH}".format(value * MPa) == "4.33 &times; 10<sup>2</sup> MPa"
    assert "{:.2eL}".format(value * MPa) == "$4.33 \\times 10^ {2}\\ \\mathrm{MPa}$"


## Test of Environment Class ##

# def test_load_environment():
#    assert "stub" == False
#
# def test_instantiator():
#    assert "stub" == False


## Tests of supplementary math functions ##


def test_sqrt():
    assert (9 * kPa).sqrt() == 3 * kPa**0.5
    assert (9 * MPa).sqrt() == 3 * MPa**0.5


## Integration tests
def test_defined_unit_persistence():
    a = units["E"]
    x = units["D"]
    b = 1 / a**2

    area = 2.3 * ft * 1.2 * ft
    c = a / area

    d = a.to("lb")
    e = 2.8 * lb
    f = 1 / d**2 * e * 10
    g = 1 / f + x / 1e3

    assert repr(b) == "25.000 kip⁻²"
    assert (
        b.repr
        == "Physical(value=1.2634765224402213e-06, dimensions=Dimensions(kg=-2, m=-2, s=4, A=0, cd=0, K=0, mol=0), factor=1.9787e+07, precision=3, _prefixed=)"
    )
    assert repr(c) == "0.072 ksf"
    assert repr(g) == "1653.380 lb"
