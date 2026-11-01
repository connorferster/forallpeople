---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# Getting started

## Installation

```bash
pip install forallpeople
```

forallpeople is pure Python and has no dependencies.

## The SI base units

Import forallpeople, conventionally as `si`:

```{code-cell} ipython3
import forallpeople as si
```

The seven SI base units are now available as variables: `si.kg`, `si.m`,
`si.s`, `si.A`, `si.cd`, `si.K` and `si.mol`. Multiply a number by a unit to
make a physical quantity: an instance of {class}`~forallpeople.Physical`.

```{code-cell} ipython3
mass = 3500 * si.kg
g = 9.81 * si.m / si.s**2
mass * g
```

With only the base units loaded, the force is shown in base units. Notice also
that `3500 kg` would be shown as `3.500 Mg`: quantities are
{doc}`scaled to a prefix <guide/display>` automatically.

## Loading an environment

An **environment** is a set of unit definitions. Loading one does two things:

1. It adds its units as variables (`si.N`, `si.kPa`, `si.ft`, ...).
2. It changes how results are displayed. A quantity whose dimensions match a
   unit in the environment is shown in that unit.

```{code-cell} ipython3
si.environment("default")   # the SI derived units: N, Pa, J, W, ...
force = mass * g
force
```

The quantity hasn't changed: it is still stored in SI base units. Only its
display has.

```{code-cell} ipython3
force.value   # always in SI base units
```

forallpeople bundles several environments. `structural` has the units of
structural engineering, in SI and US customary units:

```{code-cell} ipython3
si.environment("structural")

P = 12 * si.kip
L = 18 * si.ft
P * L / 4
```

See {doc}`guide/environments` for the bundled environments, and
{doc}`guide/custom-environments` to write your own.

## Top-level units

Typing `si.` in front of every unit is precise, but in a notebook or REPL it
gets in the way. Load the environment with `top_level=True` to put the units
into the top-level namespace instead:

```{code-cell} ipython3
si.environment("default", top_level=True)

mass = 5.25 * kg
mass * 9.81 * m / s**2
```

```{warning}
`top_level=True` writes the units into Python's builtins, where they are
visible from every module. Short names like `m`, `s` and `A` are easy to
overwrite by accident (`for m in members: ...`). Use it for interactive work,
and use `si.` in modules.
```

## In Jupyter

`Physical` instances have HTML and LaTeX representations, so in Jupyter they
display with proper superscripts and symbols. They work as values in pandas
DataFrames and numpy arrays, and they render in
[handcalcs](https://github.com/connorferster/handcalcs).

## Next steps

- {doc}`guide/quantities`: what arithmetic does with units.
- {doc}`guide/display`: prefixes, precision and string formatting.
- {doc}`guide/environments`: the bundled environments and unit conversion.
