---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# Calculating with quantities

```{code-cell} ipython3
import forallpeople as si
si.environment("default")
```

A {class}`~forallpeople.Physical` is a number with dimensions. Arithmetic works
as it would in a hand calculation: the dimensions combine, and the result is
another `Physical`.

## Multiplication and division

Quantities of any dimensions multiply and divide. A number multiplies or
divides a quantity and keeps its units.

```{code-cell} ipython3
area = 3 * si.m * 4 * si.m
pressure = 2500 * si.N / area
pressure
```

The units **reduce** as you go: `N / m²` is recognised as `Pa` because the
`default` environment defines it. Nothing has to be converted by hand.

## Units that cancel give numbers

When the units cancel completely, the result is a plain `float`, not a
"dimensionless" quantity:

```{code-cell} ipython3
spaces = 4.2 * si.m / (0.25 * si.m)
spaces, type(spaces)
```

```{code-cell} ipython3
import math

rise = 1.2 * si.m
run = 4.8 * si.m
math.degrees(math.atan(rise / run))
```

This is why forallpeople has no dimensionless units such as radians or
percent: a ratio is just a number.

## Addition and subtraction

Quantities add and subtract when their dimensions are the same:

```{code-cell} ipython3
500 * si.kg + 23 * si.kg - 300 * si.kg
```

Adding quantities of different dimensions raises a `ValueError`:

```{code-cell} ipython3
:tags: [raises-exception]
5 * si.m + 2 * si.kg
```

A plain number added to a quantity takes the units of the quantity:

```{code-cell} ipython3
5 * si.kg + 10
```

## Powers and roots

A quantity can be raised to any numeric power. The dimensions are multiplied
by the power:

```{code-cell} ipython3
side = 300 * si.m
side**2
```

```{code-cell} ipython3
(9 * si.m**2).sqrt()
```

`.sqrt(n)` takes the `n`-th root (`.sqrt(3)` is the cube root). A quantity
cannot be raised to the power of another quantity.

## Comparisons

Quantities of the same dimensions compare as you would expect:

```{code-cell} ipython3
5 * si.m > 4.5 * si.m, 3 * si.N / si.m**2 == 3 * si.Pa
```

Comparing quantities of different dimensions raises a `ValueError`.

## Floor division and modulo

`//` and `%` are not defined for `Physical`. With prefixes and unit factors,
it is ambiguous whether they should act on the SI value or on the displayed
value. To count how many times one quantity fits into another, divide and
round the resulting number:

```{code-cell} ipython3
int(4.2 * si.m / (0.25 * si.m))
```

## Quantities are immutable

Like `int`, `float` and `str`, a `Physical` cannot be changed: every operation
returns a new instance. In-place operators such as `+=` raise an error, so
write `a = a + b` instead. Because they are immutable, quantities are hashable
and can be used as dict keys or in sets.

## What a quantity stores

A `Physical` has five attributes:

`value`
: The magnitude in SI base units. This never depends on the environment or on
  how the quantity is displayed.

`dimensions`
: A {class}`~forallpeople.dimensions.Dimensions` named tuple of the powers of
  the seven base units, in the order `kg, m, s, A, cd, K, mol`.

`factor`
: The scale to a non-SI unit (e.g. `1/0.3048` for feet). It is `1` for SI
  units.

`precision`
: The number of decimal places displayed (default `3`).

`prefixed`
: An SI prefix chosen for display (e.g. `"k"`), or `""` to choose
  automatically.

```{code-cell} ipython3
pressure.repr
```

See {doc}`../background` for why quantities are modelled this way.
