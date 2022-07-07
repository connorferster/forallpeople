"""
The SI Units: "For all people, for all time"

A module to model the seven SI base units:

                    kg

            cd               m


                    SI
         mol                    s



               K           A

  ...and other derived and non-SI units for practical calculations.
"""
#    Copyright 2020 Connor Ferster

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

__version__ = "2.6.2"

from fractions import Fraction
from typing import Union, Optional
from forallpeople.dimensions import Dimensions
import forallpeople.physical_helper_functions as phf
import forallpeople.tuplevector as vec
from forallpeople.environment import Environment
import math
import builtins
import sys

NUMBER = (int, float)


class Physical(object):
    """
    A class that defines any physical quantity that can be described
    within the BIPM SI unit system.
    """

    __slots__ = ("value", "dimensions", "factor", "precision", "prefixed")

    def __init__(
        self,
        value: Union[int, float],
        dimensions: Dimensions,
        factor: float,
        precision: int = 3,
        prefixed: str = "",
    ):
        """Constructor"""
        super(Physical, self).__setattr__("value", value)
        super(Physical, self).__setattr__("dimensions", dimensions)
        super(Physical, self).__setattr__("factor", factor)
        super(Physical, self).__setattr__("precision", precision)
        super(Physical, self).__setattr__("prefixed", prefixed)

    ### API Methods ###
    @property
    def latex(self) -> str:
        return self._repr_latex_()

    @property
    def html(self) -> str:
        return self._repr_html_()

    def prefix(self, prefixed: str = "") -> Physical:
        """
        Return a Physical instance with 'prefixed' property set to 'prefix'
        if 'prefixed' is set to "unity" then the unit will be forced into its
        unprefixed state.
        """
        if self.factor != 1:
            raise AttributeError(
                "Cannot set a prefix on a Physical if it has a factor."
            )
        # check if elligible for prefixing; do not rely on __repr__ to ignore it
        return Physical(
            self.value, self.dimensions, self.factor, self.precision, prefixed
        )

    @property
    def repr(self) -> str:
        """
        Returns a repr that can be used to create another Physical instance.
        """
        repr_str = "Physical(value={}, dimensions={}, factor={:.5}, precision={}, _prefixed={})"
        factor = float(self.factor)
        if self.factor == 1:
            repr_str = "Physical(value={}, dimensions={}, factor={}, precision={}, _prefixed={})"
            factor = 1
        return repr_str.format(
            self.value, self.dimensions, factor, self.precision, self.prefixed
        )  # check

    def round(self, n: int):
        """
        Returns a new Physical with a new precision, 'n'. Precision controls
        the number of decimal places displayed in repr and str.
        """
        raise PendingDeprecationWarning(
            "Using .round() is going to be deprecated. "
            "Use Python's built-in round() function instead."
        )

    def split(self, base_value: bool = True) -> tuple:
        """
        Returns a tuple separating the value of `self` with the units of `self`.
        If base_value is True, then the value will be the value in base units. If False, then
        the apparent value of `self` will be used.

        This method is to allow flexibility in working with Physical instances when working
        with numerically optimized libraries such as numpy which cannot accept non-numerical
        objects in some of their operations (such as in matrix inversion).
        """
        if base_value:
            return (
                self.value * float(self.factor),
                Physical(
                    1 / float(self.factor), self.dimensions, self.factor, self.precision
                ),
            )
        return (float(self), Physical(1, self.dimensions, self.factor, self.precision))

    def sqrt(self, n: Union[int, float] = 2):
        """
        Returns a Physical instance that represents the square root of `self`.
        `n` can be set to an alternate number to compute an alternate root (e.g. 3.0 for cube root)
        """
        return self ** (1 / n)

    def to(self, unit_name="") -> Optional[Physical]:
        """
        Returns None and alters the instance into one of the eligible
        alternative units for its dimension, if it exists in the alternative_units dict;
        """
        dims = self.dimensions
        env_dims = environment.units_by_dimension
        derived = env_dims()["derived"]
        defined = env_dims()["defined"]
        power, dims_orig = phf._powers_of_derived(dims, env_dims)
        if not unit_name:
            print("Available units: ")
            for key in derived.get(dims_orig, {}):
                print(key)
            for key in defined.get(dims_orig, {}):
                print(key)

        if unit_name:
            defined_match = defined.get(dims_orig, {}).get(unit_name, {})
            derived_match = derived.get(dims_orig, {}).get(unit_name, {})
            unit_match = defined_match or derived_match
            if not unit_match:
                warnings.warn(f"No unit defined for '{unit_name}' on {self}.")
            new_factor = unit_match.get("Factor", 1) ** Fraction(power)
            return Physical(self.value, self.dimensions, new_factor, self.precision)

    def si(self):
        """
        Return a new Physical instance with self.factor set to 1, thereby returning
        the instance to SI units display.
        """
        return Physical(self.value, self.dimensions, 1, self.precision)

    ### repr Methods (the "workhorse" of Physical) ###

    def __repr__(self):
        return self._repr_template_()

    def _repr_html_(self):
        return self._repr_template_(template="html")

    def _repr_markdown_(self):
        return self._repr_template_(template="html")

    def _repr_latex_(self):
        return self._repr_template_(template="latex")

    def _repr_template_(self, template: str = "", format_spec="") -> str:
        """
        Returns a string that appropriately represents the Physical
        instance. The parameter,'template', allows two optional values:
        'html' and 'latex'. which will only be utilized if the Physical
        exists in the Jupyter/iPython environment.
        """
        if not format_spec:
            format_spec = f".{self.precision}f"
        dims = self.dimensions
        factor = self.factor
        float_factor = float(factor)
        val = self.value
        prefix = ""
        prefixed = self.prefixed
        kg_bool = False

        # Access external environment
        env_fact = environment.units_by_factor or dict()
        env_dims = environment.units_by_dimension or dict()

        # Do the expensive vector math method (call once, only)
        power, dims_orig = phf._powers_of_derived(dims, env_dims)

        # Determine if there is a symbol for these dimensions in the environment
        # and if the quantity is elligible to be prefixed
        symbol, prefix_bool = phf._evaluate_dims_and_factor(
            dims_orig, factor, power, env_fact, env_dims
        )
        # Get the appropriate prefix

        if prefix_bool and prefixed == "unity":
            prefix = ""
            if dims_orig == Dimensions(1, 0, 0, 0, 0, 0, 0):
                kg_bool = True
        elif prefix_bool and prefixed:
            prefix = prefixed
        elif prefix_bool and dims_orig == Dimensions(1, 0, 0, 0, 0, 0, 0):
            kg_bool = True
            prefix = phf._auto_prefix(val, power, kg=kg_bool)
        elif prefix_bool:
            prefix = phf._auto_prefix(val, power, kg=kg_bool)

        # Format the exponent (may not be used, though)
        exponent = phf._format_exponent(power, repr_format=template)

        # Format the units
        if not symbol and phf._dims_basis_multiple(dims):
            components = phf._get_unit_components_from_dims(dims)
            units_symbol = phf._get_unit_string(components, repr_format=template)
            units = units_symbol
            units = phf._format_symbol(prefix, units_symbol, repr_format=template)
            exponent = ""
        elif not symbol:
            components = phf._get_unit_components_from_dims(dims)
            units_symbol = phf._get_unit_string(components, repr_format=template)
            units = units_symbol
            exponent = ""
        else:
            units = phf._format_symbol(prefix, symbol, repr_format=template)

        # Determine the appropriate display value
        value = val * float_factor

        if prefix_bool:
            # If the quantity has a "pre-fixed" prefix, it will override
            # the value generated in _auto_prefix_value
            value = phf._auto_prefix_value(val, power, prefix, kg_bool)

        pre_super = ""
        post_super = ""
        space = " "
        pre_inline = ""
        post_inline = ""
        if template == "latex":
            space = r"\ "
            pre_super = "^{"
            post_super = "}"
            pre_inline = "$"
            post_inline = "$"
        elif template == "html":
            space = " "
            pre_super = "<sup>"
            post_super = "</sup>"
        if not exponent:
            pre_super = ""
            post_super = ""

        formatted_value = f"{value:{format_spec}}"
        if "e" in format_spec.lower():
            formatted_value = phf.format_scientific_notation(
                formatted_value, template=template
            )

        return f"{pre_inline}{formatted_value}{space}{units}{pre_super}{exponent}{post_super}{post_inline}"

    ### "Magic" Methods ###

    def __float__(self):
        value = self.value
        factor = float(self.factor)
        if factor != 1:
            return value * factor
        kg_bool = False
        dims = self.dimensions
        env_dims = environment.units_by_dimension or dict()
        power, _ = phf._powers_of_derived(dims, env_dims)
        dim_components = phf._get_unit_components_from_dims(dims)
        if len(dim_components) == 1 and dim_components[0][0] == "kg":
            kg_bool = True
        if self.prefixed:
            prefix = self.prefixed
        else:
            prefix = phf._auto_prefix(value, power, kg_bool)
        float_value = phf._auto_prefix_value(value, power, prefix, kg_bool)
        return float_value

    def __int__(self):
        return int(float(self))

    def __neg__(self):
        return self * -1

    def __abs__(self):
        if self.value < 0:
            return self * -1
        return self

    def __bool__(self):
        return True

    def __format__(self, format_spec=""):
        template = ""
        if "L" in format_spec:
            template = "latex"
            format_spec = format_spec.replace("L", "")
        elif "H" in format_spec:
            template = "html"
            format_spec = format_spec.replace("H", "")

        return self._repr_template_(template=template, format_spec=format_spec)

    def __hash__(self):
        return hash(
            (self.value, self.dimensions, self.factor, self.precision, self.prefixed)
        )

    def __round__(self, n=0):
        return Physical(self.value, self.dimensions, self.factor, n, self.prefixed)

    def __contains__(self, other):
        return False

    def __eq__(self, other):
        if isinstance(other, NUMBER):
            return math.isclose(self.value, other)
        elif type(other) == str:
            return False
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return math.isclose(self.value, other.value)
        else:
            raise ValueError(
                "Can only compare between Physical instances of equal dimension."
            )

    def __gt__(self, other):
        if isinstance(other, NUMBER):
            return self.value > other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value > other.value
        else:
            raise ValueError(
                "Can only compare between Physical instances of equal dimension."
            )

    def __ge__(self, other):
        if isinstance(other, NUMBER):
            return self.value >= other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value >= other.value
        else:
            raise ValueError(
                "Can only compare between Physical instances of equal dimension."
            )

    def __lt__(self, other):
        if isinstance(other, NUMBER):
            return self.value < other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value < other.value
        else:
            raise ValueError(
                "Can only compare between Physical instances of equal dimension."
            )

    def __le__(self, other):
        if isinstance(other, NUMBER):
            return self.value <= other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value <= other.value
        else:
            raise ValueError(
                "Can only compare between Physical instances of equal dimension."
            )

    def __add__(self, other):
        if isinstance(other, Physical):
            if self.dimensions == other.dimensions:
                try:
                    return Physical(
                        self.value + other.value,
                        self.dimensions,
                        self.factor,
                        self.precision,
                        self.prefixed,
                    )
                except:
                    raise ValueError(
                        f"Cannot add between {self} and {other}: "
                        + ".value attributes are incompatible."
                    )
            else:
                raise ValueError(
                    f"Cannot add between {self} and {other}: "
                    + ".dimensions attributes are incompatible (not equal)"
                )
        else:
            try:
                other = other / float(self.factor)
                return Physical(
                    self.value + other,
                    self.dimensions,
                    self.factor,
                    self.precision,
                    self.prefixed,
                )
            except:
                raise ValueError(
                    f"Cannot add between {self} and {other}: "
                    + ".value attributes are incompatible."
                )

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        raise ValueError(
            "Cannot incrementally add Physical instances because they are immutable."
            + " Use 'a = a + b', to make the operation explicit."
        )

    def __sub__(self, other):
        if isinstance(other, Physical):
            if self.dimensions == other.dimensions:
                try:
                    return Physical(
                        self.value - other.value,
                        self.dimensions,
                        self.factor,
                        self.precision,
                        self.prefixed,
                    )
                except:
                    raise ValueError(f"Cannot subtract between {self} and {other}")
            else:
                raise ValueError(
                    f"Cannot subtract between {self} and {other}:"
                    + ".dimensions attributes are incompatible (not equal)"
                )
        else:
            try:
                other = other / float(self.factor)
                return Physical(
                    self.value - other,
                    self.dimensions,
                    self.factor,
                    self.precision,
                    self.prefixed,
                )
            except:
                raise ValueError(
                    f"Cannot subtract between {self} and {other}: "
                    + ".value attributes are incompatible."
                )

    def __rsub__(self, other):
        if isinstance(other, Physical):
            return self.__sub__(other)
        else:
            try:
                other = other / float(self.factor)
                return Physical(
                    other - self.value,
                    self.dimensions,
                    self.factor,
                    self.precision,
                    self.prefixed,
                )
            except:
                raise ValueError(
                    f"Cannot subtract between {self} and {other}: "
                    + ".value attributes are incompatible."
                )

    def __isub__(self, other):
        raise ValueError(
            "Cannot incrementally subtract Physical instances because they are immutable."
            + " Use 'a = a - b', to make the operation explicit."
        )

    def __mul__(self, other):
        if phf.is_nan(other):
            return other
        elif isinstance(other, NUMBER):
            return Physical(
                self.value * other,
                self.dimensions,
                self.factor,
                self.precision,
                self.prefixed,
            )

        elif isinstance(other, Physical):
            new_dims = vec.add(self.dimensions, other.dimensions)
            new_power, new_dims_orig = phf._powers_of_derived(
                new_dims, environment.units_by_dimension
            )
            new_factor = self.factor * other.factor
            test_factor = phf._get_units_by_factor(
                new_factor, new_dims_orig, environment.units_by_factor, new_power
            )
            # if not test_factor:
            #     print(new_factor)
            #     new_factor = 1
            try:
                new_value = self.value * other.value
            except:
                raise ValueError(
                    f"Cannot multiply between {self} and {other}: "
                    + ".value attributes are incompatible."
                )
            if new_dims == Dimensions(0, 0, 0, 0, 0, 0, 0):
                return new_value
            else:
                return Physical(new_value, new_dims, new_factor, self.precision)
        else:
            try:
                return Physical(
                    self.value * other, self.dimensions, self.factor, self.precision
                )
            except:
                raise ValueError(
                    f"Cannot multiply between {self} and {other}: "
                    + ".value attributes are incompatible."
                )

    def __imul__(self, other):
        raise ValueError(
            "Cannot incrementally multiply Physical instances because they are immutable."
            + " Use 'a = a * b' to make the operation explicit."
        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if phf.is_nan(other):
            return other
        elif isinstance(other, NUMBER):
            return Physical(
                self.value / other,
                self.dimensions,
                self.factor,
                self.precision,
                self.prefixed,
            )
        elif isinstance(other, Physical):
            new_dims = vec.subtract(self.dimensions, other.dimensions)
            new_power, new_dims_orig = phf._powers_of_derived(
                new_dims, environment.units_by_dimension
            )
            new_factor = self.factor / other.factor
            # if not phf._get_units_by_factor(
            #     new_factor, new_dims_orig, environment.units_by_factor, new_power
            # ):
            #     new_factor = 1
            try:
                new_value = self.value / other.value
            except:
                raise ValueError(
                    f"Cannot divide between {self} and {other}: "
                    + ".value attributes are incompatible."
                )
            if new_dims == Dimensions(0, 0, 0, 0, 0, 0, 0):
                return new_value
            else:
                return Physical(new_value, new_dims, new_factor, self.precision)
        else:
            try:
                return Physical(
                    self.value / other, self.dimensions, self.factor, self.precision
                )
            except:
                raise ValueError(
                    f"Cannot divide between {self} and {other}: "
                    + ".value attributes are incompatible."
                )

    def __rtruediv__(self, other):
        if phf.is_nan(other):
            return other
        if isinstance(other, NUMBER):
            new_value = other / self.value
            new_dimensions = vec.multiply(self.dimensions, -1)
            new_factor = self.factor**-1  # added new_factor
            return Physical(
                new_value,
                new_dimensions,
                new_factor,  # updated from self.factor to new_factor
                self.precision,
            )
        else:
            try:
                return Physical(
                    other / self.value,
                    vec.multiply(self.dimensions, -1),
                    self.factor**-1,  # updated to ** -1
                    self.precision,
                )
            except:
                raise ValueError(
                    f"Cannot divide between {other} and {self}: "
                    + ".value attributes are incompatible."
                )

    def __itruediv__(self, other):
        raise ValueError(
            "Cannot incrementally divide Physical instances because they are immutable."
            + " Use 'a = a / b' to make the operation explicit."
        )

    def __pow__(self, other):
        if isinstance(other, NUMBER):
            if self.prefixed:
                return float(self) ** other
            new_value = self.value**other
            new_dimensions = vec.multiply(self.dimensions, other)
            new_factor = phf.fraction_pow(self.factor, other)
            return Physical(new_value, new_dimensions, new_factor, self.precision)
        else:
            raise ValueError(
                "Cannot raise a Physical to the power of \
                                     another Physical -> ({self}**{other})".format(
                    self, other
                )
            )


# The seven SI base units...
_the_si_base_units = {
    "kg": Physical(1, Dimensions(1, 0, 0, 0, 0, 0, 0), 1),
    "m": Physical(1, Dimensions(0, 1, 0, 0, 0, 0, 0), 1),
    "s": Physical(1, Dimensions(0, 0, 1, 0, 0, 0, 0), 1),
    "A": Physical(1, Dimensions(0, 0, 0, 1, 0, 0, 0), 1),
    "cd": Physical(1, Dimensions(0, 0, 0, 0, 1, 0, 0), 1),
    "K": Physical(1, Dimensions(0, 0, 0, 0, 0, 1, 0), 1),
    "mol": Physical(1, Dimensions(0, 0, 0, 0, 0, 0, 1), 1),
}

environment = Environment(Physical, builtins, _the_si_base_units)
environment._push_vars(_the_si_base_units, sys.modules[__name__])
