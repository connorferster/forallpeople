"""
Tests for environment loading: Python 3.14 SyntaxWarning guard, error messages
from Environment._load_environment, and loading environments from a file path.
"""

import json
import pathlib
import warnings

import pytest

import forallpeople as si
from forallpeople.dimensions import DimensionError

PACKAGE_DIR = pathlib.Path(si.__file__).parent


@pytest.mark.parametrize(
    "py_file",
    sorted(PACKAGE_DIR.rglob("*.py")),
    ids=lambda p: str(p.relative_to(PACKAGE_DIR)),
)
def test_no_syntax_warnings(py_file):
    # Compile from source: `import forallpeople` can be served from cached .pyc
    # files, which would hide invalid escape sequences.
    source = py_file.read_text(encoding="utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        compile(source, str(py_file), "exec")


def test_unknown_environment_name_message():
    with pytest.raises(ValueError, match="The environment name, not_an_env, does"):
        si.environment._load_environment("not_an_env")


def test_missing_environment_file_message(tmp_path):
    missing = tmp_path / "missing.json"
    with pytest.raises(ValueError, match="does not exist"):
        si.environment._load_environment(str(missing))


def test_missing_dimension_message(tmp_path):
    env_file = tmp_path / "bad_dims.json"
    env_file.write_text(json.dumps({"widget": {"Factor": "2"}}))
    with pytest.raises(DimensionError, match="'bad_dims.json', for unit 'widget'"):
        si.environment._load_environment(env_file)


def test_bad_factor_message(tmp_path):
    env_file = tmp_path / "bad_factor.json"
    env_file.write_text(
        json.dumps({"widget": {"Dimension": [0, 1, 0, 0, 0, 0, 0], "Factor": "abc"}})
    )
    with pytest.raises(ValueError, match="'widget' in 'bad_factor.json'.*not 'abc'"):
        si.environment._load_environment(env_file)


def test_load_environment_from_path(tmp_path):
    env_file = tmp_path / "project_units.json"
    env_file.write_text(
        json.dumps(
            {
                "furlong": {
                    "Dimension": [0, 1, 0, 0, 0, 0, 0],
                    "Factor": "1/201.168",
                    "Symbol": "furlong",
                }
            }
        ),
        encoding="utf-8",
    )
    try:
        for env_name in (env_file, str(env_file)):
            si.environment(env_name)
            assert str(2 * si.furlong) == "2.000 furlong"
            assert (2 * si.furlong).value == pytest.approx(402.336)
    finally:
        si.environment("test_definitions", top_level=True)


# The exact definitions of the units with factors, in SI base units:
# 1 lb = 0.45359237 kg, g = 9.80665 m/s², 1 ft = 0.3048 m, 1 in = 0.0254 m.
LB, G, FT, INCH = 0.45359237, 9.80665, 0.3048, 0.0254
LBF = LB * G
UNIT_SIZES = {
    # Length, area, volume
    "mile": 1760 * 0.9144,
    "yard": 0.9144,
    "ft": FT,
    "inch": INCH,
    "acre": 43560 * FT**2,
    "fl_ounce": 29.5735295625e-6,
    "quart": 0.946352946e-3,
    # Force and mass
    "lbf": LBF,
    "lb": LBF,
    "kip": 1000 * LBF,
    "ton": 2000 * LBF,
    "lbm": LB,
    "ounce": 0.028349523125,
    # Moment
    "lbft": LBF * FT,
    "kipft": 1000 * LBF * FT,
    "lbin": LBF * INCH,
    "kipin": 1000 * LBF * INCH,
    "lbft2": LBF * FT**2,
    "kft2": 1000 * LBF * FT**2,
    # Line load, pressure, weight density
    "lb_ft": LBF / FT,
    "kip_ft": 1000 * LBF / FT,
    "psf": LBF / FT**2,
    "ksf": 1000 * LBF / FT**2,
    "psi": LBF / INCH**2,
    "ksi": 1000 * LBF / INCH**2,
    "bar": 100_000,
    "pcf": LBF / FT**3,
    "kcf": 1000 * LBF / FT**3,
    "pci": LBF / INCH**3,
    "kci": 1000 * LBF / INCH**3,
    # Time, mass flow, molar mass, temperature difference
    "minute": 60,
    "hour": 3600,
    "day": 86400,
    "kg_h": 1 / 3600,
    "g_mol": 0.001,
    "kg_kmol": 0.001,
    "F": 5 / 9,
}
BUNDLED = ["default", "structural", "us_customary", "electrical", "thermal"]
FACTORED_UNITS = [
    (env_name, unit)
    for env_name in BUNDLED
    for unit, definition in json.loads(
        (PACKAGE_DIR / "environments" / f"{env_name}.json").read_text("utf-8")
    ).items()
    if "Factor" in definition
]


@pytest.mark.parametrize("env_name, unit", FACTORED_UNITS)
def test_unit_factors(env_name, unit):
    # Build the units without loading the environment: other tests rely on the
    # environment that their module loaded.
    definitions = si.environment._load_environment(env_name)
    units = si.environment._generate_units_dict(definitions, si.Physical)
    assert unit in UNIT_SIZES, f"Add the exact size of {unit!r} to UNIT_SIZES."
    assert units[unit].value == pytest.approx(UNIT_SIZES[unit], rel=1e-12)
