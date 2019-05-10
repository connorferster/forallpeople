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
import json
import re
import collections
from typing import NamedTuple, Union, Tuple, List, Any, Optional
import tuplevector as vec
from collections import ChainMap

from decimal import Decimal


number = (int, float, Decimal)

class DimensionError(Exception):
    """
    A class to describe an error based on incompatible dimensions
    """
    pass

class Dimensions(NamedTuple):
    kg: int
    m: int
    s: int
    A: int
    cd: int
    K: int
    mol: int
        
    def __add__(self, other):
        return vec.add(self, other)
    def __sub__(self, other):
        return vec.subtract(self, other)
    def __mul__(self, other):
        return vec.multiply(self, other)
    def __truediv__(self, other):
        return vec.divide(self, other)
    def __pow__(self, other):
        return vec.pow(self, other)



# The single class to describe all units...Physical (as in "a physical property")   
class Physical:
    """
    A class that defines any physical quantity that *can* be described
    within the BIPM SI unit system.
    """
    _prefixes = {'T': 1e12,'G': 1e9,'M': 1e6,'k': 1e3,'': 1.0,
                 'm': 1e-3,'μ': 1e-6,'n': 1e-09,'p': 1e-12}
    _precision = 3
    _superscripts = {"1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
                     "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "0": "⁰", 
                     "-": "⁻", ".": "'"}

    
    def __init__(self, value: Any, 
                 dimensions: Union[Dimensions, list, tuple], 
                 factor: float = 1.):
        self.value = value
        self.dimensions = Dimensions(*dimensions)
        self.factor = factor
        
    ### API Methods ###
    @property
    def symbol(self):
        return self._return_symbol()
        
    @property
    def latex(self):
        return self._repr_latex_()
    
    @property
    def components(self):
        """
        Returns a repr that can be used to create another Physical instance.
        """
        repr_str = "{}(value={}, dimensions={}, factor={})"
        return repr_str.format(self.__class__.__name__, self.value,
                               self.dimensions, self.factor)
    
    def in_units(self, unit_string=""):
        """
        Returns None and alters the instance into one of the elligible 
        alternative units for its dimension, if it exists in the alternative_units dict;
        """
        env_dims = environment.units_by_dimension
        dimensions = self.dimensions
        powers_of_derived = self._powers_of_derived(dimensions)
        exponent = powers_of_derived
        if not powers_of_derived:
            exponent = 1
        dimensions = self._dims_original(dimensions, env_dims)
        alt_options = environment.units_by_dimension['alts'].get(dimensions, [])
        si_options = environment.units_by_dimension['si'].get(dimensions, [])
        unit_options = alt_options + si_options
        if not unit_string:
            return "{0} can be view in units of: {1}".format(self, unit_options)
        if unit_options and unit_string in unit_options:
            self.factor = environment.environment[unit_string].get("Factor", 1)**exponent
            #self.symbol = environment.environment[unit_string].get("Symbol", unit_string)
            return self
        else:
            raise KeyError("Unit string {} is not found in the units environment.".format(unit_string))
            
    def si(self):
        """
        Returns None; sets self._in_units and self.factor to None.
        Effectively "reverts" the Physical to base SI units
        """
        self.factor = 1
        return self
    
    ### Repr and String methods ###
    def __repr__(self):
        return self._repr_template_()
    
    def _repr_html_(self):
        return self._repr_template_(template="html")
        
    def _repr_markdown_(self):
        return self._repr_template_(template="html")
        
    def _repr_latex_(self):
        return self._repr_template_(template="latex")
     
    def _repr_template_(self, template: str = "") -> str:
        """
        Returns a string that appropriately represents the Physical
        instance. The parameter,'template', allows two optional values: 
        'html' and 'latex'. which will only be utilized if the Physical
        exists in the Jupyter/iPython environment.
        """
        precision = self._precision
        factor = self.factor
        symbol = self.symbol
        units = self._return_units(repr_format=template)
        value = self._return_value()
        exponent = self._return_exponent()        
        
        pre_super = ""
        post_super = ""
        space = " "
        if template == "latex":
            space = r"\ "
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
        
        return f"{value:.{precision}f}{space}{units}{pre_super}{exponent}{post_super}"

        
#    def __str__(self):
#        return repr(self)



    def _return_symbol(self):
        """Part of the __str__ and __repr__ process. Returns the display symbol
        of the Physical instance, if appropriate. Returns '' otherwise."""
        env_fact = environment.units_by_factor
        env_dims = environment.units_by_dimension
        factor = self.factor
        dims = self.dimensions    
        defined = self._get_units_by_factor(factor, dims, env_fact)  
        derived = self._get_derived_unit(dims, env_dims)
        units_match = defined or derived
                  
        if units_match:
            name = tuple(units_match.keys())[0]
            symbol = units_match.get("Symbol", "")
            return symbol or name
        else: return ""
    
    def _return_value(self):
        """Part of the __str__ and __repr__ process. Returns the applicable value
        of the Physical instance with appropriate transformations/conversions."""
        val = self.value
        dims = self.dimensions
        fact = self.factor
        env_dims = environment.units_by_dimension
                  
        prefix = self._return_prefix()       
        if prefix:
            value = self._auto_prefix_value(val, dims, fact, env_dims)
        else:
            value = self._auto_value(val, dims, fact, env_dims) 
        return value
    
    def _return_prefix(self):
        """Part of the __str__ and __repr__ process. Returns the applicable
        prefix of the Physical instance, if appropriate. Returns '' otherwise."""
        val = self.value
        dims = self.dimensions
        env_dims = environment.units_by_dimension
                  
        has_mass = dims[0] != 0
        single_dim = vec.magnitude(dims) == 1
        if has_mass and single_dim: # i.e. Physical is representing mass, only
            prefix = self._auto_prefix_kg(val, dims, env_dims)
        else:
            prefix = self._auto_prefix(val, dims, env_dims)
        return prefix
                  
    def _return_units(self, repr_format: str):
        """Part of the __str__ and __repr__ process. Returns the most appropriate
        unit string of the Physical instance, e.g. Returns the appropriate symbol 
        for the units if defined in an environment .json file. Returns '' otherwise.
        """    
        dims = self.dimensions
        prefix = self._return_prefix() 
        symbol = self._return_symbol()          
        unit_components = self._get_unit_components_from_dims(dims)
        unit_string = self._get_unit_string(prefix, unit_components, repr_format)
                  
        unit_string_open = ""
        unit_string_close = ""
        dot_operator = "·"
        ohm = "Ω"
        if repr_format == "html":
            dot_operator = "&#8901;"
            ohm = "&#0937;"
        elif repr_format == "latex":
            dot_operator = r" \cdot "
            ohm = r"\Omega"
            unit_string_open = "\\text{"
            unit_string_close = "}"
                  
        if symbol:

            symbol = symbol.replace("·", unit_string_close+dot_operator+unit_string_open)\
                           .replace("*", unit_string_close+dot_operator+unit_string_open)\
                           .replace("Ω", ohm)
            print(symbol)
            formatted_units = f"{unit_string_open}{prefix}{symbol}{unit_string_close}"
        else: 
            formatted_units = unit_string
        return formatted_units
                  
    def _return_exponent(self) -> str:
        """Part of the __str__ and __repr__ process. Returns the exponent of 
        the units of the Physical instance if the units of the instance is 
        being represented by a defined derived/alternate unit symbol. 
        Returns '', otherwise."""
        dims = self.dimensions
        env_dims = environment.units_by_dimension        
        power_of_derived = self._powers_of_derived(dims, env_dims)
        symbol = self._return_symbol()
        basis_multiple = self._dims_basis_multiple(dims) 
        exponent = ""
        eps = 1e-7

        if power_of_derived and symbol and not basis_multiple:
            if power_of_derived != 1:
                exponent = power_of_derived
            # quick check for float errors...      
            if exponent and (exponent - round(exponent)) < eps: 
                exponent = round(exponent)
        return str(exponent)
    
    @staticmethod 
    def _get_units_by_factor(factor: float, dims: Dimensions, units_env: dict) -> dict:
        """
        Returns a units_dict from the environment instance if the numerical
        value of 'factor' is a match for a derived unit defined in the
        environment instance and the dimensions stored in the units_dict are
        equal to 'dims'. Returns an empty dict, otherwise.
        """
        units_match = units_env.get(factor, False)
        if units_match:
            units_name = tuple(units_match.keys())[0]
            if units_name:
                units_dims = units_match[units_name].get("Dimension", False)
                if units_dims and (dims == units_dims):
                    return units_match[units_name]
                else: return dict()
            else: return dict()
        else: return dict()
                  
    @staticmethod   
    def _get_derived_unit(dimensions: Dimensions, units_env: dict) -> dict:
        """
        TODO!!!
        """
        powers_of_derived = Physical._powers_of_derived(dimensions, units_env)
        if powers_of_derived:
            dimensions = Physical._dims_original(dimensions, units_env)
        possible_units = units_env['derived']
                  
        if possible_units:
            return possible_units.get(dimensions)
        else:
            return {}              
    
    @staticmethod              
    def _get_unit_string(prefix: str, unit_components: list, repr_format: str) -> str:
        """
        Part of the __str__ and __repr__ process. Returns a string representing 
        the SI unit components of the Physical instance extracted from the list of
        tuples, 'unit_components', using 'repr_format' as given by the _repr_x_
        function it was called by. If 'repr_format' is not given, then terminal
        output is assumed.
        """
        dot_operator = "⋅"
        pre_super = ""
        post_super = ""
        pre_symbol = ""
        post_symbol = ""
        if repr_format == "html":
            dot_operator = "&#8901;"
            pre_super = "<sup>"
            post_super = "</sup>"
        elif repr_format == "latex":
            dot_operator = r" \cdot "
            pre_symbol = "\\text{"
            post_symbol = "}"
            pre_super = "^{"
            post_super = "}"

        str_components = []
        for symbol, exponent in unit_components:
            if exponent == 1:
                this_component = f"{pre_symbol}{prefix}{symbol}{post_symbol}"
            else:
                this_component = f"{pre_symbol}{prefix}{symbol}{post_symbol}"\
                                 f"{pre_super}{exponent}{post_super}"
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
    
    @staticmethod              
    def _get_unit_components_from_dims(dims: Dimensions):
        """
        Returns a list of tuples to represent the current units based 
        on the current dimensions. Dimension ignored if 0.
        e.g. [('kg', 1), ('m', -1), ('s', -2)]
        """
        unit_components = []
        unit_symbols = dims._fields
        for idx, dim in enumerate(dims):
            if dim: #int
                unit_tuple = (unit_symbols[idx], dim)
                unit_components.append(unit_tuple)
        return unit_components
                  
                
    ### Mathematical helper functions ###

    @staticmethod
    def _dims_quotient(dimensions: Dimensions, units_env: dict) -> Optional[Dimensions]:
        """
        Returns a Dimensions object representing the element-wise quotient betwe
        'dimensions' and a defined unit if 'dimensions' is a scalar multiple
        of a defined unit in the global environment variable.
        Returns None otherwise.
        """
        derived = units_env["derived"]
        defined = units_env["defined"]
        all_units = ChainMap(derived, defined)
        for dimension_key in all_units.keys():
            if vec.multiply(dimension_key, vec.dot(dimensions,dimensions)) == \
               vec.multiply(dimensions, vec.dot(dimensions, dimension_key)):
                quotient = vec.divide(dimensions,dimension_key, ignore_zeros = True)
                return quotient
        return None     
    
    @staticmethod
    def _dims_basis_multiple(dims: Dimensions) -> Optional[Dimensions]:
        """
        TODO!!!
        Returns a Dimensions object if 'dimensions' is a scalar multiple of one of the basis
        vectors (e.g. [3,0,0,0,0,0,0] is a scalar multiple of [1,0,0,0,0,0,0]).
        Returns None, otherwise.
        """
        count = 0
        for dim in dims:
            if dim:
                count +=1
            if count > 1:
                return None
        return dims
                  
    @staticmethod
    def _dims_original(dimensions: Dimensions, units_env: dict) -> Dimensions:
        """
        Returns a dimensions array that represents the base dimensions of a unit, 
        in the event that the Physical is a unit to a power.
        e.g. A Newton, N, would have dimensions [1,1,-2,0,0,0,0] but N**2 would have
        dimensions [2,2,-4,0,0,0,0]. 
        Physical._dims_original(Dimensions(2,2,-4,0,0,0,0) would return ->
        Dimensions(1,1,-2,0,0,0,0) because that would be the original dimensions
        of N**2.
        """
        quotient = Physical._dims_quotient(dimensions, units_env)
        if quotient is not None:
            orig_dims = vec.divide(dimensions, quotient, ignore_zeros = True)
            return orig_dims
        else:
            return dimensions
                             
    @staticmethod
    def _powers_of_derived(dims: Dimensions, units_env: dict) -> Union[int, float]:
        """
        Returns an integer value that represents the exponent of a unit if the dimensions
        array is a multiple of one of the defined derived units in dimension_keys. Returns None,
        otherwise.
        e.g. a force would have dimensions = [1,1,-2,0,0,0,0] so a Physical object
        that had dimensions = [2,2,-4,0,0,0,0] would really be a force to the power of 2.
        The function returns the 2.
        """
        quotient_1 = Physical._dims_quotient(dims, units_env)
        quotient_2 = Physical._dims_basis_multiple(dims)
        if quotient_1 is not None:
            power_of_derived = vec.mean(quotient_1, ignore_empty=True)
            return power_of_derived
        elif quotient_2 is not None:
            power_of_basis = vec.mean(quotient_2, ignore_empty=True)
            return power_of_basis
       
    @staticmethod              
    def _auto_value(value: float, dims: Dimensions, factor: float, units_env: dict) -> float:
        """
        Returns the value to be displayed in __str__(). This value represents the value
        of the Physical in whatever dimension in whatever units it is intended to be in
        based on its .factor.
        """
        powers_of_derived = Physical._powers_of_derived(dims, units_env)
        if not powers_of_derived:
            powers_of_derived = 1
        return value * factor ** powers_of_derived
    
    @staticmethod
    def _auto_prefix(value: float, dims: Dimensions, units_env: dict) -> str:
        """
        Returns a string "prefix" of an appropriate value if self.value should be prefixed
        i.e. it is a big enough number (e.g. 5342 >= 1000; returns "k" for "kilo")
        """      
        prefixes = Physical._prefixes
        powers_of_derived = Physical._powers_of_derived(dims, units_env)
        if not powers_of_derived:
            powers_of_derived = 1
        if abs(value) >= 1:
            for prefix, power in prefixes.items():
                if abs(value) >= power ** powers_of_derived:                    
                    return prefix
        else:
            reverse_prefixes = sorted(prefixes.items(), key = lambda prefix: prefix[0])
            previous_prefix = reverse_prefixes[0][0] # Gets the smallest prefix to start
            for prefix, factor in reversed(list(prefixes.items())):
                if abs(value) < factor ** powers_of_derived:
                    return previous_prefix
                else:                     
                    previous_prefix = prefix
                  
    @staticmethod        
    def _auto_prefix_kg(value: float, dims: Dimensions, units_env: dict) -> str:
        """
        Just like _auto_prefix but handles the one special case for "kg" because it already
        has a prefix of "k" as an SI base unit
        """     
        prefixes = Physical._prefixes
        powers_of_derived = Physical._powers_of_derived(dims, units_env)
        for prefix, power in prefixes.items():
            if abs(value) >= power/1000:                    
                return prefix
    
    @staticmethod
    def _auto_prefix_value(value: float, dims: Dimensions, factor: float, units_env: dict) -> float:
        """
        Converts the value to a prefixed value if the instance has a symbol defined in 
        the environment (i.e. is in the defined units dict)
        """
        prefixes = Physical._prefixes
        powers_of_derived = Physical._powers_of_derived(dims, units_env)
        factored = value * factor
        if not powers_of_derived:
            powers_of_derived = 1
        if abs(factored) >= 1:
            for prefix, power in prefixes.items():
                if abs(factored) >= power ** powers_of_derived:
                    return factored / (power ** powers_of_derived)
        else:
            reverse_prefixes = sorted(prefixes.items(), key = lambda pre_fact: pre_fact[1])
            previous_power = reverse_prefixes[0][1] # Gets the smallest factor to start
            for prefix, power in reversed(list(prefixes.items())):
                if abs(factored) < power ** powers_of_derived:
                    return factored / (previous_power ** powers_of_derived)
                else:                     
                    previous_power = power
                    
    ### "Magic" Methods ###
                  
    def __hash__(self):
        return hash((self.value, self.dimensions, self.symbol, self.factor))
                  
    def __round__(self, precision=0):
        self._precision = precision
        return self
                  
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
            other = other * self.factor
            return self.__class__(self.value + other, self.dimensions, self.symbol)        
        else:
            try:
                return self.__class__(self.value + other.value, self.dimensions, self.symbol, factor = self.factor)
            except:
                raise NotImplementedError("Cannot add between {} and {}".format(self.components(), other.components()))
    
    def __radd__(self, other):
        return self.__add__(other)
            
    def __iadd__(self, other):
        self = self + other
        return self
        
    def __sub__(self, other):
        if isinstance(other, number):
            other = other * self.factor
            return self.__class__(self.value - other, self.dimensions)
        else:
            try:
                return self.__class__(self.value - other.value, self.dimensions, self.symbol, factor=self.factor)
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
            return self.__class__(new_value, self.dimensions, factor=self.factor)
        else:
            try:
                new_dimensions = vec.add(self.dimensions, other.dimensions)
                new_value = self.value * other.value
                if new_dimensions == Dimensions(0,0,0,0,0,0,0):
                    return new_value
                else:
                    return Physical(new_value, new_dimensions, factor = self.factor*other.factor)
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
            return Physical(new_value, self.dimensions, factor = self.factor)
        else:
            try: 
                new_dimensions = vec.subtract(self.dimensions, other.dimensions)
                new_value = self.value / other.value
                if new_dimensions == Dimensions(0,0,0,0,0,0,0):
                    return new_value
                else:
                    return Physical(new_value, new_dimensions, factor = self.factor/other.factor)
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
            new_factor = self.factor
            return Physical(new_value, new_dimensions, self.symbol, factor = new_factor)
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
    derived = dict()
    defined = dict()
    units_by_dimension = {"derived": derived, "defined": defined}
    units_by_factor = {}
    
    def __init__(self, physical_class):
        self._physical_class = physical_class
    
    def __call__(self, env_name: str):
        self.environment = self.load_environment(env_name)                          
        for name, definition in self.environment.items():
            factor = definition.get("Factor", 1)
            dimension = definition.get("Dimension")
            value = definition.get("Value", 1)
            if factor == 1 and value == 1:
                self.units_by_dimension["derived"].setdefault(dimension, dict()).update({name: definition})
            elif factor != 1:
                self.units_by_dimension["defined"].setdefault(dimension, dict()).update({name: definition}) 
                self.units_by_factor.update({factor: {name: definition}})
        
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
                to_globals.update({unit: physical_class(1/factor, dimensions, factor=factor)})
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