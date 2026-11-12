---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# How quantities are displayed

```{code-cell} ipython3
import forallpeople as si
si.environment("default")
```

forallpeople shows a quantity the way you would write it in a calculation:
in the units of the environment, scaled to a sensible prefix, to three decimal
places.

## Automatic prefixes

SI quantities are scaled to the prefix that keeps the number between 1 and
1000:

```{code-cell} ipython3
5000 * si.kg
```

```{code-cell} ipython3
4_000_000_000 / si.s
```

```{code-cell} ipython3
0.000000112 * si.m
```

Prefixes are applied to:

1. the SI base units (`m`, `kg`, `s`, `A`, `cd`, `K`, `mol`), and
2. SI units defined in the environment (units with no factor, such as `N`
   and `Pa`).

They are not applied to:

1. compound units that the environment does not define (a `kkg·A` would not
   make sense), and
2. non-SI units (units with a factor, such as `lbf`: there is no `klbf`).

```{code-cell} ipython3
40000 * si.A * si.kg
```

When a prefixed unit is raised to a power, the prefix is raised with it. That
is why this area stays in `km²`: a `Mm²` is a million `km²`.

```{code-cell} ipython3
distance = 500_000 * si.m
distance, distance**2
```

### Choosing the prefix

{meth}`~forallpeople.Physical.prefix` sets the prefix of a quantity. Use
`"unity"` for no prefix:

```{code-cell} ipython3
force = 34_335 * si.N
force, force.prefix("M"), force.prefix("unity")
```

Only SI quantities have prefixes: `.prefix()` raises an error on a quantity
in a non-SI unit.

## Precision

Three decimal places are shown by default. Use Python's `round()` to change
the precision of a quantity. It changes only the display: the value is not
rounded.

```{code-cell} ipython3
a = 4230.2349329 * si.kg
a, round(a, 6)
```

Be careful with quantities that cannot be prefixed. A very small value in an
undefined compound unit can show as `0.000`:

```{code-cell} ipython3
c = 1 / (4_000_000 * si.kg * si.A)
c, round(c, 9)
```

## String formatting

Quantities accept Python's format specifications. The units are added after
the number:

```{code-cell} ipython3
force = 322.6573 * si.N
f"{force:.1f}", f"{force:.4e}"
```

Add `H` for HTML or `L` for LaTeX:

```{code-cell} ipython3
f"{force:.2eH}", f"{force:.2eL}"
```

The `.html` and `.latex` properties give the same representations at the
quantity's own precision. Jupyter uses them automatically.

```{code-cell} ipython3
force.latex
```

## `float()` gives the number you see

`float()` returns the number **as it is displayed**, in the displayed prefix
and unit. `.value` is always in SI base units.

```{code-cell} ipython3
a = 5_523_400 * si.N
a, float(a), a.value
```

So `float()` depends on the magnitude: `float(30.2 * kN)` is `30.2` but
`float(0.5 * kN)` is `500.0`, because `0.5 kN` displays as `500.000 N`. Use
`.value` when you need a number that does not depend on the display.

Functions in Python's `math` module call `float()` on their argument, so they
work on the displayed number too:

```{code-cell} ipython3
import math

length = 4200 * si.m   # displays as 4.200 km
math.sqrt(length)      # the square root of 4.2
```

This is deliberate: it makes empirical formulas easy to write (see
{doc}`empirical`). To take the square root of the quantity itself, use
`.sqrt()`, or {meth}`~forallpeople.Physical.split` to work on the SI value:

```{code-cell} ipython3
value, unit = length.split()
math.sqrt(value) * unit
```

## Reading the display in code

{meth}`~forallpeople.Physical.display` returns what is shown as a
{class}`~forallpeople.Display`: the number (`magnitude`), the unit (`unit`) and
the `factor` from the SI value to the number (`magnitude == value * factor`).
The factor includes the prefix and is an exact `Fraction`, so code that
writes the quantity elsewhere (a spreadsheet, a report) does not have to parse
the string:

```{code-cell} ipython3
length.display(), (3 * si.m**2).display("latex")
```

## `repr()` and `str()`

forallpeople puts conventions before Python's: both `repr()` and `str()` give
the readable form, so quantities display well in the REPL, in Jupyter, and
inside lists, dicts, arrays and DataFrames. For the machine-readable form, use
the `.repr` property:

```{code-cell} ipython3
force.repr
```
