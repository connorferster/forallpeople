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
"""
Physical quantities in YMPrint projects (https://github.com/StructuralPython/ymprint).

YMPrint runs setup() through its "ymprint.plugins" entry point when both packages
are installed. It registers:

- a serializer, so a Physical exported by a document (`_export`) or published by
  a script is written exactly (its .to_dict(), tagged for YMPrint), and
- a decoder, so whoever reads that data back through `_data` gets a Physical,
  displayed in the environment it was written in if none is active yet;
- the "yaml+units" data loader, for hand-written data with quantities:

      # project.ymprint.yml
      _data:
        geometry: {path: geometry.yml, loader: yaml+units}

      # geometry.yml
      _environment: structural
      B01: {span: 6 m, w_DL: 2.5 kN/m}

  Every quantity str (a number, alone or followed by whitespace and units) is
  parsed with parse_tree(); strs like "2026-014" are left alone. The file names its environment in `_environment` (an environment name, or a path
  to an environment .json relative to the file); there is no default.

YMPrint is imported only inside setup(), so forallpeople does not depend on it.
"""

import pathlib
import warnings
from typing import Any

# The tag YMPrint's decoder registry knows a serialized Physical by.
TYPE_TAG = "forallpeople.Physical"

# The key a "yaml+units" file names its environment with.
ENVIRONMENT_KEY = "_environment"


def setup() -> None:
    """Registers the serializer, decoder and "yaml+units" loader with YMPrint."""
    from forallpeople import Physical
    from ymprint.data_sources import register_loader
    from ymprint.exports import register_serializer

    try:
        from ymprint.exports import register_decoder
    except ImportError:  # YMPrint 0.8.0
        warnings.warn(
            "This version of ymprint cannot read Physical values back from exported "
            "data (they are read as dicts); upgrade to ymprint 0.8.1 or later."
        )
    else:
        register_decoder(TYPE_TAG, decode)
    register_serializer(Physical, serialize)
    register_loader("yaml+units", load_yaml_with_units, override=True)


def serialize(quantity) -> dict:
    """Returns the exact JSON form of 'quantity', tagged for YMPrint's decoder."""
    return {_type_key(): TYPE_TAG, **quantity.to_dict()}


def decode(data: dict):
    """
    Returns the Physical serialized in 'data' (YMPrint's tag is ignored). If no
    environment is active, the bundled environment named in 'data' is loaded so
    that the value displays as it was written; an active environment is never
    replaced. Unlike si.loads(), this has that side effect because in a YMPrint
    project the data comes from the project's own exports.
    """
    from forallpeople import Physical

    _use_recorded_environment(data.get("environment"))
    return Physical.from_dict(data)


# The (situation, environment name) pairs already warned about by decode().
_warned = set()


def _use_recorded_environment(name: Any) -> None:
    """
    Loads the environment 'name', recorded in a serialized Physical, if no
    environment is active and 'name' is a bundled environment. Otherwise warns
    (once per process) if the value will not display in 'name'.
    """
    from forallpeople import environment

    if not isinstance(name, str) or not name:
        return
    active = environment._env_name
    if active == name:
        return
    if active is None:
        if name in _environment_names():
            environment(name)
        else:
            _warn_once(
                ("custom", name),
                f"Physical values were written in the units environment {name!r}, "
                f"which is not bundled with forallpeople, so it was not loaded. Load "
                f"it with si.environment(...), or read a `yaml+units` file that names "
                f"it, before displaying them.",
            )
        return
    _warn_once(
        ("different", name, active),
        f"Physical values were written in the units environment {name!r} but "
        f"display in the active environment {active!r}.",
    )


def _warn_once(key: tuple, message: str) -> None:
    if key in _warned:
        return
    _warned.add(key)
    warnings.warn(message, stacklevel=3)


def load_yaml_with_units(path: pathlib.Path) -> Any:
    """
    Returns the data in the YAML file 'path', with every quantity str parsed
    into a Physical (or float) in the environment the file names in
    `_environment`.
    """
    from forallpeople.parsing import UnitParseError
    from ymprint.data_sources import DataSourceError
    from ymprint.yaml_loader import load_yaml

    path = pathlib.Path(path)
    data = load_yaml(path)
    if not isinstance(data, dict) or ENVIRONMENT_KEY not in data:
        raise DataSourceError(
            f"{path.name} is read with the `yaml+units` loader, so it must name its units "
            f"environment at the top, e.g. `{ENVIRONMENT_KEY}: structural`. "
            f"Available environments: {', '.join(_environment_names())}."
        )
    data = dict(data)
    _use_environment(data.pop(ENVIRONMENT_KEY), path)

    from forallpeople import environment

    try:
        return environment.parse_tree(data, strict=True)
    except UnitParseError as err:
        raise DataSourceError(f"{path.name}: {err}") from None


def _use_environment(name: Any, path: pathlib.Path) -> None:
    """
    Loads the environment 'name' (a bundled name, or a .json path relative to
    'path') unless it is already the active one. Loading one replaces the active
    environment for the whole process, so switching is warned about.
    """
    from forallpeople import environment
    from ymprint.data_sources import DataSourceError

    if not isinstance(name, str) or not name.strip():
        raise DataSourceError(
            f"{path.name}: `{ENVIRONMENT_KEY}` must be an environment name or a path to "
            f"an environment .json, not {name!r}."
        )
    name = name.strip()
    target = name
    if name.endswith(".json"):
        target = str((path.parent / name).resolve())
        if not pathlib.Path(target).is_file():
            raise DataSourceError(
                f"{path.name}: the environment file {target} does not exist."
            )
    elif name not in _environment_names():
        raise DataSourceError(
            f"{path.name}: unknown units environment {name!r}. "
            f"Available environments: {', '.join(_environment_names())}."
        )

    active = environment._env_name
    if active == pathlib.Path(target).stem:
        return
    if active is not None:
        warnings.warn(
            f"{path.name} uses the units environment {name!r}, which replaces "
            f"{active!r} for the rest of this process."
        )
    environment(target)


def _environment_names() -> list:
    folder = pathlib.Path(__file__).parent / "environments"
    return sorted(p.stem for p in folder.glob("*.json") if p.stem != "test_definitions")


def _type_key() -> str:
    try:
        from ymprint.exports import TYPE_KEY
    except ImportError:  # YMPrint 0.8.0
        return "$type"
    return TYPE_KEY
