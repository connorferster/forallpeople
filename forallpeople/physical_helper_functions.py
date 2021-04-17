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

from __future__ import annotations
from collections import ChainMap
import functools
from typing import Any, Union, Optional
from forallpeople.dimensions import Dimensions
import forallpeople.tuplevector as vec

### Helper methods for repr methods ###

_prefixes = { # Do not add custom prefixes between Y and y, e.g. "c": 1e-2
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "T": 1e12,
    "G": 1e09,
    "M": 1e06,
    "k": 1e03,
    "": 1.0,
    "m": 1e-3,
    "μ": 1e-6,
    "n": 1e-09,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
    "z": 1e-21,
    "y": 1e-24,
}

_additional_prefixes = {
    "c": 1e-2,
}

_superscripts = {
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
    "0": "⁰",
    "-": "⁻",
    ".": "'",
}
_eps = 1e-7
_total_precision = 6


def _evaluate_dims_and_factor(
    dims_orig: Dimensions,
    factor: Union[int, float],
    power: Union[int, float],
    env_fact: dict,
    env_dims: dict,
) -> tuple:
    """Part of the __str__ and __repr__ process.
    Returns a tuple containing the
    appropriate symbol as a string (if applicable; '' if not) and a
    boolean indicating whether or not the dimension and factor combination
    is elligible for a prefix."""
    defined = _get_units_by_factor(
        factor=factor, dims=dims_orig, units_env=env_fact, power=power
    )

    # Derived units not retrieving inverted definitions
    derived = _get_derived_unit(dims=dims_orig, units_env=env_dims)
    single_dim = _dims_basis_multiple(dims_orig)
    if defined:
        units_match = defined
        prefix_bool = False
    elif derived or single_dim:
        units_match = derived
        prefix_bool = True
    else:
        units_match = derived
        prefix_bool = False

    if units_match:
        name = tuple(units_match.keys())[0]
        symbol = units_match.get(name, {}).get("Symbol", "")
        symbol = symbol or name
    else:
        symbol = ""
    return (symbol, prefix_bool)


#@functools.lru_cache(maxsize=None) #Not possible to use LRU cache here?
def _get_units_by_factor(
    factor: float, dims: Dimensions, units_env: dict, power: Union[int, float]
) -> dict:
    """
    Returns a units_dict from the environment instance if the numerical
    value of 'factor' is a match for a derived unit defined in the
    environment instance and the dimensions stored in the units_dict are
    equal to 'dims'. Returns an empty dict, otherwise.
    """
    new_factor = factor ** (1 / power)
    units_match = units_env.get(round(new_factor, _total_precision), dict())

    try:
        units_name = tuple(units_match.keys())[0]
    except IndexError:
        units_name = ""
    retrieved_dims = units_match.get(units_name, dict()).get("Dimension", dict())
    if dims != retrieved_dims:
        return dict()
    return units_match


def _get_derived_unit(dims: Dimensions, units_env: dict) -> dict:
    """
    Returns a units definition dict that matches 'dimensions'.
    If 'dimensions' is a derived unit raised to a power (e.g. N**2),
    then its original dimensions are checked instead of the altered ones.
    Returns {} if no unit definition matches 'dimensions'.
    """
    derived_units = units_env.get("derived")
    return derived_units.get(dims, dict())


def _get_unit_string(unit_components: list, repr_format: str) -> str:
    """
    Part of the __str__ and __repr__ process. Returns a string representing
    the SI unit components of the Physical instance extracted from the list of
    tuples, 'unit_components', using 'repr_format' as given by the _repr_x_
    function it was called by. If 'repr_format' is not given, then terminal
    output is assumed.
    """
    dot_operator = "·"  # new: · , # old: ⋅
    pre_super = ""
    post_super = ""
    pre_symbol = ""
    post_symbol = ""
    if repr_format == "html":
        dot_operator = "&#8901;"  # &#183;
        pre_super = "<sup>"
        post_super = "</sup>"
    elif repr_format == "latex":
        dot_operator = r" \cdot "
        pre_symbol = "\\text{"
        post_symbol = "}"
        pre_super = "^{"
        post_super = "}"

    str_components = []
    kg_only = ""
    for symbol, exponent in unit_components:
        if exponent:
            kg_only = symbol
        if exponent == 1:
            this_component = f"{pre_symbol}{symbol}{post_symbol}"
        else:
            if not repr_format:
                exponent = _get_superscript_string(str(exponent))
            this_component = (
                f"{pre_symbol}{symbol}{post_symbol}"
                f"{pre_super}{exponent}{post_super}"
            )
        str_components.append(this_component)
    if kg_only == "kg":  # Hack for lone special case of a kg only Physical
        return dot_operator.join(str_components).replace("kg", "g")
    return dot_operator.join(str_components)


def _get_unit_components_from_dims(dims: Dimensions):
    """
    Returns a list of tuples to represent the current units based
    on the current dimensions. Dimension ignored if 0.
    e.g. [('kg', 1), ('m', -1), ('s', -2)]
    """
    unit_components = []
    unit_symbols = dims._fields
    for idx, dim in enumerate(dims):
        if dim:  # int
            unit_tuple = (unit_symbols[idx], dim)
            unit_components.append(unit_tuple)
    return unit_components


def _format_symbol(prefix: str, symbol: str, repr_format: str = "") -> str:
    """
    Returns 'symbol' formatted appropriately for the 'repr_format' output.
    """
    # if r"\text" or "^" in symbol: # in case pre-formatted latex from unit_string
    #    return symbol
    symbol_string_open = ""
    symbol_string_close = ""
    dot_operator = "·"
    ohm = "Ω"
    if repr_format == "html":
        dot_operator = "&#8901;"
        ohm = "&#0937;"
    elif repr_format == "latex":
        dot_operator = " \\cdot "
        ohm = "\\Omega"
        symbol_string_open = "\\text{"
        symbol_string_close = "}"

    symbol = (
        symbol.replace("·", symbol_string_close + dot_operator + symbol_string_open)
        .replace("*", symbol_string_close + dot_operator + symbol_string_open)
        .replace("Ω", ohm)
    )
    formatted_symbol = f"{symbol_string_open}{prefix}{symbol}{symbol_string_close}"
    if symbol.startswith("\\text{"):  # special case for 'single dimension' Physicals...
        formatted_symbol = f"{symbol[0:6]}{prefix}{symbol[6:]}"
    return formatted_symbol


def _format_exponent(
    power: Union[int, float], repr_format: str = "", eps: float = 1e-7
) -> str:
    """
    Returns the number in 'power' as a formatted exponent for text display.
    """
    if power == 1:
        return ""

    if abs((abs(power) - round(abs(power)))) <= eps:
        power = int(round(power))
    exponent = str(power)
    if not repr_format:
        exponent = _get_superscript_string(exponent)
    return exponent


def _get_superscript_string(exponent: str) -> str:
    """Part of the __str__ and __repr__ process. Returns the unicode
    "superscript" equivalent string for a given float."""
    exponent_components = list(exponent)
    exponent_string = ""
    for component in exponent_components:
        exponent_string += _superscripts[component]
    return exponent_string


### Mathematical helper functions ###


def _powers_of_derived(dims: Dimensions, units_env: dict) -> Union[int, float]:
    """
    Returns an integer value that represents the exponent of a unit if the
    dimensions
    array is a multiple of one of the defined derived units in dimension_keys.
    Returns None,
    otherwise.
    e.g. a force would have dimensions = [1,1,-2,0,0,0,0] so a Physical object
    that had dimensions = [2,2,-4,0,0,0,0] would really be a force to the power of
    2.
    This function returns the 2, stating that `dims` is the second power of a
    derived dimension in `units_env`.
    """
    quotient_1 = _dims_quotient(dims, units_env)
    quotient_2 = _dims_basis_multiple(dims)
    quotient_1_mean = None
    if quotient_1 is not None:
        quotient_1_mean = vec.mean(quotient_1, ignore_empty=True)
        
    if quotient_1 is not None and quotient_1_mean != -1:
        power_of_derived = vec.mean(quotient_1, ignore_empty=True)
        base_dimensions = vec.divide(dims, quotient_1, ignore_zeros=True)
        return ((power_of_derived or 1), base_dimensions)
    elif quotient_1_mean == -1 and quotient_2 is not None: # Situations like Hz and s
        power_of_basis = vec.mean(quotient_2, ignore_empty=True)
        base_dimensions = vec.divide(dims, quotient_2, ignore_zeros=True)
        return ((power_of_basis or 1), base_dimensions)
    elif quotient_1_mean == -1: # Now we can proceed with an inverse  unit
        power_of_derived = vec.mean(quotient_1, ignore_empty=True)
        base_dimensions = vec.divide(dims, quotient_1, ignore_zeros=True)
        return ((power_of_derived or 1), base_dimensions)
    elif quotient_2 is not None:
        power_of_basis = vec.mean(quotient_2, ignore_empty=True)
        base_dimensions = vec.divide(dims, quotient_2, ignore_zeros=True)
        return ((power_of_basis or 1), base_dimensions)
    else:
        return (1, dims)

#@functools.lru_cache(maxsize=None) Cannot use cache with dict input
def _dims_quotient(dimensions: Dimensions, units_env: dict) -> Optional[Dimensions]:
    """
    Returns a Dimensions object representing the element-wise quotient between
    'dimensions' and a defined unit if 'dimensions' is a scalar multiple
    of a defined unit in the global environment variable.
    Returns None otherwise.
    """
    derived = units_env["derived"]
    defined = units_env["defined"]
    all_units = ChainMap(defined, derived)
    potential_inv = None # A flag to catch a -1 value (an inversion)
    quotient = None
    quotient_result = None
    for dimension_key in all_units.keys():
        if _check_dims_parallel(dimension_key, dimensions):
            quotient = vec.divide(dimensions, dimension_key, ignore_zeros=True)
            mean = vec.mean(quotient, ignore_empty=True)
            if mean == -1: 
                potential_inv = quotient
            elif -1 < mean < 1:
                return None # Ignore parallel dimensions if they are fractional dimensions
            else:
                quotient_result = quotient
    return quotient_result or potential_inv # Inversion ok, if only option



@functools.lru_cache(maxsize=None)
def _check_dims_parallel(d1: Dimensions, d2: Dimensions) -> bool:
    """
    Returns True if d1 and d2 are parallel vectors. False otherwise.
    """
    return vec.multiply(d1, vec.dot(d2, d2)) == vec.multiply(d2, vec.dot(d1, d2))


def _dims_basis_multiple(dims: Dimensions) -> Optional[Dimensions]:
    """
    Returns `dims` if `dims` is a scalar multiple of one of the basis vectors.
    Returns None, otherwise.
    This is used as a check to see if `dims` contains only a single dimension,
    even if that single dimension is to a higher power.
    e.g.
    if `dims` equals Dimensions(2, 0, 0, 0, 0, 0, 0) then `dims` will be
    returned.
    if `dims` equals Dimensions(0, 1, 1, 0, 0, 0, 0) then None will be returned.
    if `dims` equals Dimensions(0, 14, 0, 0, 0, 0, 0) then `dims` will be returned.
    """
    count = 0
    for dim in dims:
        if dim:
            count += 1
        if count > 1:
            return None
    return dims


def _auto_prefix(value: float, power: Union[int, float], kg: bool = False) -> str:
    """
    Returns a string "prefix" of an appropriate value if self.value should be prefixed
    i.e. it is a big enough number (e.g. 5342 >= 1000; returns "k" for "kilo")
    """
    kg_factor = 1
    if kg:
        kg_factor = 1000
    prefixes = _prefixes
    if abs(value) >= 1:
        for prefix, power_of_ten in prefixes.items():
            if abs(value) >= (power_of_ten / kg_factor) ** abs(power):
                return prefix
    else:
        reverse_prefixes = sorted(prefixes.items(), key=lambda prefix: prefix[0])
        # Get the smallest prefix to start...
        previous_prefix = reverse_prefixes[0][0]
        for prefix, power_of_ten in reversed(list(prefixes.items())):
            if abs(value) < (power_of_ten / kg_factor) ** abs(power):
                return previous_prefix
            else:
                previous_prefix = prefix


def _auto_prefix_kg(value: float, power: Union[int, float]) -> str:
    """
    Just like _auto_prefix but handles the one special case for "kg" because it already
    has a prefix of "k" as an SI base unit. The difference is the comparison of
    'power_of_ten'/1000 vs 'power_of_ten'.
    """
    prefixes = _prefixes
    if abs(value) >= 1:
        for prefix, power_of_ten in prefixes.items():
            if abs(value) >= (power_of_ten / 1000) ** abs(power):
                return prefix
    else:
        reverse_prefixes = sorted(prefixes.items(), key=lambda prefix: prefix[0])
        # Get the smallest prefix to start...
        previous_prefix = reverse_prefixes[0][0]
        for prefix, power_of_ten in reversed(list(prefixes.items())):
            if abs(value) < (power_of_ten / 1000) ** abs(power):
                return previous_prefix
            else:
                previous_prefix = prefix


def _auto_prefix_value(
    value: float, power: Union[int, float], prefixed: str = "", kg: bool = False,
) -> float:
    """
    Converts the value to a prefixed value if the instance has a symbol defined in
    the environment (i.e. is in the defined units dict)
    """
    if prefixed == "unity": return value
    kg_factor = 1
    if kg:
        kg_factor = 1000
    if prefixed in _additional_prefixes: prefixes = _additional_prefixes
    else: prefixes = _prefixes
    if prefixed:
        return value / ((prefixes[prefixed] / kg_factor) ** power)
    if abs(value) >= 1:
        for prefix, power_of_ten in prefixes.items():
            if abs(value) >= (power_of_ten / kg_factor) ** abs(power):
                return value / ((power_of_ten / kg_factor) ** power)
    else:
        reverse_prefixes = sorted(prefixes.items(), key=lambda pre_fact: pre_fact[1])
        # Get the smallest factor to start...
        previous_power_of_ten = reverse_prefixes[0][1]
        for prefix, power_of_ten in reversed(list(prefixes.items())):
            if abs(value) < (power_of_ten / kg_factor) ** abs(power):
                return value / ((previous_power_of_ten / kg_factor) ** abs(power))
            else:
                previous_power_of_ten = power_of_ten


def swap_scientific_notation_float(value: float, precision: int) -> str:
    """
    Returns a deque representing 'pycode_as_deque' with any python floats that
    will get "cut-off" by the 'precision' arg when they are rounded as being 
    rendered as strings in python's "e format" scientific notation.

    A float is "cut-off" by 'precision' when it's number of significant digits will
    be less than those required by precision. 

    e.g. elem = 0.001353 with precision=3 will round to 0.001, with only one
    significant digit (1 < 3). Therefore this float is "cut off" and will be 
    formatted instead as "1.353e-3"

    elem = 0.1353 with precision=3 will round to 0.135 with three significant digits
    (3 == 3). Therefore this float will not be formatted.
    """
    if test_for_small_float(value, precision):
        new_value = (
                "{:.{precision}e}".format(value, precision=precision)
                .replace("e-0", "e-")
                .replace("e+0", "e+")
            )
        return new_value
    return


def test_for_small_float(value: float, precision: int) -> bool:
    """
    Returns True if 'value' is a float whose rounded str representation
    has fewer significant figures than the number in 'precision'. 
    Return False otherwise.
    """
    if not isinstance(value, (float)):
        return False
    if value == 0:
        return False
    value_as_str = str(round(abs(value), precision))
    if "e" in str(value):
        return True
    if "." in value_as_str:
        left, *_right = value_as_str.split(".")
        if left != "0":
            return False
    if (
        round(value, precision) != round(value, precision + 1)
        or str(abs(round(value, precision))).replace("0", "").replace(".", "")
        == str(abs(round(value, precision + 1))).replace("0", "").replace(".", "")
        == ""
    ):
        return True
    else:
        return False


def swap_scientific_notation_str(value_as_str: str) -> str:
    """
    Returns a deque representing 'line' with any python 
    float elements in the deque
    that are in scientific notation "e" format converted into a Latex 
    scientific notation.
    """
    b = "}"
    if test_for_scientific_notation_str(value_as_str):
        new_value_as_str = value_as_str.replace("e", " \\times 10 ^ {") + b
        return new_value_as_str
    return value_as_str

def test_for_scientific_notation_str(value_as_str: str) -> bool:
    """
    Returns True if 'elem' represents a python float in scientific
    "e notation".
    e.g. 1.23e-3, 0.09e5
    Returns False otherwise
    """
    test_for_float = False
    try:
        float(value_as_str)
        test_for_float = True
    except:
        pass

    if "e" in str(value_as_str).lower() and test_for_float:
        return True
    return False

def is_nan(value: Any) -> bool:
    """
    Returns True if 'value' is some form of NaN, whether float('nan')
    or a numpy or pandas Nan.
    """
    # Test for numpy.nan and float('nan')
    if not value == value:
        return True
    else:
        return False
    