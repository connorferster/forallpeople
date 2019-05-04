#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from forallpeople import tuplevector_lite as vec
import json
import re
import sys
import copy
from collections import defaultdict, ChainMap
from collections import namedtuple
from decimal import Decimal
from forallpeople import tuplevector_lite as vec


# TODO: Add support for displaying fractional dimensions

class DimensionError(Exception):
    """
    A class to describe an error based on incompatible dimensions
    """
    pass

Dimensions = namedtuple("Dimensions", ["kg", "m", "s", "A", "cd", "K", "mol"])


number = (int, float, Decimal)

# The single class to describe all units...Physical (as in physical property)   
class Physical:
    """
    A base class to define all of the properties that an SI unit would have
    """
    _superscripts = {"1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸",
                "9": "⁹", "0": "⁰", "-": "⁻", ".": "'"}
  
    _prefixes = {'T': 1e12,'G': 1e9,'M': 1e6,'k': 1e3,'': 1.0,
            'm': 1e-3,'μ': 1e-6,'n': 1e-09,'p': 1e-12}

    _precision = 3
    
    def __init__(self, value: str, dimensions, in_units = None, factor = 1):
        self.value = value
        if isinstance(dimensions, (list)):
            dimensions = Dimensions(dimensions)
        elif not isinstance(dimensions, tuple):
            raise ValueError("'dimensions' must be either list, tuple, "
                             "or Dimensions; not {}".format(type(dimensions)))
        self.dimensions = dimensions
        self._in_units = in_units
        self._factor = factor
        
        # "Lookup by factor" method of assigning "self.in_units":
        # Allows alternative units to naturally persist and combine and re-derive
        # themselves when performing a string of calculations. 
        # i.e. allows the result of lb*ft = ft-lb if all three are defined
        
        if factor != 1 and not in_units: # below ensures a dimensions check when doing a factor lookup
            potential_units = environment.units_by_factor.get(factor, None) # <- the factor lookup
            potential_match = environment.environment.get(potential_units, None)
            if potential_match:
                possible_matching_dimensions = potential_match.get("Dimension", None)
                possible_matching_symbol = potential_match.get("Symbol", potential_units)
                if possible_matching_dimensions is not None and\
                   (self.dimensions == possible_matching_dimensions):
                    self._in_units = possible_matching_symbol
                else:
                    self._factor = 1
            else:
                self._factor = 1
        
    def __repr__(self):
        return self._repr_template_()
    
    def _repr_html_(self):
        return self._repr_template_(template="html")
        
    def _repr_markdown_(self):
        return self._repr_html_()
        
    def _repr_latex_(self):
        return self._repr_template_(template="latex")
     
    def _repr_template_(self, template="") -> str:
        """Returns a string that appropriately represents the Physical instance.
        'template' allows two optional values: 'html', 'latex'.
        'html' and 'latex' are used with Jupyter."""

        precision = self._precision
        factor = self._factor #float
        in_units = self._in_units 
        units = self._return_units(repr_format=template)
        value = self._return_value()
        exponent = self._return_exponent()        
        
        pre_super = ""
        post_super = ""
        space = " "
        if template == "latex":
            space = "\ "
            pre_super = "^{"
            post_super = "}"
        elif template == "html": 
            space = " "
            pre_super = "<sup>"
            post_super = "</sup>"
        
        if not exponent or exponent == 1:
            pre_super = ""
            post_super = ""
        if exponent and exponent != 1 and not template:
            exponent = Physical._get_superscript_string(exponent)
        
        return "{0:.{1}f}{2}{3}{4}{5}{6}".format(value, precision, space, units, 
                                                 pre_super, exponent, post_super)
    def __round__(self, precision=0):
        self._precision = precision
        return self
        
#    def __str__(self):
#        return repr(self)

    def __hash__(self):
        return hash((self.value, self.dimensions, self._in_units, self._factor))

    def _return_symbol(self):
        """Part of the __str__ and __repr__ process. Returns the display symbol
        of the Physical instance, if appropriate. Returns '' otherwise."""
        derived_name = self._get_derived_name(self.dimensions) #Optional[str]
        symbol = ""
        in_units = self._in_units
        unit_name = in_units or derived_name
        if unit_name and (derived_name or in_units):
            has_value_key = environment.environment.get(unit_name, {}).get("Value", False)
            if not has_value_key:
                symbol = environment.environment.get(unit_name, {}).get("Symbol", unit_name)
        return symbol
    
    def _return_prefix(self):
        """Part of the __str__ and __repr__ process. Returns the applicable
        prefix of the Physical instance, if appropriate. Returns '' otherwise."""
        has_mass = self.dimensions[0] != 0
        single_dim = vec.magnitude(self.dimensions) == 1
        is_basis_multiple = self._dims_basis_multiple(self.dimensions)
        derived_name = self._get_derived_name(self.dimensions)
        in_units = self._in_units
        
        prefix = ""
        if has_mass and single_dim:
            prefix = self._auto_prefix_kg()
        elif (derived_name or single_dim or is_basis_multiple is not None) and not in_units:
            prefix = self._auto_prefix()
        return prefix
    
    def _get_unit_string(self, unit_components: list, repr_format: str) -> str:
        """Part of the __str__ and __repr__ process. Returns a string representing 
        the SI unit components of the Physical instance extracted from the list of
        tuples, 'unit_components', using 'repr_format' as given by the _repr_x_
        function it was called by. If 'repr_format' is not given, then terminal
        output is assumed."""
        dot_operator = "⋅"
        pre_super = ""
        post_super = ""
        pre_unit = ""
        post_unit = ""
        prefix = self._return_prefix()
        if repr_format == "html":
            dot_operator = "&#8901;"
            pre_super = "<sup>"
            post_super = "</sup>"
        elif repr_format == "latex":
            dot_operator = " \cdot "
            pre_unit = "\\text{"
            post_unit = "}"
            pre_super = "^{"
            post_super = "}"

        if repr_format == "html" or repr_format == "latex":
            unit_string = ""
            str_components = []
            for unit, exponent in unit_components:
                if exponent == 1:
                    this_component = "{0}{1}{2}{3}".format(pre_unit, prefix, unit, post_unit)
                else:
                    this_component = "{0}{1}{2}{3}{4}{5}{6}".format(pre_unit, prefix, unit, 
                                                                    post_unit, pre_super, exponent, 
                                                                    post_super)
                str_components.append(this_component)
            return dot_operator.join(str_components)
        else: # terminal output
            unit_string = ""
            str_components = []
            for unit, exponent in unit_components:
                if exponent == 1:
                    this_component = "{0}{1}".format(prefix,unit)
                else:
                    super_exponent = Physical._get_superscript_string(exponent)
                    this_component = "{0}{1}{2}".format(prefix, unit, super_exponent)
                str_components.append(this_component)
            return dot_operator.join(str_components)
        
    @staticmethod
    def _get_superscript_string(exponent: float) -> str:
        """Part of the __str__ and __repr__ process. Returns the unicode 
        "superscript" equivalent string for a given float."""
        exponent_components = list(str(exponent))
        if exponent == int(exponent):
            exponent_components = list(str(int(exponent)))
            
        exponent_string = ""
        for component in exponent_components:
            exponent_string += Physical._superscripts[component]
        return exponent_string          
    
    def _return_value(self):
        """Part of the __str__ and __repr__ process. Returns the applicable value
        of the Physical instance with appropriate transformations/conversions."""
        prefix = self._return_prefix()
        value = self._auto_value()        
        if prefix:
            value = self._auto_prefix_value()
        return value
        
    def _return_units(self, repr_format: str):
        """Part of the __str__ and __repr__ process. Returns the most appropriate
        unit string of the Physical instance, e.g. Returns the appropriate symbol 
        for the units if defined in an environment .json file. Returns '' otherwise.
        """     
        unit_string_open = ""
        unit_string_close = ""
        dot_operator = "·"
        ohm = "Ω"
        prefix = self._return_prefix()            
        if repr_format == "html":
            dot_operator = "&#8901;"
            ohm = "&#0937;"
        elif repr_format == "latex":
            dot_operator = " \cdot "
            ohm = "\Omega"
            unit_string_open = "\\text{"
            unit_string_close = "}"
            
        in_units = self._in_units
        symbol = self._return_symbol()
        symbol = symbol.replace("·", unit_string_close+dot_operator+unit_string_open)\
                       .replace("*", unit_string_close+dot_operator+unit_string_open)\
                       .replace("Ω", ohm)
        unit_string = self._get_unit_string(unit_components = self._unit_data_from_dims(), 
                                            repr_format=repr_format)
        

        if symbol or in_units:
            units = in_units or symbol
            formatted_units = "{}{}{}{}".format(unit_string_open, prefix, units, unit_string_close)
        else: 
            formatted_units = unit_string
        return formatted_units
    
    def _return_exponent(self) -> str:
        """Part of the __str__ and __repr__ process. Returns the exponent of 
        the units of the Physical instance if the units of the instance is 
        being represented by a defined derived/alternate unit symbol. 
        Returns '', otherwise."""
        power_of_derived = self._powers_of_derived(self.dimensions)
        exponent = ""
        derived_name = self._get_derived_name(self.dimensions)
        basis_multiple = self._dims_basis_multiple(self.dimensions)
        if power_of_derived and (derived_name or self.in_units) and not basis_multiple:
            if power_of_derived != 1:
                exponent = power_of_derived
            if exponent and exponent == int(exponent):
                exponent = int(exponent)
        return str(exponent)
        
    # API Methods
    @property
    def latex(self):
        return self._repr_latex_()
    
    @property
    def components(self):
        """
        Returns a repr that can be used to create another Physical instance.
        """
        repr_str = "{}(value={}, dimensions={}, in_units={}, factor={})"
        return repr_str.format(self.__class__.__name__, self.value,
                               self.dimensions, self._in_units, self._factor)
    
    def in_units(self, unit_string=""):
        """
        Returns None and alters the instance into one of the elligible 
        alternative units for its dimension, if it exists in the alternative_units dict;
        """
        dimensions = self.dimensions
        powers_of_derived = self._powers_of_derived(dimensions)
        exponent = powers_of_derived
        if not powers_of_derived:
            exponent = 1
        dimensions = self._dims_original(dimensions)
        alt_options = environment.units_by_dimension['alts'].get(dimensions, [])
        si_options = environment.units_by_dimension['si'].get(dimensions, [])
        unit_options = alt_options + si_options
        if not unit_string:
            return "{0} can be view in units of: {1}".format(self, unit_options)
        if unit_options and unit_string in unit_options:
            self._factor = environment.environment[unit_string].get("Factor", 1)**exponent
            self._in_units = environment.environment[unit_string].get("Symbol", unit_string)
            return self
        else:
            raise KeyError("Unit string {} is not found in the units environment.".format(unit_string))
            
            
    def si(self):
        """
        Returns None; sets self._in_units and self._factor to None.
        Effectively "reverts" the Physical to base SI units
        """
        self._in_units = None
        self._factor = 1
        return self
                
            
    # "Private" methods and helper functions
    @classmethod    
    def _get_derived_name(cls, dimensions: Dimensions):
        """
        Returns the name of the derived unit if 'dimensions' matches one of the 
        dimensions stored in the environment as defined by the loaded configuration
        .json file. 
        Returns None if a match is not found"""
        powers_of_derived = cls._powers_of_derived(dimensions)
        if powers_of_derived:
            dimensions = cls._dims_original(dimensions)
        possible_units = environment.units_by_dimension.get("si").get(dimensions)
        if type(possible_units) is list:
            return possible_units[0]
        else:
            return None
        
    @staticmethod
    def _dims_quotient(dimensions: Dimensions) -> Dimensions:
        """
        Returns a Dimensions object representing the element-wise quotient betwe
        'dimensions' and a defined unit if 'dimensions' is a scalar multiple
        of a defined unit in the global environment variable.
        Returns None otherwise.
        """
        si = environment.units_by_dimension.get('si')
        alts = environment.units_by_dimension.get('alts')
        merged_si_alts = ChainMap(si, alts)
        for dimension_key in merged_si_alts.keys():
            if vec.multiply(dimension_key, vec.dot(dimensions,dimensions)) == \
               vec.multiply(dimensions, vec.dot(dimensions, dimension_key)):
                quotient = vec.divide(dimensions,dimension_key)
                return quotient
        return None     
    
    @staticmethod
    def _dims_basis_multiple(dimensions: Dimensions) -> Dimensions:
        """
        Returns True if 'dimensions' is a scalar multiple of one of the basis
        vectors (e.g. [3,0,0,0,0,0,0] is a scalar multiple of [1,0,0,0,0,0,0]).
        Returns None, otherwise.
        """
        bases_vectors = ([1,0,0,0,0,0,0], [0,1,0,0,0,0,0], [0,0,1,0,0,0,0],
                         [0,0,0,1,0,0,0], [0,0,0,0,1,0,0], [0,0,0,0,0,1,0],
                         [0,0,0,0,0,0,1])
        result = False
        for basis in bases_vectors:
            to_test = Dimensions(*basis)
            if vec.multiply(to_test, vec.dot(dimensions, dimensions)) ==\
               vec.multiply(dimensions, vec.dot(dimensions, to_test)):
                return vec.divide(dimensions, to_test)
        return None
                             
    @classmethod
    def _powers_of_derived(cls, dimensions: Dimensions):
        """
        Returns an integer value that represents the exponent of a unit if the dimensions
        array is a multiple of one of the defined derived units in dimension_keys. Returns None,
        otherwise.
        e.g. a force would have dimensions = [1,1,-2,0,0,0,0] so a Physical object
        that had dimensions = [2,2,-4,0,0,0,0] would really be a force to the power of 2.
        The function returns the 2.
        """
        quotient_1 = cls._dims_quotient(dimensions)
        quotient_2 = cls._dims_basis_multiple(dimensions)
        if quotient_1 is not None:
            power_of_derived = vec.mean(quotient_1, ignore_empty=True)
            return power_of_derived
        elif quotient_2 is not None:
            power_of_basis = vec.mean(quotient_2, ignore_empty=True)
            return power_of_basis

        
    @staticmethod
    def _dims_original(dimensions: Dimensions):
        """
        Returns a dimensions array that represents the base dimensions of a unit, 
        in the event that the Physical is a unit to a power.
        e.g. A Newton, N, would have dimensions [1,1,-2,0,0,0,0] but N**2 would have
        dimensions [2,2,-4,0,0,0,0]. 
        Physical._dims_original(Dimensions(2,2,-4,0,0,0,0) would return ->
        Dimensions(1,1,-2,0,0,0,0) because that would be the original dimensions
        of N**2.
        """
        quotient = Physical._dims_quotient(dimensions)
        if quotient is not None:
            orig_dims = vec.divide(dimensions, quotient)
            return orig_dims
        else:
            return dimensions
              
    def _unit_data_from_dims(self):
        """
        Returns a list of tuples to represent the current units based 
        on the current dimensions. Dimension ignored if 0.
        e.g. [('kg', 1), ('m', -1), ('s', -2)]
        """
        unit_data = []
        unit_symbols = self.dimensions._fields
        for idx, dim in enumerate(self.dimensions):
            if dim != 0:
                unit_tuple = (unit_symbols[idx], dim)
                unit_data.append(unit_tuple)
        return unit_data
       
    def _auto_value(self):
        """
        Returns the value to be displayed in __str__(). This value represents the value
        of the Physical in whatever dimension in whatever units it is intended to be in
        based on its ._factor.
        """
        powers_of_derived = self._powers_of_derived(self.dimensions)
        if not powers_of_derived:
            powers_of_derived = 1
        return self.value * self._factor ** powers_of_derived
    
    def _auto_prefix(self):
        """
        Returns a string "prefix" of an appropriate value if self.value should be prefixed
        i.e. it is a big enough number (e.g. 5342 >= 1000; returns "k" for "kilo")
        """      
        prefixes = self._prefixes
        powers_of_derived = self._powers_of_derived(self.dimensions)
        if not powers_of_derived:
            powers_of_derived = 1
        if abs(self.value) >= 1:
            for prefix, factor in prefixes.items():
                if abs(self.value) >= factor ** powers_of_derived:                    
                    return prefix
        else:
            reverse_prefixes = sorted(prefixes.items(), key = lambda prefix: prefix[0])
            previous_prefix = reverse_prefixes[0][0] # Gets the smallest prefix to start
            for prefix, factor in reversed(list(prefixes.items())):
                if abs(self.value) < factor ** powers_of_derived:
                    return previous_prefix
                else:                     
                    previous_prefix = prefix
                    
            
    def _auto_prefix_kg(self):
        """
        Just like _auto_prefix but handles the one special case for "kg" because it already
        has a prefix of "k" as an SI base unit
        """     
        prefixes = self._prefixes
        powers_of_derived = self._powers_of_derived(self.dimensions)
        if self.dimensions[0] != 0:
            for prefix, factor in self._prefixes.items():
                if abs(self.value) >= factor/1000:                    
                    return prefix
            
    def _auto_prefix_value(self):
        """
        Converts the value to a prefixed value if the instance has a symbol defined in 
        the environment (i.e. is in the defined units dict)
        """
        prefixes = self._prefixes
        powers_of_derived = self._powers_of_derived(self.dimensions)
        conversion_factor = self._factor
        value = self.value * conversion_factor
        if not powers_of_derived:
            powers_of_derived = 1
        if abs(value) >= 1:
            for prefix, power_factor in self._prefixes.items():
                if abs(value) >= power_factor ** powers_of_derived:
                    return value / (power_factor ** powers_of_derived)
        else:
            reverse_prefixes = sorted(self._prefixes.items(), key = lambda pre_fact: pre_fact[1])
            previous_power_factor = reverse_prefixes[0][1] # Gets the smallest factor to start
            for prefix, power_factor in reversed(list(prefixes.items())):
                if abs(value) < power_factor ** powers_of_derived:
                    return value / (previous_power_factor ** powers_of_derived)
                else:                     
                    previous_power_factor = power_factor
                    
    
    def __eq__(self, other):
        if isinstance(other,number):
            return self.value == other
        elif type(other) == str:
            return True
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value == other.value
        else:
            raise AttributeError("Can only compare between Physicals of equal dimension")
            
    def __gt__(self, other):
        if isinstance(other,number):
            return self.value > other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value > other.value
        else:
            raise AttributeError("Can only compare between PhysicalProperties of equal dimension")
            
    def __ge__(self, other):
        if isinstance(other,number):
            return self.value >= other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value >= other.value
        else:
            raise AttributeError("Can only compare between PhysicalProperties of equal dimension")
            
    def __lt__(self, other):
        if isinstance(other,number):
            return self.value < other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value < other.value
        else:
            raise AttributeError("Can only compare between PhysicalProperties of equal dimension")
            
    def __le__(self, other):
        if isinstance(other,number):
            return self.value <= other
        elif isinstance(other, Physical) and self.dimensions == other.dimensions:
            return self.value <= other.value
        else:
            raise AttributeError("Can only compare between Physical of equal dimension")
            
    def __add__(self, other):
        if isinstance(other, number):
            other = other * self._factor
            return self.__class__(self.value + other, self.dimensions, self._in_units)        
        else:
            try:
                return self.__class__(self.value + other.value, self.dimensions, self._in_units, factor = self._factor)
            except:
                raise NotImplementedError("Cannot add between {} and {}".format(self.components(), other.components()))
    
    def __radd__(self, other):
        return self.__add__(other)
            
    def __iadd__(self, other):
        self = self + other
        return self
        
    def __sub__(self, other):
        if isinstance(other, number):
            other = other * self._factor
            return self.__class__(self.value - other, self.dimensions)
        else:
            try:
                return self.__class__(self.value - other.value, self.dimensions, self._in_units, factor=self._factor)
            except:
                raise NotImplementedError("Cannot add between {} and {}".format(self.components(), other.components()))
    
    def __rsub__(self, other):
        if type(self) is type(other):
            return self.__sub__(other)
        elif isinstance(other, number):
            return self.__class__(other - self.value, self.dimensions)
        else:
            raise NotImplementedError
            
    def __isub__(self, other):
        self = self - other
        return self
            
    def __mul__(self, other):
        if isinstance(other, number):
            new_value = self.value * other
            return self.__class__(new_value, self.dimensions, in_units = self._in_units, factor=self._factor)
        else:
            try:
                new_dimensions = vec.add(self.dimensions, other.dimensions)
                new_value = self.value * other.value
                if new_dimensions == Dimensions(0,0,0,0,0,0,0):
                    return new_value
                else:
                    return Physical(new_value, new_dimensions, in_units = None, factor = self._factor*other._factor)
            except:
                raise NotImplementedError
            
    def __imul__(self, other):
        if isinstance(other, number):
            self.value *= other
            return self
            
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, other):
        if isinstance(other, number):
            new_value = self.value / other
            return Physical(new_value, self.dimensions, in_units = self._in_units, factor = self._factor)
        else:
            try: 
                new_dimensions = vec.subtract(self.dimensions, other.dimensions)
                new_value = self.value / other.value
                if new_dimensions == Dimensions(0,0,0,0,0,0,0):
                    return new_value
                else:
                    return Physical(new_value, new_dimensions, in_units = None, factor = self._factor/other._factor)
            except:
                raise NotImplementedError
            
    def __rtruediv__(self, other):
        if isinstance(other, number):
            new_value = self.value / other
            new_dimensions = vec.multiply(self.dimensions, -1)
            return Physical(new_value, new_dimensions)
        else:
            raise NotImplementedError
            
    def __pow__(self, other):
        if isinstance(other, number):
            new_value = self.value ** other
            new_dimensions = vec.multiply(self.dimensions, other)
            new_factor = self._factor
            return Physical(new_value, new_dimensions, self._in_units, factor = new_factor)
        else:
            raise ValueError("Cannot raise a Physical to the power of \
                                     another Physical -> ({self}**{other})".format(self,other))
            
    def __abs__(self):
        if self.value < 0:
            return self * -1
        return self
    
class Environment:
    """
    A class that contains information about the units definitions that will be used
    by each Physical instance. Each Physical instance requests units definition 
    information from the single SIEnvironment instance (OMG! Singleton!)
    """
    environment = {}
    si = dict()
    alts = dict()
    units_by_dimension = {"si": si, "alts": alts}
    units_by_factor = {}
    
    def __init__(self, physical_class):
        self._physical_class = physical_class
    
    def __call__(self, env_name: str):
        self.environment = self.load_environment(env_name)
        self.units_by_factor = {}                            
        for name, definition in self.environment.items():
            factor = definition.get("Factor", 1)
            dimension = definition.get("Dimension")
            value = definition.get("Value", None)
            if factor == 1 and not value:
                self.units_by_dimension["si"].setdefault(dimension, list()).append(name)
            elif not value:
                self.units_by_dimension["alts"].setdefault(dimension, list()).append(name)                     
                self.units_by_factor.update({factor: name})
        self.instantiator(self.environment, self._physical_class)
    
    def load_environment(self, env_name: str):
        """
        Returns a dict that describes a set of unit definitions as contained in the 
        JSON file titled "'env_name'.json" after the 'Dimension' definition is converted to 
        an Dimensions object and any factors are checked for safety then evaluated.
        Raises error if file not found.
        """
        dim_array_not_defn = "Dimension array not defined in environment"\
                             " .json file, '{env_name}.json', for unit '{unit}'"
        unit_factor_not_eval = "Unit definition in '{env_name}.json': Factor"\
                             "must be an arithmetic expr (as a str), a float,"\
                             "or an int: not '{factor}'."
        
        path = __file__.strip("__init__.py")
        filename = path + env_name + ".json"
        with open(filename, 'r') as json_unit_definitions:
            units_environment = json.load(json_unit_definitions)

        # Load definitions
        arithmetic_expr = re.compile(r"[0-9.*/+-]")
        for unit, definitions in units_environment.items():
            dimensions = definitions.get("Dimension", False)
            factor = definitions.get("Factor", "1")
            symbol = definitions.get("Symbol", False)
            if not dimensions:
                raise DimensionError(dim_array_not_defn.format(env_name, unit))
            else:
                units_environment[unit]["Dimension"] = Dimensions(*dimensions)

            if type(factor) is str and not arithmetic_expr.match(factor):
                raise ValueError(unit_factor_not_eval.format(unit, env_name, factor))
            else:
                factor = str(factor)
                units_environment[unit]["Factor"] = eval(factor) 
        return units_environment
    
    def instantiator(self, environment: dict, physical_class):
        """
        Returns None; updates the globals dict with the units defined in the "definitions" 
        portion of the environment dict
        """
        to_globals = {}
        # Transfer definitions
        for unit, definitions in self.environment.items():
            dimensions = definitions["Dimension"]
            factor = definitions.get("Factor", 1)
            symbol = definitions.get("Symbol", None)
            value = definitions.get("Value", 1)
            if symbol:
                to_globals.update({unit: physical_class(1/factor, dimensions, in_units = symbol, factor=factor)})
            else:
                to_globals.update({unit: physical_class(value, dimensions)})
        globals().update(to_globals)


if not "environment" in globals(): 
    environment = Environment(Physical)

# The seven SI base units...
_the_si_base_units = {
    "kg": Physical(1, Dimensions(1,0,0,0,0,0,0)),
    "m": Physical(1, Dimensions(0,1,0,0,0,0,0)),
    "s": Physical(1, Dimensions(0,0,1,0,0,0,0)),
    "A": Physical(1, Dimensions(0,0,0,1,0,0,0)),
    "cd": Physical(1, Dimensions(0,0,0,0,1,0,0)),
    "K": Physical(1, Dimensions(0,0,0,0,0,1,0)),
    "mol": Physical(1, Dimensions(0,0,0,0,0,0,1))}
globals().update(_the_si_base_units)
    
def fsqrt(p: Physical) -> Physical:
    """"
    Returns the fake square root of 'p'.
    The fake square root is the square root of the apparent
    value of a Physical. 
     e.g. 9 * kN**2 <- apparent_value = 9 kN
                       actual_value = 9000 N
                       fsqrt(9*kN) = 3 kN
                       sqrt(9*kN) = 94.868 N
                       
    """
    if isinstance(p, number):
        return (p)**(1/2)
    elif isinstance(p, Physical):
        value = Physical._auto_prefix_value(p)
        unit_holder = p / value
        new_value = value**(1/2)
        return new_value * unit_holder