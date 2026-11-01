---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# Empirical formulas

Many design formulas come from fitting test results. They assume their inputs
are in particular units, and give a result in some other unit, without being
dimensionally consistent. forallpeople can handle these, as long as the hidden
units are made explicit.

```{code-cell} ipython3
import math
import forallpeople as si
si.environment("structural")
```

## Roots of stresses

Concrete design codes use $\sqrt{f'_c}$ with $f'_c$ in MPa, and treat the
result as a stress in MPa. The intent is the square root of the *number* 35,
in MPa.

Because `float()` gives the displayed number (see
{doc}`display`), `math.sqrt` of a quantity displayed in MPa is the root of the
number in MPa. Put the units back on:

```{code-cell} ipython3
f_c = 35 * si.MPa
math.sqrt(f_c) * si.MPa
```

To use this in many formulas, write a function for it:

```{code-cell} ipython3
def sqrt_stress(f):
    """Returns the square root of the stress 'f' (in MPa), in MPa."""
    return math.sqrt(f.prefix("M")) * si.MPa

sqrt_stress(35 * si.MPa), sqrt_stress(0.5 * si.MPa)
```

`.prefix("M")` fixes the displayed prefix, so `float()` (and `math.sqrt`) see
the stress in MPa even when it would otherwise be displayed in kPa.

## Hidden units in coefficients

A coefficient can carry units that the formula doesn't show. The area of
flexural reinforcement in the Canadian concrete code is

$$A_s = 0.0015\, f'_c\, b \left(d - \sqrt{d^2 - \frac{3.85\, M_f}{f'_c\, b}}\right)$$

which should give an area, but the coefficient `0.0015` has hidden units of
`1/MPa`. Written as it is, the result has units of force:

```{code-cell} ipython3
f_c = 35 * si.MPa
b = 300 * si.mm
d = 600 * si.mm
M_f = 200 * si.kN * si.m

0.0015 * f_c * b * (d - (d**2 - (3.85 * M_f) / (f_c * b)) ** 0.5)
```

Give the coefficient its units, and the result is an area:

```{code-cell} ipython3
A_s = (0.0015 / si.MPa) * f_c * b * (d - (d**2 - (3.85 * M_f) / (f_c * b)) ** 0.5)
A_s.prefix("m")
```

## Purely numerical formulas

Some formulas are a numerical fit, with no dimensional meaning at all. The
tension resistance of a bolted timber connection in the Canadian wood code is

$$QS_i = 14\, t \sqrt{\frac{d_e}{1 - d_e/d}}$$

with `t`, `d_e` and `d` in mm, and the result in N. Take the numbers out in
the units the formula expects (`.prefix("m")` displays a length in mm, so
`float()` gives millimetres), calculate, and apply the units to the result:

```{code-cell} ipython3
t = 38 * si.mm
d = 140 * si.mm
d_e = 89 * si.mm

t_mm, d_mm, d_e_mm = (float(x.prefix("m")) for x in (t, d, d_e))
QS_i = 14 * t_mm * math.sqrt(d_e_mm / (1 - d_e_mm / d_mm)) * si.N
QS_i
```
