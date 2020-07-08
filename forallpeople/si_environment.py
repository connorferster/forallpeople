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


import pathlib
import json
import re
from types import ModuleType
from forallpeople.dimensions import Dimensions

# from forallpeople.physical import Physical

# _the_si_base_units = {
#     "kg": Physical(1, Dimensions(1, 0, 0, 0, 0, 0, 0), 1.0),
#     "m": Physical(1, Dimensions(0, 1, 0, 0, 0, 0, 0), 1.0),
#     "s": Physical(1, Dimensions(0, 0, 1, 0, 0, 0, 0), 1.0),
#     "A": Physical(1, Dimensions(0, 0, 0, 1, 0, 0, 0), 1.0),
#     "cd": Physical(1, Dimensions(0, 0, 0, 0, 1, 0, 0), 1.0),
#     "K": Physical(1, Dimensions(0, 0, 0, 0, 0, 1, 0), 1.0),
#     "mol": Physical(1, Dimensions(0, 0, 0, 0, 0, 0, 1), 1.0),
# }


class Environment:
    """
    A class that contains information about the units definitions that will be used
    by each Physical instance. Each Physical instance requests units definition
    information from the single Environment instance (OMG! Singleton!)
    """

    environment = {}
    units_by_dimension = {"derived": dict(), "defined": dict()}
    units_by_factor = dict()
    unit_vars = {}

    def __init__(self, physical_class, builtins_module, si_base_units):
        self._physical_class = physical_class
        self._builtins_module = builtins_module
        self._si_base_units = si_base_units
        self.python_builtins = {
            name: getattr(builtins_module, name) for name in dir(builtins_module)
        }
        if not self.environment:
            self.environment = self._si_base_units

    def __call__(self, env_name: str = ""):
        if not env_name:
            print(self.environment)
            return
        self.environment = self._load_environment(env_name)
        for name, definition in self.environment.items():
            factor = round(
                definition.get("Factor", 1), self._physical_class._total_precision
            )
            dimension = definition.get("Dimension")
            value = definition.get("Value", 1)
            if factor == 1 and value == 1:
                self.units_by_dimension["derived"].setdefault(dimension, dict()).update(
                    {name: definition}
                )
            elif factor != 1:
                self.units_by_dimension["defined"].setdefault(dimension, dict()).update(
                    {name: definition}
                )
                self.units_by_factor.update({factor: {name: definition}})

        return self.push_units_into_user_namespace(
            self._generate_units_dict(self.environment, self._physical_class)
        )

    def _load_environment(self, env_name: str):
        """
        Returns a dict that describes a set of unit definitions as contained in the
        JSON file titled "'env_name'.json" after the 'Dimension' definition is converted to
        an Dimensions object and any factors are checked for safety then evaluated.
        Raises error if file not found.
        """
        dim_array_not_defn = (
            "Dimension array not defined in environment"
            " .json file, '{env_name}.json', for unit '{unit}'"
        )
        unit_factor_not_eval = (
            "Unit definition in '{env_name}.json': Factor"
            "must be an arithmetic expr (as a str), a float,"
            "or an int: not '{factor}'."
        )

        path = pathlib.Path(__file__).parent
        filename = env_name + ".json"
        file_path = path / filename
        with open(file_path, "r", encoding="utf-8") as json_unit_definitions:
            units_environment = json.load(json_unit_definitions)

        # Load definitions
        arithmetic_expr = re.compile(r"[0-9.*/+-]")
        for unit, definitions in units_environment.items():
            dimensions = definitions.get("Dimension", ())
            factor = definitions.get("Factor", "1")
            symbol = definitions.get("Symbol", "")
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

    @staticmethod
    def _generate_units_dict(environment: dict, physical_class):
        """
        Returns None; updates the globals dict with the units defined in the "definitions"
        portion of the environment dict. This is the method that instantiates all of the
        unit symbols defined in the environment json file.
        """
        to_globals = {}
        # Transfer definitions
        for unit, definitions in environment.items():
            dimensions = definitions["Dimension"]
            factor = definitions.get("Factor", 1)
            symbol = definitions.get("Symbol", "")
            value = definitions.get("Value", 1)
            if symbol:
                to_globals.update(
                    {unit: physical_class(1 / factor, dimensions, factor)}
                )
            else:
                to_globals.update({unit: physical_class(value, dimensions, factor)})
        Environment.unit_vars = to_globals
        return to_globals

    def push_units_into_user_namespace(self, units_dict: dict) -> None:
        """
        Returns None. For every item in 'unit_dict' add that item to the 
        builtins module in order dynamically instantiate the units in the dict
        to make them available to the user in the top-level namespace.
        Cleans out the existing builtins attrs prior to pushing new values to
        prevent polluting the namespace.
        """
        the_si_base_units = self._si_base_units
        builtins_module = self._builtins_module

        # First the clean
        current_builtins = {
            name: getattr(builtins_module, name) for name in dir(builtins_module)
        }
        for old_var_name, old_physical in current_builtins.items():
            if (
                old_var_name not in self.python_builtins
                and old_var_name not in the_si_base_units
            ):
                delattr(builtins_module, old_var_name)

        # Then the push
        for var_name, physical in units_dict.items():
            setattr(builtins_module, var_name, physical)

