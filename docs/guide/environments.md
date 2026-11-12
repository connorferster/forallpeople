---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# Environments

An **environment** is a set of unit definitions, stored as a JSON file. One
environment is active at a time. Loading it:

1. **adds its units as variables**, e.g. `si.kN`, `si.ft`, `si.psf`, and
2. **sets how quantities are displayed**: a quantity whose dimensions (and
   factor) match a unit in the environment is shown in that unit.

The SI base units are always available, whatever environment is loaded.

```{code-cell} ipython3
import forallpeople as si

force = 3500 * si.kg * 9.81 * si.m / si.s**2
force
```

```{code-cell} ipython3
si.environment("default")
force
```

The quantity is the same in both cells. Think of the environment as a lens:
it changes how quantities look, never what they are.

## Loading an environment

```python
si.environment("structural")                  # a bundled environment, by name
si.environment("path/to/my_units.json")       # your own environment file
si.environment("structural", top_level=True)  # units as top-level variables
```

A name is looked up among the bundled environments first. A `pathlib.Path`,
or a string ending in `.json`, is always treated as a file path. Loading a new
environment removes the variables of the previous one.

Call `si.environment()` with no arguments to print the units that are loaded:

```{code-cell} ipython3
si.environment()
```

## Bundled environments

`default`, `structural`, `us_structural`, `us_customary`, `electrical` and
`thermal` are bundled
with forallpeople. The tables list each unit's variable name, how it is
displayed, its dimensions, and its definition as written in the environment
file (see {doc}`custom-environments` for what `Value` and `Factor` mean).

::::{tab-set}

:::{tab-item} default
```{include} ../_generated/environment-default.md
```
:::

:::{tab-item} structural
```{include} ../_generated/environment-structural.md
```
:::

:::{tab-item} us_structural
```{include} ../_generated/environment-us_structural.md
```
:::

:::{tab-item} us_customary
```{include} ../_generated/environment-us_customary.md
```
:::

:::{tab-item} electrical
```{include} ../_generated/environment-electrical.md
```
:::

:::{tab-item} thermal
```{include} ../_generated/environment-thermal.md
```
:::

::::

The package also contains `test_definitions`, which is used by the test suite.

## Working in US customary units

A non-SI unit is an SI unit with a **factor**. A foot is a metre with a factor
of `1/0.3048`. The value is still stored in SI units:

```{code-cell} ipython3
si.environment("structural")

L = 12 * si.ft
L, L.value, L.factor
```

Factors carry through calculations. A result is displayed in a defined unit
when its dimensions and factor both match one:

```{code-cell} ipython3
w = 0.8 * si.kip / si.ft
w * L**2 / 8
```

### Mixing unit systems

When quantities in two unit systems are added, the result takes the units of
the left-hand quantity:

```{code-cell} ipython3
5 * si.kN + 2 * si.kip, 2 * si.kip + 5 * si.kN
```

### When no defined unit matches

If a calculation produces a factor that no unit in the environment has, the
result is displayed in SI units of the same dimensions:

```{code-cell} ipython3
5 * si.kip / (2 * si.m), 2 * si.kip * si.ft * si.ft
```

Convert such results with `.to()` or `.si()` (below), or use an environment
with `Default` units, such as `us_structural`.

### The `us_structural` environment

`us_structural` is for calculations entirely in US customary units. It
defines `lb` and `kip` with `inch` (shown as `in`) and `ft` in every
combination of a force times, or over, a length to the first to fourth power:
moments (`kip·ft`), `kip·in²`, `lb·in³`, line loads (`kip/ft`), pressures
(`psi`, `ksf`), densities (`pcf`, `kci`) and `kip/in⁴`, so intermediate values
are shown in a unit you would write.

Each dimension has a `Default` unit (see {doc}`custom-environments`), used
when units are mixed so that no defined unit matches, e.g. ksi and psi:

```{code-cell} ipython3
si.environment("us_structural")

A_s = 2.37 * si.inch**2
f_y = 60 * si.ksi
f_c = 4000 * si.psi
b = 12 * si.inch
a = A_s * f_y / (0.85 * f_c * b)
a, 2 * si.ft * (6 * si.inch)
```

Without the default, `a` would be shown in millimetres. The defaults are `in`,
`kip`, `kip·ft`, `kip·in²`, `kip·in³`, `kip·in⁴`, `kip/ft`, `ksi`, `pcf` and
`kip/in⁴`.

```{code-cell} ipython3
si.environment("structural")
```

## Converting units

{meth}`~forallpeople.Physical.to` returns the quantity in another unit of the
same dimensions in the environment:

```{code-cell} ipython3
L.to("inch")
```

Call it with no arguments to list the units it can convert to:

```{code-cell} ipython3
L.to()
```

{meth}`~forallpeople.Physical.si` returns the quantity in SI units:

```{code-cell} ipython3
L.si(), (40 * si.psf).si()
```

## How the display unit is chosen

For each quantity, forallpeople looks in the environment for units with the
same dimensions, then:

1. If one of them also has the same factor, it is a **defined** unit (such as
   `ft` or `psf`), and it is used.
2. If none has the same factor, but the factor is not 1, the unit marked as
   the `Default` for those dimensions is used, if there is one.
3. Otherwise, the SI unit of those dimensions (a unit with no factor, such as
   `Pa`) is used, with an automatic prefix.
4. If no unit has the same dimensions, the quantity is shown as a product of
   SI base units, e.g. `kg·m⁻¹·s⁻²`.

Dimensions are matched exactly, so a unit is only recognised for the
dimensions it is defined with. Units such as `kN·m` (a moment) and `J` (an
energy) have the same dimensions, so an environment should define only the one
that the quantities in it mean (see {doc}`../background`).

Powers of a unit in the environment are recognised too:

```{code-cell} ipython3
(4 * si.ft)**2, (4 * si.ft)**3, 5 * si.kN * si.m * si.m
```
