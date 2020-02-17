# Forallpeople: SI Units Library for Daily Calculation Work

The metric system (now SI system):
*"For all time. For all people."*
Nicolas de Caritat (Marquis de Condorcet)

`forallpeople` is a robust library for performing units-aware calculations in Python.
It has a small code base and favours "convention over configuration", although the
actual units environment you work in is fully customizable. It is Jupyter-ready and 
tested on Windows.

Intended users: working engineers, scientists, teachers, and students who want to be
able to check any calculations for dimension errors, print formatted calculation
reports and summaries with Jupyter/IPython, and focus on productivity instead of
fussing with managing units and dimensions.

## Teaser in Jupyter

<img src = "https://github.com/connorferster/forallpeople/blob/master/Jupyter_example.PNG">


## Installing

You can install using pip:

`pip install forallpeople`

## Basic usage

The most basic use is just to import the library:

`import forallpeople as si`

This will import the `Physical` class. It is the primary class in the module and is used to describe all physical quantities. 
`Physical` instances are **immutable**.

Upon import, the SI base units are instantiated and are available in the namespace as the following variables:

* `si.m` - meter
* `si.kg` - kilogram
* `si.s` - second
* `si.A` - ampere
* `si.cd` - candela
* `si.K` - kelvin
* `si.mol` - mole

Because we have not loaded an environment yet, all results from all calculations will
be shown in the form of a combination of the SI base units, e.g.:

```python
>>> area = 3*si.m * 4*si.m
>>> area
12.000 m²
>>> force = 2500 * si.kg * si.m / si.s**2
>>> force
2500.000 kg·m·s⁻²
>>> force / area
208.333 kg·m⁻¹·s⁻²
```

The resulting `force / area` calculation is in pascals (if you can recognize the dimensions).

However, you would probably rather see the final units in *pascals*. To do this, you load an `Environment`.

## Loading an environment

`si.environment('default')`

Now, the above calculation will appear more conventional:

```python
>>> area = 3*si.m * 4*si.m
>>> force = 2500 * si.kg * si.m / si.s**2
>>> force
2.500 kN
>>> force/area
208.333 Pa
```

When you load an environment, whether it is the `default` environment or one you define, the *representation* of the units will change to fit the definitions in the environment. Environment definitions are *dimensional*, meaning, if you end up with a `Physical` of a dimension that matches a dimension in the environment, then when you ask to see your Physical instance (e.g. in a REPL), you will see it in the units defined by the dimensions.

It is important to note that, no matter what environment is loaded or not loaded, your Physical instances will always carry their value in the SI base units, e.g.:

```python
>>> pressure = force / area
>>> pressure = 208.333 Pa
>>> pressure.repr
>>> 'Physical(value=208.33333333333334, dimensions=Dimensions(kg=1, m=-1, s=-2, A=0, cd=0, K=0, mol=0), factor=1, _precision=3)'
```

Additionally, when you load an environment, the units defined in the environment will be instantiated  as `Physical` and you can utilize them as variables in calculations.

The `'default'` environment defines and loads the following units as variables:

* `si.N` - newton
* `si.Pa` - pascal
* `si.J` - joule
* `si.W` - watt
* `si.C` - coulomb
* `si.V` - volt
* `si.F` - farad
* `si.Ohm` - ohm
* `si.S` - siemens
* `si.Wb` - weber
* `si.T` - tesla
* `si.H` - henry
* `si.lm` - lumen
* `si.lx` - lux
* `si.Bq` - becquerel
* `si.Gy` - gray
* `si.Sv` - sievert
* `si.kat` - katal


Because the units of `si.N` are one of the `Physical` instances that have now been instantiated and loaded into the `si` namespace, you can perform this calculation directly: 

```python
>>> area = 3*si.m * 4*si.m
>>> force = 2500 * si.N
>>> force / area
>>> 208.333 Pa
```

## API

Each `Physical` instance offers the following methods and properties:

### Properties

* `.value`: A `float` that represents the numerical value of the physical quantity in SI base units
* `.dimensions`: A `Dimensions` object (a `NamedTuple`) that describes the dimension of the quantity as a vector
* `.factor`: A `float` that represents a factor that the value should be multiplied by to linearly scale the quantity into an alternate unit system (e.g. US customary units or UK imperial) that is defined in SI units.
* `.latex`: A `str` that represents the pretty printed `repr()` of the quanity in latex code.
* `.html`: A `str` that represents the pretty printed `repr()` of the quantity in HTML code.
* `.repr`: A `str` that represents the traditional machine readable `repr()` of the quantity: `Physical` instances default to a pretty printed `__repr__()` instead of a machine readable `__repr__()` because it makes them more compatible with other libraries (e.g. `numpy`, `pandas`, handcalcs[https://github.com/connorferster/handcalcs], and `jupyter`).

### Methods

Almost all methods return a new `Physical` because all instances are **immutable**.

* `.round(self, n: int)`: Returns a `Physical` instance identical to `self` except with the display precision set to `n`. You can also call the python built-in `round()` on the instance to get the same behaviour.
* `.sqrt(self, n: float)`: Returns a `Physical` that represents the square root of `self`. `n` can be set to any other number to compute alternate roots.
* `.split(self)`: Returns a 2-tuple where the 0-th element is the `.value` of the quantity and the 1-th element is the `Physical` instance with a value set to `1` (i.e. just the dimensional part of the quantity). To reconstitute, multiply the two tuple elements together. This is useful to perform computations in `numpy` that only accept numerical input (e.g. `numpy.linalg.inv()`): the value can be computed separately from the dimension and then reconstituted afterwards.
* `.in_units(self, unit_name: str = "")`: Returns a new `Physical` instance with a `.factor` corresponding to a dimensionally compatible unit defined in the `environment`. If `.in_units()` is called without any arguments, then a list of available units for that quantity is printed to `stdout`.

## Calculations with "empirical" formulas (dimensionally inconsistent formulas)

It is not uncommon for engineering formulas to use formulas whose dimensions seem to magically appear on their own. The kinds of formulae are compatible with `forallpeople` if the "hidden dimensions" are recognized and accounted for by the user.

Example: in the Canadian concrete design code it is recognized that the `sqrt(MPa)` results in units of `MPa` instead of `MPa⁰'⁵`. To compensate for this, because `forallpeople` requires units to dimensionally consistent, we have to multiply our result by `1 * MPa⁰'⁵`. 

```python
>>> import forallpeople as si
>>> si.environment('structural')
>>> f_c = 35 * si.MPa
>>> f_c_sqrt = f_c.sqrt() * (1*si.MPA ** 0.5)
>>> f_c_sqrt
5.916 MPa
```


## Using * imports

Forallpeople was designed to be used with `import *` for ease of use and to reduce re-typing, i.e. `si.m` becomes simply `m`. This also makes `forallpeople` more compatible with computational reporting packages such as handcalcs[https://github.com/connorferster/handcalcs]. 

If one wishes to use `from forallpeople import *` with environments, it requires an additional step:

```python
from forallpeople import *
environment('default') # or your own defined environment name
from forallpeople import *
```

Note the import, loading an environment, and then importing again. 

The reason for this is to allow the module to load the newly instantiated variable names into the namespace. In essence, when you import the first time, you import the basic variable names into your global namespace. When you load an environment, you load additional names into the *module's* namespace but, since you have not named the module's namespace, you cannot access them. It is only when you perform the import again, and python recognizes that there are now new elements in the module's namespace to import, that you will get the new variable names into your global namespace.

However, using `import *` can also quickly clutter up one's namespace, especially if the user loads multiple environments: the variable names of the new `Physical` instances are simply appended to the global namespace.

## How Physical instances work

`forallpeople` is all about describing **physical quantities** and defines a single class, `Physical`, to describe them. `Physical` instances are composed of four components (as attributes): 

* `<instance>.value` = a `float` that is the numerical value of the quantity in the SI base units
* `<instance>.dimensions` = a `NamedTuple`, called `Dimensions`, that describes the dimensionality of the physical quantity
* `<instance>.factor` = a `float` that can be used to define a physical quantity in an alternate unit system that is linearly based upon the SI units (e.g. US customary units, imperial, etc.)
* `<instance>._precision` = an `int` that describes the number of decimal places to display when the `Physical` instance is rendered through `.__repr__()`, default value is `3`.

Because `Physical` instances are immutable (just like `int`, `float`, and `bool`), the user cannot set these attributes directly. It also means that any operation operating on a `Physical` instance returns a new instance. As such, the intended way of creating new instances is as the result of calculations.

### Dimension vectors

`Physical` instances track the dimensions of their physical quantities by using vectors. The vector is stored in the `Dimensions` class, which is a `NamedTuple`. Using the vector library, tuplevector[https://github.com/connorferster/tuplevector] (which is "baked in" to `forallpeople`), we can perform vector arithmetic on `Dimensions` objects directly. 

### Arithmetic on Physicals

Arithmetic on `Physical` instances work mostly how you would expect, with few caveats:

* Addition/Subtraction: 
  * Two (or more) instances will add/sub if dimensions are equal
  * One instance and one (or more) number(s) (`float`, `int`) will add/sub and assume the units of the instance
  * e.g. `a = 5*si.m + 2*si.m` ,  `b = 5*si.kg + 10`
* Multiplication:
  * Instances will multiply with each other and their dimensions will combine
  * Instances will multiply with numbers and will assume the units of instance(s) that were also a part of the multiplication
  * e.g. `c = 12 *si.m * 2*si.kg * si.s` , `d = 4.5*si.m * 2.3`
* Division (true division):
  * Instances will divide by each other and their dimensions will combine
  * Instances will divide with numbers and will assume the units of the instance(s) that were also a part of the division
  * If two instances of the same dimension are divided, the result will be a `float` (i.e. the units are completely cancelled out; there is no "dimensionless" `Physical`: either a quantity has units as a `Physical` or it is a number)
  * e.g. `5 * si.m / (2 * si.m)` -> `2.5`
* Floor division:
  * Is intentionally not implemented in `Physical`. This is because it creates ambiguity when working within an environment where units with factors are defined (does floor division return the value of floor division of the SI base unit value or the apparent value after multiplied by it's `.factor`? Either would return results that may be unexpected.)
  * Floor division can be achieved by using true division and calling `int()` on the result, although this returns an `int` and not a `Physical`
* Power:
  * You can raise an instance to any power, if it is a number (`int`, `float`). You cannot raise a Physical instance to the power of another instance (what would that even mean?)
* Abs:
  * Returns the absolute value of the instance
* Neg:
  * Equivalent to instance * -1



## Auto-prefixing

`forallpeople` employs "auto-prefixing" and, as such, does not specifically allow the user to choose the order of magnitude to display the unit in. In this way, the library chooses the principal of "convention over configuration". For example:

```python
>>> current = 0.5 * A
>>> current
500.000 mA # 'current' is auto-prefixed to 500 milliamperes
>>> resistance = 1200 * Ohm
>>> resistance
1.200 kΩ # 'resistance' is auto-prefixed to kilo-ohms
>>> voltage = current * resistance
>>> voltage
600.000 V # 'voltage' does not have a prefix because its value is above 1 V but less than 1000 V
```

The prefixes of the entire SI units system (from `10**-24` to `10**24`) are built-in to the `Physical` class.

However, auto-prefixing is only triggered in certain, intuitive circumstances:

1. The unit is **one of** `m`, `kg`, `s`, `A`, `cd`, `K`, or  `mol` (i.e. the SI base units)
2. The unit is a derived unit in the SI unit system (i.e. it is defined in the environment and has a `.factor == 1`)

This means that auto-prefixing is not used in the following circumstances:

1. The unit is defined in the environment with a factor (e.g. `lb`: it would not make sense to have a `klb` or a `mlb`)
2. The unit is a compound unit but not defined in the environment (e.g. it would not make sense to have a `kkg*m/s`)

When the auto-prefixing is triggered for a unit and that unit is of a power other than `1`, then auto-prefixing considers the prefix to also be part of the unit's power. For example:

```python
>>> a = 5000 * si.m
>>> a
5.000 km
>>> a**2
25.000 km² # This may seem intuitive but it's important to remember that the 'kilo' prefix is also being squared
>>> b = 500000 * si.m 
>>> b
500.000 km
>>> b**2
250000.000 km² # Why isn't this being shown as 250 Mm²? Because it would take 1,000,000 km² to make a Mm². This is only 250,000 km².
```

## How to define your own environments

An environment is simply a JSON document stored within the package folder in the following format:

    "Name": {
        "Dimension": [0,0,0,0,0,0,0],
        "Value": 1,
        "Factor": 1,
        "Symbol": ""}


For example, if you wanted to create an environment that defined only kilopascals and pounds-force in US customary units, you would do it like this:

    "kPa": {
        "Dimension": [1,-1,-2,0,0,0,0],
        "Value": 1000},
    "lb-f": {
        "Dimension": [1, 1, -2, 0, 0, 0, 0],
        "Factor": "1/0.45359237/9.80665",
        "Symbol": "lb"}


* Note, JSON does not allow comments; comments are included in this example for explanation purposes, only. If you copy/paste this example into your JSON environemnt file, be sure to remove the comments.
* Note also that arithmetical expressions in Factor are eval'd to allow for the most accurate input of factors; to prevent a security risk, Factor is regex'd to ensure that only numbers and arithmetic symbols are in Factor and not any alphabetic characters (see Environment._load_environment in source code to validate).


## REPLs and Jupyter Notebook/Lab

`forallpeople` prioritizes *usage conventions* over *python conventions*. Specifically, the library *deliberately* switches the intentions behind the `__repr__()` and `__str__()` methods: `__repr__()` will give the pretty printed version and `__str__()` will give a version of the unit that can be used to recreate the unit. As such, it becomes intuitive to use within any python repl and it really shines when used in a Jupyter Notebook. This also makes it natuarlly compatible with other common python libraries such as `pandas` and `numpy`.

## Using Physicals with Numpy

`Physical` instances can be used with many `numpy` operations. See below example:

```python
>>> a = 5 * si.kN
>>> b = 3.5 * si.kN
>>> c = 7.7 * si.kN
>>> d = 6.6 * si.kN
>>> m1 = np.matrix([[a, b], [b, a]])
>>> m2 = np.matrix([[c, d], [d, c]])
>>> m1
matrix([
[5.000 kN, 3.500 kN],
[3.500 kN, 5.000 kN]], dtype=object)
>>> m2
matrix([
[7.700 kN, 6.600 kN],
[6.600 kN, 7.700 kN]], dtype=object)
>>> m1 + m2
matrix([
[12.700 kN, 10.100 kN],
[10.100 kN, 12.700 kN]], dtype=object)
>>> m1 @ m2
matrix([
[61.600 kN², 59.950 kN²],
[59.950 kN², 61.600 kN²]], dtype=object)
>>> m2 - m1
matrix([
[2.700 kN, 3.100 kN],
[3.100 kN, 2.700 kN]], dtype=object)
>>> m1 / m2
matrix([
[0.6493506493506493, 0.5303030303030303],
[0.5303030303030303, 0.6493506493506493]], dtype=object)
```
 



