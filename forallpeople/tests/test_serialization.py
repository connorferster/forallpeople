"""
Tests for JSON serialization of Physical instances (to_dict / from_dict and
the json_default / json_object_hook hooks).
"""

import io
import json
from fractions import Fraction

import pytest

import forallpeople as si


@pytest.fixture(autouse=True, scope="module")
def structural_environment():
    # Other test modules load "test_definitions" at the top level at import
    # time, so load "structural" only while this module runs, then restore it.
    si.environment("structural")
    yield
    si.environment("test_definitions", top_level=True)


def slots(q):
    return (q.value, q.dimensions, q.factor, q.precision, q.prefixed)


def make_quantities():
    return {
        "kN": 30.2 * si.kN,
        "ft": 2 * si.ft,
        "psf": 5 * si.psf,
        "kipft": 12 * si.kipft,
        "forced_prefix": (3 * si.kN).prefix("m"),
        "unity_prefix": (3 * si.kN).prefix("unity"),
        "precision": round(4.5 * si.kN / si.m, 2),
        "kN_m": 4.5 * si.kN / si.m,
        "mm4": 164e6 * si.mm**4,
        "sqrt": (4 * si.m).sqrt(),
    }


QUANTITY_NAMES = [
    "kN",
    "ft",
    "psf",
    "kipft",
    "forced_prefix",
    "unity_prefix",
    "precision",
    "kN_m",
    "mm4",
    "sqrt",
]


@pytest.mark.parametrize("name", QUANTITY_NAMES)
def test_round_trip_exact(name):
    q = make_quantities()[name]
    q2 = si.Physical.from_dict(q.to_dict())
    assert slots(q2) == slots(q)
    assert str(q2) == str(q)


@pytest.mark.parametrize("name", QUANTITY_NAMES)
def test_round_trip_through_json_text(name):
    q = make_quantities()[name]
    q2 = si.loads(si.dumps(q))
    assert slots(q2) == slots(q)


def test_to_dict_format():
    assert (30.2 * si.kN).to_dict() == {
        "__physical__": 1,
        "value": 30200.0,
        "dimensions": [1, 1, -2, 0, 0, 0, 0],
        "factor": 1,
        "precision": 3,
        "prefixed": "",
        "environment": "structural",
        "display": "30.200 kN",
    }
    d = (2 * si.ft).to_dict()
    assert d["factor"] == "1250/381"
    assert d["value"] == pytest.approx(0.6096)
    assert d["display"] == "2.000 ft"


def test_factor_stays_fraction():
    for q in (2 * si.ft, 5 * si.psf, 12 * si.kipft):
        q2 = si.loads(si.dumps(q))
        assert isinstance(q2.factor, Fraction)
        assert q2.factor == q.factor


def test_nested_tree_round_trip():
    tree = {
        "capacities": {"Vr": 30.2 * si.kN, "Mr": [12 * si.kipft, 4.5 * si.kN * si.m]},
        "phi": 0.9,
        "section": "W310x74",
        "count": 3,
        "flags": (True, None),
    }
    loaded = si.loads(si.dumps(tree, indent=2))
    assert loaded["phi"] == 0.9
    assert loaded["section"] == "W310x74"
    assert loaded["count"] == 3
    assert loaded["flags"] == [True, None]
    assert slots(loaded["capacities"]["Vr"]) == slots(tree["capacities"]["Vr"])
    for a, b in zip(loaded["capacities"]["Mr"], tree["capacities"]["Mr"]):
        assert slots(a) == slots(b)


def test_hooks_with_stdlib_json():
    tree = {"Vr": 30.2 * si.kN}
    text = json.dumps(tree, default=si.json_default)
    loaded = json.loads(text, object_hook=si.json_object_hook)
    assert loaded["Vr"] == tree["Vr"]


def test_dump_and_load_files():
    buf = io.StringIO()
    si.dump({"Vr": 30.2 * si.kN}, buf)
    buf.seek(0)
    assert si.load(buf)["Vr"] == 30.2 * si.kN


def test_json_default_rejects_other_types():
    with pytest.raises(TypeError, match="set is not JSON serializable"):
        si.json_default({1, 2})
    with pytest.raises(TypeError):
        si.dumps({"bad": object()})


def test_to_dict_omits_environment_when_none_is_loaded(monkeypatch):
    monkeypatch.setattr(si.environment, "_env_name", None)
    assert "environment" not in (30.2 * si.kN).to_dict()


def test_from_dict_with_and_without_environment():
    d = (30.2 * si.kN).to_dict()
    assert si.Physical.from_dict(d) == 30.2 * si.kN
    d["environment"] = "us_customary"  # informational only: never loaded
    assert si.Physical.from_dict(d) == 30.2 * si.kN
    del d["environment"]
    assert si.Physical.from_dict(d) == 30.2 * si.kN
    assert si.environment._env_name == "structural"


def test_display_ignored_on_load():
    d = (30.2 * si.kN).to_dict()
    d["display"] = "999 MPa"
    assert si.Physical.from_dict(d) == 30.2 * si.kN


def test_demand_capacity_ratio_after_load():
    caps = si.loads(si.dumps({"Vr": 30.2 * si.kN}))
    dcr = (15.1 * si.kN) / caps["Vr"]
    assert isinstance(dcr, float)
    assert dcr == pytest.approx(0.5)


@pytest.mark.parametrize(
    "change, match",
    [
        ({"__physical__": 2}, "__physical__"),
        ({"dimensions": [1, 1, -2]}, "dimensions"),
        ({"dimensions": "kN"}, "dimensions"),
        ({"dimensions": [1, 1, -2, 0, 0, 0, "x"]}, "dimensions"),
        ({"value": "30200"}, "value"),
        ({"factor": "abc"}, "factor"),
        ({"precision": 2.5}, "precision"),
        ({"prefixed": None}, "prefixed"),
    ],
)
def test_from_dict_errors(change, match):
    d = (30.2 * si.kN).to_dict()
    d.update(change)
    with pytest.raises(ValueError, match=match):
        si.Physical.from_dict(d)


def test_from_dict_missing_value():
    d = (30.2 * si.kN).to_dict()
    del d["value"]
    with pytest.raises(ValueError, match="'value': missing"):
        si.Physical.from_dict(d)


def test_from_dict_missing_tag():
    d = (30.2 * si.kN).to_dict()
    del d["__physical__"]
    with pytest.raises(ValueError, match="__physical__"):
        si.Physical.from_dict(d)


def test_load_with_different_environment():
    text = si.dumps({"L": 2 * si.ft, "P": 30.2 * si.kN})
    try:
        si.environment("default")
        loaded = si.loads(text)
        assert loaded["L"].value == pytest.approx(0.6096)
        assert loaded["L"].factor == Fraction(1250, 381)
        assert loaded["P"].value == 30200.0
    finally:
        si.environment("structural")
