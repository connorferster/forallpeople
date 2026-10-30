"""
Tests for the YMPrint plugin: Physical values exported and read back through a
YMPrint project, and the "yaml+units" data loader. Skipped without ymprint.
"""

import json
import math
import pathlib
import subprocess
import sys
import textwrap
import warnings
from importlib.metadata import entry_points

import pytest

ymprint = pytest.importorskip("ymprint")

import forallpeople as si
from forallpeople import ymprint_plugin
from ymprint import Ymprint
from ymprint.data_sources import DataSourceError, load_file
from ymprint.exports import dumps
from ymprint.project import Project


@pytest.fixture(autouse=True, scope="module")
def structural_environment():
    # Other test modules load "test_definitions" at the top level at import
    # time, so load "structural" only while this module runs, then restore it.
    si.environment("structural")
    ymprint_plugin.setup()
    yield
    si.environment("test_definitions", top_level=True)


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text), encoding="utf-8")
    return path


def slots(q):
    return (q.value, q.dimensions, q.factor, q.precision, q.prefixed)


def test_the_plugin_is_registered_for_ymprint():
    plugins = [e.value for e in entry_points(group="ymprint.plugins")]
    assert "forallpeople.ymprint_plugin:setup" in plugins


# Built when the test runs: the units exist only once the environment is loaded.
QUANTITIES = {
    "kN": lambda: 30.2 * si.kN,
    "small kN": lambda: 0.5 * si.kN,
    "MPa": lambda: 250 * si.MPa,
    "kN·m": lambda: 12 * si.kN * si.m,
    "ft": lambda: (6 * si.m).to("ft"),
    "sqrt": lambda: (4 * si.m**2).sqrt(),
    "precision": lambda: round(30.21234 * si.kN, 5),
}


@pytest.mark.parametrize("name", list(QUANTITIES))
def test_quantities_round_trip_exactly(tmp_path, name):
    quantity = QUANTITIES[name]()
    path = tmp_path / "out.json"
    path.write_text(dumps({"q": quantity}), encoding="utf-8")
    loaded = load_file(path)["q"]
    assert isinstance(loaded, si.Physical)
    assert slots(loaded) == slots(quantity)
    assert str(loaded) == str(quantity)


def test_the_json_is_tagged_and_readable(tmp_path):
    data = json.loads(dumps({"Vr": 30.2 * si.kN}))["Vr"]
    assert data["$type"] == ymprint_plugin.TYPE_TAG
    assert data["value"] == 30200.0
    assert data["display"] == "30.200 kN"
    # forallpeople's own JSON hook reads it too.
    assert slots(si.loads(json.dumps(data))) == slots(30.2 * si.kN)


# --- decoding in the recorded environment -----------------------------------------


def decode_in_fresh_process(data: dict) -> subprocess.CompletedProcess:
    """
    Decodes 'data' with the plugin in a new process, where no environment has
    been loaded, and prints the result, the active environment and any warnings.
    """
    script = textwrap.dedent(f"""
        import json, warnings
        warnings.simplefilter("always")
        import forallpeople as si
        from forallpeople import ymprint_plugin
        data = json.loads({json.dumps(json.dumps(data))})
        q = ymprint_plugin.decode(data)
        ymprint_plugin.decode(data)
        print(q)
        print(si.environment._env_name)
        """)
    return subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )


def test_decode_loads_the_recorded_environment_when_none_is_active():
    data = serialized(12 * si.kN * si.m)
    assert data["environment"] == "structural"
    run = decode_in_fresh_process(data)
    assert run.stdout.splitlines() == ["12.000 kN·m", "structural"]
    assert run.stderr == ""


def test_decode_does_not_load_a_custom_environment():
    data = {**serialized(12 * si.kN * si.m), "environment": "house_units"}
    run = decode_in_fresh_process(data)
    assert run.stdout.splitlines() == ["12000.000 kg·m²·s⁻²", "None"]
    assert run.stderr.count("'house_units', which is not bundled") == 1


def test_decode_never_switches_the_active_environment(monkeypatch):
    monkeypatch.setattr(ymprint_plugin, "_warned", set())
    expected = 12 * si.kN * si.m
    data = serialized(expected)
    try:
        si.environment("default")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            first = ymprint_plugin.decode(data)
            ymprint_plugin.decode(data)
        assert si.environment._env_name == "default"
        assert slots(first) == slots(expected)
        messages = [str(w.message) for w in caught]
        assert len(messages) == 1
        assert "written in the units environment 'structural'" in messages[0]
        assert "display in the active environment 'default'" in messages[0]
    finally:
        si.environment("structural")


def test_decode_in_the_same_environment_is_silent():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert ymprint_plugin.decode(serialized(30.2 * si.kN)) == 30.2 * si.kN


def serialized(quantity) -> dict:
    return json.loads(dumps({"q": quantity}))["q"]


# --- yaml+units ------------------------------------------------------------------


def test_yaml_with_units(tmp_path):
    path = write(
        tmp_path / "geometry.yml",
        """
        _environment: structural
        B01: {span: 6 m, w_DL: 2.5 kN/m, f_y: 350 MPa, M: -4 kN·m, P: 1.2e3 N}
        B02: {span: 10 ft, label: B02, n: 3, ratio: "0.9"}
        """,
    )
    data = load_file(path, "yaml+units")
    assert "_environment" not in data
    b01, b02 = data["B01"], data["B02"]
    assert slots(b01["span"]) == slots(6 * si.m)
    assert math.isclose(b01["w_DL"].value, 2500)
    assert str(b01["f_y"]) == "350.000 MPa"
    assert math.isclose(b01["M"].value, -4000)
    assert math.isclose(b01["P"].value, 1200)
    assert math.isclose(b02["span"].value, 3.048)
    assert (b02["label"], b02["n"], b02["ratio"]) == ("B02", 3, 0.9)


def test_yaml_with_units_leaves_strs_that_only_start_with_a_number(tmp_path):
    path = write(
        tmp_path / "project.yml",
        """
        _environment: structural
        number: "000.000.000"
        date: 2026-014
        span: 6 m
        """,
    )
    data = load_file(path, "yaml+units")
    assert data["number"] == "000.000.000"
    assert data["date"] == "2026-014"
    assert slots(data["span"]) == slots(6 * si.m)


def test_yaml_with_units_requires_an_environment(tmp_path):
    path = write(tmp_path / "geometry.yml", "B01: {span: 6 m}\n")
    with pytest.raises(
        DataSourceError,
        match="_environment: structural.*Available environments: .*us_customary",
    ):
        load_file(path, "yaml+units")


def test_an_unknown_environment_is_an_error(tmp_path):
    path = write(tmp_path / "geometry.yml", "_environment: martian\nB01: {span: 6 m}\n")
    with pytest.raises(DataSourceError, match="unknown units environment 'martian'"):
        load_file(path, "yaml+units")


def test_an_unknown_unit_names_where_it_is(tmp_path):
    path = write(
        tmp_path / "geometry.yml", "_environment: structural\nB01: {span: 6 furlongs}\n"
    )
    with pytest.raises(DataSourceError, match=r"geometry.yml: B01.span: '6 furlongs'"):
        load_file(path, "yaml+units")


def test_an_environment_file_next_to_the_data(tmp_path):
    bundled = pathlib.Path(si.__file__).parent / "environments" / "structural.json"
    (tmp_path / "house_units.json").write_text(
        bundled.read_text(encoding="utf-8"), encoding="utf-8"
    )
    path = write(
        tmp_path / "geometry.yml", "_environment: house_units.json\nB01: {span: 6 m}\n"
    )
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            data = load_file(path, "yaml+units")
        assert slots(data["B01"]["span"]) == slots(6 * si.m)
        assert any("replaces 'structural'" in str(w.message) for w in caught)
    finally:
        si.environment("structural")


# --- end to end ------------------------------------------------------------------


def test_a_quantity_flows_from_data_through_an_export_to_a_reader(tmp_path):
    write(
        tmp_path / "project.ymprint.yml",
        """
        _data:
          geometry: {path: geometry.yml, loader: yaml+units}
          capacities:
            from: calc.yml
        """,
    )
    write(
        tmp_path / "geometry.yml",
        "_environment: structural\nB01: {span: 6 m, w: 5 kN/m}\n",
    )
    calc = write(
        tmp_path / "calc.yml",
        """
        _export:
          B01:
            M_f: $M_f
        Beam B01:
          - _py:
              echo: false
              source: |
                g = geometry["B01"]
                M_f = g["w"] * g["span"]**2 / 8
          - "M_f = {{ M_f }}"
        """,
    )
    run = Ymprint().render_all(calc)
    assert not run.failures

    capacities = Project.find(tmp_path).catalog().load("capacities")
    m_f = capacities["B01"]["M_f"]
    assert isinstance(m_f, si.Physical)
    assert math.isclose(m_f.value, 22500)
    assert str(m_f) == "22.500 kN·m"
