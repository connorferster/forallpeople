# Forallpeople: SI Units Library for Daily Calculation Work

The metric system (now SI system):
*"For all time. For all people."*
  -- Nicolas de Caritat (Marquis de Condorcet)

`forallpeople` is a robust library for performing units-aware calculations in Python.
It has a small code base and favours "convention over configuration", although the
actual units environment you work in is fully customizable. It is Jupyter-ready and 
tested on Windows.

Intended users: working engineers, scientists, teachers, and students who want to be
able to check any calculations for dimension errors, print formatted calculation
reports and summaries with Jupyter/IPython, and focus on productivity instead of
fussing with managing units and dimensions.

## Teaser in Jupyter

<img src = "https://github.com/connorferster/forallpeople/blob/master/Jupyter.PNG">


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

Because we have loaded an environment, all results from all calculations will
be shown in the form of a combination of the SI base units, e.g.:

```
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

```
>>> area = 3*si.m * 4*si.m
>>> force = 2500 * si.kg * si.m / si.s**2
>>> force
2.500 kN
>>> force/area
208.333 Pa
```

When you load an environment, whether it is the `default` environment or one you define, the *representation* of the units will change to fit the definitions in the environment. Environment definitions are *dimensional*, meaning, if you end up with a `Physical` of a dimension that matches a dimension in the environment, then when you ask to see your Physical instance (e.g. in a REPL), you will see it in the units defined by the dimensions.

It is important to note that, no matter what environment is loaded or not loaded, your Physical instances will always carry their value in the SI base units, e.g.:

```
>>> pressure = force / area
>>> pressure = 208.333 Pa
>>> pressure.repr
>>> 'Physical(value=208.33333333333334, dimensions=Dimensions(kg=1, m=-1, s=-2, A=0, cd=0, K=0, mol=0), factor=1, _precision=3)'
```

Additionally, when you load an environment, the units defined in the environment will be instantiated  as `Physical`s and you can utilize them as variables in calculations.

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

```
>>> area = 3*si.m * 4*si.m
>>> force = 2500 * si.N
>>> force / area
>>> 208.333 Pa
```

## Usage with "from forallpeople import *"

Forallpeople was designed to be used with `import *` for ease of use and to reduce re-typing, i.e. `si.m` becomes simply `m`. This also makes `forallpeople` more compatible with computational reporting packages such as `handcalcs`. 

However, using `import *` can also quickly clutter up one's namespace, especially if the user loads multiple environments: the variable names of the new `Physical` instances are simply appended to the global namespace.

If one wishes to use `from forallpeople import *` with environments, it requires an additional step:

```
from forallpeople import *
environment('default') # or your own defined environment name
from forallpeople import *
```

Note the import, loading an environment, and then importing again. The reason for this is to allow the module to load the newly instantiated variable names into the namespace. In essence, when you import the first time, you import the basic variable names into your global namespace. When you load an environment, you load additional names into the *module's* namespace but, since you have not named it, you cannot access them. It is only when you perform the import again, and python recognizes that there are now new elements in the module's namespace to import, that you will get the new variable names into your global namespace.


## How Physical instances work

`forallpeople` is all about describing **physical quantities** and defines a single class, `Physical`, to describe them. `Physical` instances are composed of four components (as attributes): 

* .value = a `float` that is the numerical value of the quantity as described by the SI base units
* .dimensions = a `NamedTuple` that describes the dimensionality of the physical quantity
* .factor = a `float` that can be used to define a physical quantity in an alternate unit system that is linearly based upon the SI units (e.g. US customary units, imperial, etc.)
* ._precision = an `int` that describes the number of decimal places to display when the `Physical` instance is rendered through `.__repr__()`


## REPLs and Jupyter Notebook/Lab

`forallpeople` prioritizes *usage conventions* over *python conventions*. Specifically, the library *deliberately* switches the intentions behind the `__repr__()` and `__str__()` methods: `__repr__()` will give the pretty printed version and `__str__()` will give a version of the unit that can be used to recreate the unit. As such, it becomes intuitive to use within any python repl and it really shines when used in a Jupyter Notebook. This also makes it natuarlly compatible with other common python libraries such as `pandas` and `numpy`.

## Anatomy of the Physical instance



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



