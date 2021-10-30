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
import sys
from types import ModuleType
from forallpeople.dimensions import Dimensions


class Environment:
    """
    A class that contains information about the units definitions that will be used
    by each Physical instance. Each Physical instance requests units definition
    information from the single Environment instance (OMG! Singleton!)
    """

    environment = {}

    def __init__(
        self, physical_class: type, builtins_module: ModuleType, si_base_units: dict
    ):
        self._units_by_dimension = {"derived": dict(), "defined": dict()}
        self._units_by_factor = dict()
        self._physical_class = physical_class
        self._builtins_module = builtins_module
        self._si_base_units = si_base_units
        self.this_module = sys.modules["forallpeople"]
        self.push_module = None
        if not self.environment:
            self.environment = self._si_base_units

    @property
    def units_by_dimension(self):
        def return_dict():
            return self._units_by_dimension
        return return_dict

    @property
    def units_by_factor(self):
        def return_dict():
            return self._units_by_factor
        return return_dict

    def __call__(self, env_name: str = "", top_level: bool = False):
        if not env_name:
            try:
                print(
                        self._generate_units_dict(
                            self.environment, self._physical_class
                        ), "\n", self._si_base_units),
                    
            except TypeError:
                print(self.environment)
            return

        push_module = self.this_module
        if top_level:
            push_module = self._builtins_module

        if self.environment != self._si_base_units and self.push_module:
            old_units_dict = self._generate_units_dict(
                self.environment, self._physical_class
            )

            self.del_vars(old_units_dict, self.push_module)

        self.environment = self._load_environment(env_name)
        new_units_dict = self._generate_units_dict(
            self.environment, self._physical_class
        )
        self.push_vars(new_units_dict, push_module)
        self.push_vars(self._si_base_units, push_module)

        # Update internal class dictionaries: self.units_by_dimension, self.units_by_factor
        self._units_by_dimension = {"derived": dict(), "defined": dict()}
        self._units_by_factor = dict()
        for name, definition in self.environment.items():
            factor = round(
                definition.get("Factor", 1), self._physical_class._total_precision
            )
            dimension = definition.get("Dimension")
            value = definition.get("Value", 1)
            if factor == 1 and value == 1:
                self._units_by_dimension["derived"].setdefault(dimension, dict()).update(
                    {name: definition}
                )
            elif factor != 1:
                self._units_by_dimension["defined"].setdefault(dimension, dict()).update(
                    {name: definition}
                )
                self._units_by_factor.update({factor: {name: definition}})
        self.push_module = push_module  # Update previous push_module; could be either module or top-level

    
    def push_vars(self, units_dict: dict, module: ModuleType) -> None:
        module.__dict__.update(units_dict)

    def del_vars(self, units_dict: dict, module: ModuleType) -> None:
        for key in units_dict.keys():
            module.__dict__.pop(key)

    def _load_environment(self, env_name: str):
        """
        Returns a dict that describes a set of unit definitions as contained in the
        JSON file titled "'env_name'.json". Alternatively, 'env_name' can
        also be a path to a JSON file outside forallpeople.
        After the 'Dimension' definition is converted to an Dimensions
        object and any factors are checked for safety then evaluated.
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
        if pathlib.Path(env_name).exists():
            file_path = pathlib.Path(env_name)
        else:
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
        units_dict = {}
        # Transfer definitions
        for unit, definitions in environment.items():
            dimensions = definitions["Dimension"]
            factor = definitions.get("Factor", 1)
            symbol = definitions.get("Symbol", "")
            value = definitions.get("Value", 1)
            if symbol:
                units_dict.update(
                    {unit: physical_class(1 / factor, dimensions, factor)}
                )
            else:
                units_dict.update({unit: physical_class(value, dimensions, factor)})
        return units_dict


