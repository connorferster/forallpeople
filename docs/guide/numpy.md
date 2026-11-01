---
file_format: mystnb
kernelspec:
  name: python3
  display_name: Python 3
---

# Using numpy

```{code-cell} ipython3
import numpy as np
import forallpeople as si
si.environment("structural")
```

`Physical` instances can be the elements of numpy arrays (with
`dtype=object`), and most element-wise operations work:

```{code-cell} ipython3
m1 = np.array([[5.0 * si.kN, 3.5 * si.kN], [3.5 * si.kN, 5.0 * si.kN]])
m2 = np.array([[7.7 * si.kN, 6.6 * si.kN], [6.6 * si.kN, 7.7 * si.kN]])
m1 + m2
```

```{code-cell} ipython3
m1 @ m2
```

```{code-cell} ipython3
m1 / m2
```

## Numerical routines

Routines that need numbers, such as `np.linalg.inv` or `np.linalg.solve`,
don't accept object arrays of quantities. Separate the values from the units
with {meth}`~forallpeople.Physical.split`, calculate with the values, and
multiply the units back on:

```{code-cell} ipython3
K = 2500 * si.kN / si.m          # a spring stiffness
value, unit = K.split()
value, unit
```

```{code-cell} ipython3
stiffness = np.array([[2, -1], [-1, 2]]) * value
loads = np.array([10.0, 5.0]) * (1 * si.kN).value

displacements = np.linalg.solve(stiffness, loads) * si.m
displacements
```

`split()` returns the value in SI base units (as `.value` does) and a unit
quantity of `1` with the same dimensions. Their product is the original
quantity. With `base_value=False`, the value is the displayed number instead.
