---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# forallpeople

**The world's units at your fingertips.**

> *"For all people. For all time."*
> Nicolas de Caritat (Marquis de Condorcet), on the creation of the metric
> (SI) system.

forallpeople is a Python library for units-aware calculations in the SI unit
system, and in the unit systems that are defined from it, such as US customary
units. Units are ordinary Python variables: multiply a number by a unit to make
a physical quantity.

```{code-cell} ipython3
import forallpeople as si
si.environment("structural")

span = 6 * si.m
w = 4.5 * si.kN / si.m
M = w * span**2 / 8
M
```

- **Units reduce as you calculate.** `kN/m × m²` is `kN·m`, with no
  `.to()` call needed.
- **Quantities display the way you would write them by hand:** `20.250 kN·m`,
  not `20250.0 kilogram * meter ** 2 / second ** 2`. Results are scaled to a
  prefix automatically (`5000 m` is `5.000 km`).
- **Units cancel to plain numbers.** `4.2 m / 0.25 m` is the float `16.8`, so
  trigonometry and other maths just work.
- **Environments decide which units you see.** Load a bundled environment
  (SI derived units, structural engineering, US customary, ...) or write your
  own as a JSON file.
- **Read and write quantities as text:** parse `"350 MPa"` from YAML or JSON
  data, and save quantities to JSON exactly.
- **Works with Jupyter**, numpy, pandas and
  [handcalcs](https://github.com/connorferster/handcalcs), with HTML and LaTeX
  output.

forallpeople was released on [PyPI](https://pypi.org/project/forallpeople/) on
World Metrology Day, 20 May 2019: the day the new definition of the kilogram
came into force.

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} Getting started
:link: getting-started
:link-type: doc
Install forallpeople and make your first quantities.
:::

:::{grid-item-card} Environments
:link: guide/environments
:link-type: doc
Choose which units are available, and how results are displayed.
:::

:::{grid-item-card} Units in data files
:link: guide/parsing
:link-type: doc
Parse quantities from text, and save them to JSON.
:::

:::{grid-item-card} API reference
:link: api/index
:link-type: doc
`Physical`, `environment`, parsing and serialization.
:::
::::

```{toctree}
:hidden:
:caption: Guide

getting-started
guide/quantities
guide/display
guide/environments
guide/custom-environments
```

```{toctree}
:hidden:
:caption: Working with other tools

guide/parsing
guide/json
guide/ymprint
guide/numpy
guide/empirical
```

```{toctree}
:hidden:
:caption: Reference

background
api/index
```
