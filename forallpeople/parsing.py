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
Parsing of physical quantities from text, e.g. "350 MPa" or "4.5 kN/m".

    quantity   := number [ws] [unit_expr]
    number     := Python float literal (sign, decimal, exponent, underscores)
    unit_expr  := term (op term)*            op := "*" | "·" | "/"  (left-associative)
    term       := atom [exponent]
    atom       := unit_name | "(" unit_expr ")"
    exponent   := ("**" | "^") signed_number | superscript_number   (e.g. ⁴, ⁻², ⁰'⁵)
    unit_name  := [SI prefix] (environment key | environment Symbol | SI base unit)

The unit expression is evaluated on Physical instances with a small precedence
parser: there is no eval().
"""

import difflib
import math
import re
from typing import Any, Optional, Union

from forallpeople.dimensions import Dimensions, DimensionError
import forallpeople.physical_helper_functions as phf


class UnitParseError(ValueError):
    """
    Raised when a str cannot be parsed into a physical quantity.
    """


_NUMBER = re.compile(
    r"[+-]?(?:\d(?:_?\d)*(?:\.(?:\d(?:_?\d)*)?)?|\.\d(?:_?\d)*)(?:[eE][+-]?\d(?:_?\d)*)?"
)

# A str that parse_tree() parses: a number, alone or followed by whitespace and
# unit text. Strs with something glued to the number ("2026-014", "38x140",
# "350MPa") are left alone.
_QUANTITY_CANDIDATE = re.compile(rf"\s*{_NUMBER.pattern}(?:\s*$|\s+\S)")

_SUPERSCRIPT_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_FROM_SUPERSCRIPT = str.maketrans(
    {sup: char for char, sup in phf._superscripts.items()}
)

_TOKEN = re.compile(
    rf"""
    (?P<ws>\s+)
    | (?P<exp>(?:\*\*|\^)\s*(?P<exp_paren>\()?\s*(?P<exp_val>[+-]?\d+(?:\.\d+)?)
        \s*(?(exp_paren)\)))
    | (?P<sup>⁻?[{_SUPERSCRIPT_DIGITS}]+(?:'[{_SUPERSCRIPT_DIGITS}]+)?)
    | (?P<op>[*·⋅/])
    | (?P<lparen>\()
    | (?P<rparen>\))
    | (?P<name>(?:(?![{_SUPERSCRIPT_DIGITS}])[^\W\d]|°)(?:(?![{_SUPERSCRIPT_DIGITS}])\w|°)*)
    """,
    re.VERBOSE,
)

_PREFIXES = {
    prefix: value for prefix, value in phf._prefixes.items() if prefix
} | phf._additional_prefixes
_PREFIXES.update({"u": _PREFIXES["μ"], "\u00b5": _PREFIXES["μ"]})  # "u" and micro sign
_CANONICAL_PREFIXES = {"u": "μ", "\u00b5": "μ"}

_SPACE_HINT = (
    "Units separated only by a space are ambiguous: use '·' or '*' to multiply "
    "them (e.g. 'kN·m' or 'kN*m')."
)


def parse(text: str, environment, expect=None) -> Union[float, Any]:
    """
    Returns a Physical (or a float, if dimensionless) parsed from 'text' using the
    units known to 'environment'. If 'expect' is given (a unit str such as "MPa" or
    a Physical), raises DimensionError if the result has different dimensions.
    """
    if not isinstance(text, str):
        raise UnitParseError(f"Expected a str to parse, not {type(text).__name__}.")
    stripped = text.strip()
    match = _NUMBER.match(stripped)
    if not match:
        raise UnitParseError(f"{text!r} does not start with a number.")
    value = float(match.group())
    unit_text = stripped[match.end() :].strip()
    if not unit_text:
        result = value
    else:
        result = value * _evaluate_unit_expr(unit_text, environment)
        # A single prefixed SI unit (e.g. "kPa", "mm") keeps displaying with the
        # prefix it was written with.
        _, prefix = _resolve_name(unit_text, environment)
        if prefix:
            result = result.prefix(prefix)

    if expect is not None:
        _check_expected(result, unit_text, expect, environment)
    return result


def parse_tree(obj: Any, environment, strict: bool = True, _path: str = "") -> Any:
    """
    Returns a copy of 'obj' (nested dicts, lists and tuples) with every quantity
    str parsed into a Physical (or float). A quantity str is a number, alone or
    followed by whitespace and unit text (e.g. "12", "350 MPa"); a str with
    anything else attached to the number (e.g. "2026-10-29", "38x140", "350MPa")
    is left as a str. Keys are never parsed, and other values are returned
    unchanged. If a quantity str cannot be parsed (e.g. "2 storeys"), raises
    UnitParseError naming its path when 'strict' is True, otherwise leaves it as
    a str.
    """
    if isinstance(obj, dict):
        return {
            key: parse_tree(
                value, environment, strict, f"{_path}.{key}" if _path else str(key)
            )
            for key, value in obj.items()
        }
    if isinstance(obj, (list, tuple)):
        items = [
            parse_tree(value, environment, strict, f"{_path}[{idx}]")
            for idx, value in enumerate(obj)
        ]
        return items if isinstance(obj, list) else type(obj)(items)
    if isinstance(obj, str) and _QUANTITY_CANDIDATE.match(obj):
        try:
            return parse(obj, environment)
        except UnitParseError as err:
            if not strict:
                return obj
            location = f"{_path}: " if _path else ""
            raise UnitParseError(f"{location}{obj!r}: {err}") from None
    return obj


def _check_expected(result, unit_text: str, expect, environment) -> None:
    """
    Raises DimensionError if 'result' does not have the dimensions of 'expect'.
    """
    if isinstance(expect, str):
        expect_text = expect.strip()
        if _NUMBER.match(expect_text):
            expected = parse(expect_text, environment)
        else:
            expected = _evaluate_unit_expr(expect_text, environment)
    else:
        expected = expect
        expect_text = str(expect)
    expected_dims = _dims_of(expected)
    result_dims = _dims_of(result)
    if result_dims != expected_dims:
        got = unit_text or "a dimensionless number"
        raise DimensionError(
            f"Expected the dimensions of {expect_text} {tuple(expected_dims)}, "
            f"got {got} {tuple(result_dims)}."
        )


def _dims_of(quantity) -> Dimensions:
    return getattr(quantity, "dimensions", Dimensions(0, 0, 0, 0, 0, 0, 0))


def _evaluate_unit_expr(unit_text: str, environment):
    """
    Returns the Physical (or float) described by the unit expression 'unit_text'.
    """
    # A whole-expression match comes first so that defined units with factors
    # (e.g. "kip·ft", "N/m") keep displaying as authored.
    whole = _lookup_name(unit_text, environment)
    if whole is not None:
        return whole
    return _UnitExprParser(unit_text, environment).parse()


def _lookup_name(name: str, environment):
    """
    Returns the unit for 'name', or None if not found. 'name' is an environment
    key, an environment Symbol, or the display name of an SI unit with an SI
    prefix (e.g. "kN·m", "μm", "mg"; the display name is the Symbol, if the unit
    has one, otherwise the key).
    """
    return _resolve_name(name, environment)[0]


def _resolve_name(name: str, environment) -> tuple:
    """
    Returns (unit, prefix) for 'name', as found by _lookup_name(). 'prefix' is
    the SI prefix (e.g. "k", "μ") when 'name' is an SI unit with an SI prefix,
    otherwise "". 'unit' is None if 'name' is not found.
    """
    units = environment._units_dict
    if name in units:
        return units[name], _implied_prefix(name, units[name], environment)
    alias = environment._symbol_aliases.get(name)
    if alias is not None:
        return units[alias], _implied_prefix(name, units[alias], environment)
    if name == "g":
        return _gram(environment), ""
    for prefix, base in _split_prefix(name):
        unit = _lookup_display_name(base, environment)
        if unit is not None and _is_prefixable(unit):
            return _PREFIXES[prefix] * unit, _CANONICAL_PREFIXES.get(prefix, prefix)
    return None, ""


def _implied_prefix(name: str, unit, environment) -> str:
    """
    Returns the SI prefix that 'name', a unit defined in 'environment', is
    written with, or "" if it is not exactly an SI prefix on a prefixable unit.
    e.g. "kPa" defined with a Value of 1000 returns "k"; "kip", "ft" and the SI
    base unit "kg" return "".
    """
    if name in environment._si_base_units or unit.factor != 1:
        return ""
    for prefix, base in _split_prefix(name):
        base_unit = _lookup_display_name(base, environment)
        if (
            base_unit is not None
            and _is_prefixable(base_unit)
            and unit.dimensions == base_unit.dimensions
            and math.isclose(unit.value, _PREFIXES[prefix] * base_unit.value)
        ):
            return _CANONICAL_PREFIXES.get(prefix, prefix)
    return ""


def _split_prefix(name: str) -> list:
    """
    Returns the (prefix, remainder) pairs for each SI prefix that 'name' starts with.
    """
    return [
        (prefix, name[len(prefix) :])
        for prefix in sorted(_PREFIXES, key=len, reverse=True)
        if name.startswith(prefix) and len(name) > len(prefix)
    ]


def _lookup_display_name(name: str, environment):
    if name == "g":
        return _gram(environment)
    key = environment._display_names.get(name)
    if key is not None:
        return environment._units_dict[key]
    return None


def _gram(environment):
    return environment._units_dict["kg"] / 1000


def _is_prefixable(unit) -> bool:
    """
    Returns True if 'unit' is a coherent SI unit (or the gram) that may take an
    SI prefix: e.g. "N", "N·m" or "g" but not "kN", "mm" or "ft".
    """
    if unit.factor != 1:
        return False
    kg_only = unit.dimensions == Dimensions(1, 0, 0, 0, 0, 0, 0)
    return unit.value == (0.001 if kg_only else 1)


class _UnitExprParser:
    """
    A precedence parser that evaluates a unit expression on Physical instances.
    """

    def __init__(self, text: str, environment):
        self.text = text
        self.environment = environment
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _error(self, message: str) -> UnitParseError:
        return UnitParseError(f"Cannot parse units {self.text!r}: {message}")

    def _tokenize(self, text: str) -> list:
        tokens = []
        pos = 0
        preceded_by_space = False
        while pos < len(text):
            match = _TOKEN.match(text, pos)
            if not match:
                raise self._error(f"unexpected character {text[pos]!r}.")
            kind = match.lastgroup
            if kind == "exp_paren" or kind == "exp_val":
                kind = "exp"
            if kind == "ws":
                preceded_by_space = True
            else:
                if kind == "exp":
                    token_value = float(match.group("exp_val"))
                elif kind == "sup":
                    token_value = float(match.group().translate(_FROM_SUPERSCRIPT))
                else:
                    token_value = match.group()
                tokens.append((kind, token_value, preceded_by_space))
                preceded_by_space = False
            pos = match.end()
        return tokens

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return (None, None, False)

    def _next(self):
        token = self._peek()
        self.pos += 1
        return token

    def parse(self):
        result = self._expr()
        kind, value, _ = self._peek()
        if kind is not None:
            raise self._error(f"unexpected {value!r}.")
        return result

    def _expr(self):
        result = self._term()
        while True:
            kind, value, spaced = self._peek()
            if kind == "op":
                self._next()
                rhs = self._term()
                result = result / rhs if value == "/" else result * rhs
            elif kind in ("name", "lparen"):
                if spaced:
                    raise self._error(_SPACE_HINT)
                raise self._error(f"missing an operator before {value!r}.")
            else:
                return result

    def _term(self):
        result = self._atom()
        kind, value, _ = self._peek()
        if kind in ("exp", "sup"):
            self._next()
            power = int(value) if value.is_integer() else value
            result = result**power
        return result

    def _atom(self):
        kind, value, _ = self._next()
        if kind == "name":
            unit = _lookup_name(value, self.environment)
            if unit is None:
                raise UnitParseError(_unknown_unit_message(value, self.environment))
            return unit
        if kind == "lparen":
            result = self._expr()
            closing, _, _ = self._next()
            if closing != "rparen":
                raise self._error("missing a closing ')'.")
            return result
        if kind is None:
            raise self._error("expected a unit at the end.")
        raise self._error(f"expected a unit, got {value!r}.")


def _unknown_unit_message(name: str, environment) -> str:
    env_name = environment._env_name
    if env_name is None:
        message = (
            f"{name!r} is not a unit: no environment has been loaded, so only the SI "
            "base units (kg, m, s, A, cd, K, mol) are known until "
            "si.environment(...) is called."
        )
    else:
        message = f"{name!r} is not a unit in environment {env_name!r}."
    display_names = environment._display_names
    aliases = environment._symbol_aliases
    suggestions = []
    for prefix, base in _split_prefix(name):
        for match in difflib.get_close_matches(base, display_names, n=1):
            key = display_names[match]
            if _is_prefixable(environment._units_dict[key]):
                suggestion = f"{prefix + match!r}"
                if key != match:
                    suggestion += f" ({key})"
                suggestions.append(suggestion)
    candidates = list(environment._units_dict) + list(aliases)
    for match in difflib.get_close_matches(name, candidates, n=3):
        if match in aliases:
            suggestions.append(f"{match!r} ({aliases[match]})")
        else:
            suggestions.append(repr(match))
    suggestions = list(dict.fromkeys(suggestions))[:3]
    if suggestions:
        message += f" Did you mean {' or '.join(suggestions)}?"
    return message
