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
JSON serialization of Physical instances.

    json.dumps(tree, default=si.json_default)
    json.loads(text, object_hook=si.json_object_hook)

or, equivalently, si.dumps(tree) / si.loads(text) (and si.dump / si.load for files).
"""

import json
from typing import Any, IO


def json_default(obj: Any) -> dict:
    """
    Returns the JSON-compatible dict for 'obj' if it is a Physical. Intended as
    the 'default' argument of json.dump(s). Raises TypeError for anything else
    so it can be chained with other encoders.
    """
    from forallpeople import Physical

    if isinstance(obj, Physical):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_object_hook(obj: dict) -> Any:
    """
    Returns a Physical if 'obj' is a serialized Physical, otherwise 'obj'
    unchanged. Intended as the 'object_hook' argument of json.load(s).
    """
    from forallpeople import Physical, SERIALIZATION_TAG

    if SERIALIZATION_TAG in obj:
        return Physical.from_dict(obj)
    return obj


def dumps(obj: Any, **kwargs) -> str:
    """
    Returns 'obj' serialized to a JSON str, encoding any Physical instances.
    Accepts the same keyword arguments as json.dumps.
    """
    kwargs.setdefault("default", json_default)
    return json.dumps(obj, **kwargs)


def dump(obj: Any, fp: IO[str], **kwargs) -> None:
    """
    Writes 'obj' as JSON to the file-like 'fp', encoding any Physical instances.
    Accepts the same keyword arguments as json.dump.
    """
    kwargs.setdefault("default", json_default)
    json.dump(obj, fp, **kwargs)


def loads(s: str, **kwargs) -> Any:
    """
    Returns the object deserialized from the JSON str 's', decoding any
    serialized Physical instances. Accepts the same keyword arguments as json.loads.
    """
    kwargs.setdefault("object_hook", json_object_hook)
    return json.loads(s, **kwargs)


def load(fp: IO[str], **kwargs) -> Any:
    """
    Returns the object deserialized from the JSON file-like 'fp', decoding any
    serialized Physical instances. Accepts the same keyword arguments as json.load.
    """
    kwargs.setdefault("object_hook", json_object_hook)
    return json.load(fp, **kwargs)
