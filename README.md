# Forallpeople: SI Units Library for Daily Calculation Work

The metric system (now SI system):
*"For all time. For all people."*
  - Nicolas de Caritat (Marquis de Condorcet)

`forallpeople` is a robust library for performing units-aware calculations in Python.
It has a small code base and favours "convention over configuration", although the
actual units environment you work in is fully customizable.

<img src = "https://github.com/connorferster/forallpeople/blob/master/Jupyter.PNG">

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
>>> from forallpeople import *
>>> length = 3 * m
>>> width = 5 * m
>>> height = 2 * m
>>> vol = length * width * height
>>> vol
30.000 m³
>>> mass = 534.25 * kg
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
>>> current = 0.5 * A
>>> current
500.000 mA
>>> resistance = 1200 * Ohm
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
### Import just the basic SI units:

Note: `forallpeople` is a library that was *specifically* designed to be used with `import *` for maximum convenience.

`from forallpeople import *`

This will initialize the namespace with all of the basic SI units: `m`, `kg`, `s`, `A`, `cd`, `K`, `mol`.

### Import the basic SI units and all of the SI derived units through the default environment

```
from forallpeople import *
environment('default')
from forallpeople import *
```

This will initialize the "default" environment which will initialize the namespace with all of the basic SI units and the derived SI units: `N` for newton, `Pa` for pascal, `J` for joule, `W` for watt, `C` for coulomb, `V` for volt, `F` for farad, `ohm` for ohm, `S` for siemens, `Wb` for weber, `T` for tesla, `H` for henry, `lm` for lumen, `lx` for lux, `Bq` for becquerel, `Gy` for gray, `Sv` for sievert, and `kat` for katal.

The "double import" above is required to bring in the newly instantiated `Physical` instances (performed by `environment('default')`) into the global namespace for use.

You can also import it into its own namespace:

`import forallpeople as si`
`si.environment('default')`

And then use all of the units listed above with the si prefix, e.g. `si.m`, `si.kg`, `si.s`, etc.

Constraining the module to using it's own namespace (e.g. as `si`) prevents the need for the "double import"

### REPLs and Jupyter Notebook/Lab

`forallpeople` prioritizes *usage conventions* over *python conventions*. Specifically, the library *deliberately* switches the intentions behind the `__repr__()` and `__str__()` methods: `__repr__()` will give the pretty printed version and `__str__()` will give a version of the unit that can be used to recreate the unit. As such, it becomes intuitive to use within any python repl and it really shines when used in a Jupyter Notebook. This also makes it natuarlly compatible with other common python libraries such as `pandas` and `numpy`.

## Examples

A simple example

```
>>> from forallpeople import *
>>> length = 3 * m
>>> width = 5 * m
>>> height = 2 * m
>>> vol = length * width * height
>>> vol
30.000 m³
>>> mass = 534.25 * kg
>>> dens = mass/vol
>>> dens
17.808 kg·m⁻³
>>> type(dens)
<class 'forallpeople.Physical'>
>>> dens.data
'Physical(value=17.808333333333334, dimensions=Dimensions(kg=1, m=-3, s=0, A=0, cd=0, K=0, mol=0), factor=1, _precision=3)'
```

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



