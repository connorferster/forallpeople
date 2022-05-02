# Background and Approach

`forallpeople` implements the SI unit system in a single Python class called, `Physical`, as in "a physical quantity".

It is intended for folks who routinely perform calculations within a single, typical, unit context and with limited precision requirements. This is common among engineers working within a single discipline (e.g. electrical, mechanical, or civil engineering, etc.) but may be less common to scientists who may be working between different unit contexts with precisions that may or may not carry uncertainties (other units packages, such as pint, may be more suitable for those applications). 

`forallpeople` assumes the following:

* Floating point numbers are going to be used for calculation and their precision is generally adequate
* A physical quantity with a given set of dimensions will always represent the same phenomenon
    * e.g. One context may be that a `Physical` with `Dimensions(kg=1, m=2, s=-2, A=0, cd=0, K=0, mol=0)` will always represent a "torque" (say, in `N*m`) but will never be considered as "energy" (say, in `J`). However, another context could consider a `Physical` with the same dimensions always as "energy" in joules and never as a "torque". `forallpeople` would never consider the dimensions to represent the phenomena of both "energy" and "torque" at the same time.
    * This is consistent with the application of derived units as described in the [SI brochure](https://www.bipm.org/en/publications/si-brochure) (pg. 140, 9th ed.)


## Data Model

A `Physical` instance has the following two _primary_ attributes to model an SI unit:

1. `.value`: The magnitude of the quantity in unscaled SI base units
2. `.dimensions`: A vector, implemented as a `NamedTuple`, that describes the dimension of the physical quantity within the seven dimensional space where the SI units are defined: kg, m, s, A, cd, K, mol.

Additionally, it has the following three _secondary_ attributes which affect how the physical quantity is _represented_:

3. `.precision: int = 3`: The default number of decimal places to display in the physical quantity's representation
4. `.factor: Decimal = Decimal("1")`: An arbitrary factor applied to the `.value` attribute to scale it to another unit system based upon the SI units. This is most commonly used for representing units in the US Customary system.
5. `.prefixed: str = ""`: A single-character string representing one of the scaling prefixes used in the SI unit system, e.g. "k" for "kilo", as in "kilometer" or "u" for "micro" as in "micronewton".

## Unit Representation

All `Physical` instances model a physical quantity in SI base units. Each `Physical` instance is immutable representing that the physical quantity in real life is also "immutable": it simply is as it is and we have the SI units to describe it.

However, we can change the _representation_ of the physical quantity to whatever we want. `forallpeople` can instantiate a singleton `Environment` which globally affects how the representation of all physical quantities in the namespace are displayed to you, the calculator.

In this example, a force is calculated. The representation of the resulting force is the default one: an unscaled magnitude in SI base units.

```python
import forallpeople as si

G = 9.81 * (si.m/si.s**2)
m = 3200.5*si.kg
force = m*G
print(force) # 318.825 kg·m·s⁻²
```

The representation of this physical quantity can be altered by loading an environment. This example will use the `'default'` environment which defines the "derived" units of the SI unit system (i.e. Pa, N, V, W, etc.).

```python
import forallpeople as si

G = 9.81 * (si.m/si.s**2)
m = 3200.5*si.kg
force = m*G
print(force) # 318.825 kg·m·s⁻²
si.environment('default')
print(force) # 318.825 N
```

The immutable physical quantity of `force` is unchanged. One way to think of the unit environment is as a kind of "lens" with which we "view" the resulting physical quantity. Depending on the environment that is loaded, the view of the physical quantity will change. 

As an example, let us now load the `'us_customary'` environment.

```python
import forallpeople as si

G = 9.81 * (si.m/si.s**2)
m = 3200.5*si.kg
force = m*G
print(force) # 318.825 kg·m·s⁻²
si.environment('default')
print(force) # 318.825 N
si.environment('us_customary')
print(force) # 70573.126 lb
```

All of these are different representations of the same _immutable_ physical quantity of `318.825 kg·m·s⁻²`.

## No dimensionless definitions

Some unit libraries define dimensionless units such as degree, radian, or steradian.

`forallpeople` does not allow for the definition of dimensionless units. If a `Physical` ever results in a quantity that has `.dimensions` of `0` in all components then a `float` is returned.

The intended behaviour is to be similar to that of a hand calculation: when the units cancel out, they cancel out and you are left with a number.

This makes trigonometry easy and intuitive.

e.g. 

```python
from math import cos
import forallpeople as si
x1 = 32.3 * si.m
x2 = 49.1 * si.m
print(x1 / x2) # 0.6578411405295315
print(cos(x1 / x2)) # 0.7913140226440856
```

This approach has the negative consequence of introducing ambiguity between the physical quantities of hertz (cycles per second), angular velocity (radians per second), and angular frequency (radians per second) which all have SI dimensions of `s⁻¹`. The [SI units brochure](https://www.bipm.org/en/publications/si-brochure) recommends "that the quantities called "frequency", "angular frequency", and "angular velocity" always be given explicit units of Hz or rad/s and not `s⁻¹`." However, this can be _partially_ managed within `forallpeople` through the unit environment definitions. See [Customizing Unit Environments](customizing_unit_environments.ipynb).


## Auto-scaling

By convention, the [derived](Nomenclature.ipynb) quantities are often represented with prefix that scales the quantity to use a minimum number of digits, e.g. `103000.0 N` would be more commonly written as `103.0 kN` and `0.0000000000234 m` would be more commonly written as `23.4 pm`. `forallpeople` automatically represents base units, powers of base units, and recognized derived units with "auto-scaling" to follow a "convention over configuration" approach. However, a custom prefix can be set on individual instances, see [Assigning Prefixes](basic_usage.ipynb) for more information.

The following units would be auto-scaled (and would also be eligible for providing an over-riding prefix):


