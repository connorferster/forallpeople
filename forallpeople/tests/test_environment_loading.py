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
