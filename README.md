# Forallpeople: SI Units Library for Daily Calculation Work

The metric system (now SI system):
*"For all time. For all people."*
  - Nicolas de Caritat (Marquis de Condorcet)

`forallpeople` is a robust library for performing units-aware calculations in Python.
It has a small code base and favours "convention over configuration", although the
actual units environment you work in is fully customizable.

There are other units packages out there but `forallpeople` is designed for fast and
simple daily use: units act as you would expect (they automatically combine and
cancel out), they are labelled as you would expect (e.g. 'm' for meter, 'kg' for
kilogram), unit quantities exist independently, and are ready-to-use upon import.

Intended users: working engineers, scientists, teachers, and students who want to be
able to check any calculations for dimension errors, print formatted calculation
reports and summaries with Jupyter/IPython, and focus on productivity instead of
fussing with managing units and dimensions.

## Examples

A simple example:

```
>>> import forallpeople as si
>>> length = 3 * si.m
>>> width = 5 * si.m
>>> height = 2 * si.m
>>> vol = length * width * height
>>> vol
30.000 m³
>>> mass = 534.25 * si.kg
>>> dens = mass/vol
>>> dens
17.808 kg·m⁻³
>>> type(dens)
<class 'forallpeople.Physical'>
>>> dens.data
'Physical(value=17.808333333333334, dimensions=Dimensions(kg=1, m=-3, s=0, A=0, cd=0, K=0, mol=0), factor=1, _precision=3)'
```

Another example, showing auto-reduction of units and auto-prefixing:
```
>>> si.environment('default')
>>> current = 0.5 * si.A
>>> current
500.000 mA
>>> resistance = 1200 * si.Ohm
>>> resistance
1.200 kΩ
>>> voltage = current * resistance
>>> voltage
600.000 V
>>> type(voltage)
<class 'forallpeople.Physical'>
>>> voltage.data
'Physical(value=600.0, dimensions=Dimensions(kg=1, m=2, s=-3, A=-1, cd=0, K=0, mol=0), factor=1, _precision=3)'
```

## Installing

`pip install forallpeople`

## Basic usage

`import forallpeople as si`

This will import the `Physical` class that is the class used to describe all of the SI units, or other derived units,
as physical quantities. Additionally, it will import the pre-instantiated SI base units of:

* `si.m` - meter
* `si.kg` - kilogram
* `si.s` - second
* `si.A` - ampere
* `si.cd` - candela
* `si.K` - kelvin
* `si.mol` - mole

This allows you to perform units-aware calculations with all of the SI base units but the results from all calculations will
be shown in the form of a combination of the base units, e.g.:

```
>>> area = 3*4 * si.m**2
>>> area
12.000 m²
>>> force = 2500 * si.kg * si.m / si.s**2
>>> force
2500.000 kg·m·s⁻²
>>> force / area
208.333 kg·m⁻¹·s⁻²
```

If you can recognize the units, you may realize that the final answer is in units of pascals, however you probably
would rather see the final units in *pascals*. To do this, you load an `Environment`.

## Loading an environment

`si.environment('default')`

This will import the "default" environment which contains all of the SI derived units:

* `si.N` - newton
* `si.Pa` - pascal
* `si.J` - joule
* `si.W` - watt
* `si.C` - coulomb
* `si.V` - volt
* `si.F` - farad
* `si.ohm` - ohm
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

Now, the same calculation will provide the same result but it will appear more conventional:

```
>>> area = 3 * 4 * si.m**2
>>> force = 2500 * si.kg * si.m / si.s**2
>>> force
2.500 kN
>>> force/area
208.333 Pa
```

Because the units of `si.N` are one of the `Physical` instances that have now been instantiated and loaded into the `si` namespace, you can perform this calculation directly: 

```
>>> area = 3 * 4 * si.m**2
>>> force = 2500 * si.N
>>> force / area
>>> 208.333 Pa
```

## Usage with "from forallpeople import *"

Forallpeople was designed to be used with `import *` for ease of use and to reduce the amount of re-typing, i.e. `si.m` becomes simply `m`. This also makes `forallpeople` more compatible with computational reporting packages such as `handcalcs`. However, using `import *` can also quickly clutter up one's namespace, especially if the user loads multiple environments: each new environment instantiates the units defined in the environment as new variable names without removing the previous ones. i.e. new variable instances are simply appended to the global namespace.

If one wishes to use `from forallpeople import *` with environments, it requires an additional step:

```
from forallpeople import *
environment('default') # or your own defined environment name
from forallpeople import *
```

Note the import, loading an environment, and then importing again. The reason for this is to allow the module to load the newly instantiated variable names into the namespace. In essence, when you import the first time, you import the basic variable names into your global namespace. When you load an environment, you load additional names into the *module's* namespace but, since you have not named it, you cannot access them. It is only when you perform the import again, and python recognizes that there are now new elements in the module's namespace to import, that you will get the new variable names into your global namespace.


## How Physical instances work

## How Environments work with Physical instances


## REPLs and Jupyter Notebook/Lab

`forallpeople` prioritizes *usage conventions* over *python conventions*. Specifically, the library *deliberately* switches the intentions behind the `__repr__()` and `__str__()` methods: `__repr__()` will give the pretty printed version and `__str__()` will give a version of the unit that can be used to recreate the unit. As such, it becomes intuitive to use within any python repl and it really shines when used in a Jupyter Notebook. This also makes it natuarlly compatible with other common python libraries such as `pandas` and `numpy`.

## Anatomy of the Physical instance

`forallpeople` is all about describing **physical quantities** and defines a single class, `Physical`, to describe them. `Physical` instances are composed of four components (as attributes): 
* .value = a `float` that is the numerical value of the quantity as described by the SI base units
* .dimensions = a `NamedTuple` that describes the dimensionality of the physical quantity
* .factor = a `float` that can be used to define a physical quantity in an alternate unit system that is linearly based upon the SI units (e.g. US customary units, imperial, etc.)
* ._precision = an `int` that describes the number of decimal places to display when the `Physical` instance is rendered through `.__repr__()`

`forallpeople` automatically reduces units into defined units:
```
>>> current = 0.5 * A
>>> current
500.000 mA
>>> resistance = 1200 * Ohm
>>> resistance
1.200 kΩ
>>> voltage = current * resistance
>>> voltage
600.000 V
```

You can see the dimensions and constituents of each 

## Gotchas

* Does not know "prefixed units" automatically; they must be declared as variables or set up in the environment

`forallpeople` 



