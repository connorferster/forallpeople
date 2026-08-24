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

import ast
from fractions import Fraction
from operator import add, sub, mul, truediv, pow
import pathlib
import json
import sys
from typing import Union
from types import ModuleType
from forallpeople.dimensions import Dimensions, DimensionError


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
                    self._generate_units_dict(self.environment, self._physical_class),
                    "\n",
                    self._si_base_units,
                ),

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
        self._push_vars(new_units_dict, push_module)
        self._push_vars(self._si_base_units, push_module)

        # Update internal class dictionaries: self.units_by_dimension, self.units_by_factor
        self._units_by_dimension = {"derived": dict(), "defined": dict()}
        self._units_by_factor = dict()
        for name, definition in self.environment.items():
            factor = definition.get("Factor", 1)
            dimension = definition.get("Dimension")
            value = definition.get("Value", 1)
            if factor == 1 and value == 1:
                self._units_by_dimension["derived"].setdefault(
                    dimension, dict()
                ).update({name: definition})
            elif factor != 1:
                self._units_by_dimension["defined"].setdefault(
                    dimension, dict()
                ).update({name: definition})
                # Accumulate rather than overwrite: multiple units can share
                # the same factor value with different dimensions (e.g. kN and
                # mT both have factor 0.001).  Overwriting silently discards
                # all but the last-loaded unit from the factor index.
                if factor in self._units_by_factor:
                    self._units_by_factor[factor][name] = definition
                else:
                    self._units_by_factor[factor] = {name: definition}
        self.push_module = push_module  # Update previous push_module; could be either module or top-level

    def _push_vars(self, units_dict: dict, module: ModuleType) -> None:
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
            "Unit definition for '{unit}' in '{env_name}.json': Factor "
            "must be an arithmetic expr (as a str), a float, "
            "or an int: not '{factor}'."
        )
        file_path = pathlib.Path(__file__).parent / "environments" / f"{env_name}.json"

        if not file_path.exists():
            raise ValueError(
                "The environment name, {env_name}, does not exist in the installed environments."
            )

        with open(file_path, "r", encoding="utf-8") as json_unit_definitions:
            units_environment = json.load(json_unit_definitions)

        # Load definitions
        for unit, definitions in units_environment.items():
            dimensions = definitions.get("Dimension", ())
            factor_expr = definitions.get("Factor", "1")
            symbol = definitions.get("Symbol", "")
            if not dimensions:
                raise DimensionError(
                    dim_array_not_defn.format(env_name=env_name, unit=unit)
                )
            else:
                units_environment[unit]["Dimension"] = Dimensions(*dimensions)

            try:
                units_environment[unit]["Factor"] = evaluate_factor_expression(
                    factor_expr
                )
            except (ValueError, SyntaxError, ZeroDivisionError):
                raise ValueError(
                    unit_factor_not_eval.format(
                        unit=unit, env_name=env_name, factor=factor_expr
                    )
                )
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
                    {unit: physical_class(1 / float(factor), dimensions, factor)}
                )
            else:
                units_dict.update({unit: physical_class(value, dimensions, factor)})
        return units_dict


_FACTOR_BINOPS = {
    ast.Add: add,
    ast.Sub: sub,
    ast.Mult: mul,
    ast.Div: truediv,
    ast.Pow: pow,
}


def _evaluate_factor_node(node: ast.AST) -> Union[int, Fraction]:
    """
    Recursively evaluates a node of a parsed factor expression over Fraction.

    Only numeric literals, parentheses (implicit in the parse tree), unary
    +/- and the binary operators + - * / ** are permitted. Every other node
    type -- names, calls, attribute access, comparisons, subscripts -- raises
    ValueError, so an environment .json cannot smuggle in executable code.
    """
    if isinstance(node, ast.Expression):
        return _evaluate_factor_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError(
                f"Factor expressions may only contain numbers: got {node.value!r}"
            )
        # via str() so that a decimal literal becomes its exact Fraction
        # (0.3048 -> 381/1250) rather than the binary float approximation.
        return Fraction(str(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _evaluate_factor_node(node.operand)
        return operand if isinstance(node.op, ast.UAdd) else -operand
    if isinstance(node, ast.BinOp) and type(node.op) in _FACTOR_BINOPS:
        left = _evaluate_factor_node(node.left)
        right = _evaluate_factor_node(node.right)
        return _FACTOR_BINOPS[type(node.op)](left, right)
    raise ValueError(
        f"Not a permitted operation in a Factor expression: {type(node).__name__}"
    )


def evaluate_factor_expression(
    factor_expression: Union[str, int, float],
) -> Union[int, Fraction]:
    """
    Returns the evaluated result of 'factor_expression', an arithmetic
    expression given as a str (a plain int or float is also accepted).

    The expression is parsed with Python's own grammar and evaluated over
    Fraction, so operator precedence, parentheses and scientific notation are
    all honoured and the result is exact. Only numeric literals and the
    operators + - * / ** (and unary +/-) are permitted.
    """
    if isinstance(factor_expression, (int, float)) and not isinstance(
        factor_expression, bool
    ):
        return Fraction(str(factor_expression))
    parsed = ast.parse(str(factor_expression).strip(), mode="eval")
    return _evaluate_factor_node(parsed)
