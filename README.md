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

## Installing

`pip install forallpeople`

## Basic usage

`forallpeople` is a library that was *specifically* designed to be used with `import *` for maximum convenience.

`from forallpeople import *`

This will initialize the namespace with all of the basic SI units: `m`, `kg`, `s`, `A`, `cd`, `K`, `mol`.

It will also initialize the namespace with all of the basic derived SI units: `N` for newton, `Pa` for pascal, `J` for joule, `W` for watt, `C` for coulomb, `V` for volt, `F` for farad, `ohm` for ohm, `S` for siemens, `Wb` for weber, `T` for tesla, `H` for henry, `lm` for lumen, `lx` for lux, `Bq` for becquerel, `Gy` for gray, `Sv` for sievert, and `kat` for katal.

You can also import it into its own namespace:

`import forallpeople as si`

And then use all of the units listed above with the si prefix, e.g. `si.m`, `si.kg`, `si.s`, etc.

### REPLs and Jupyter Notebook/Lab

`forallpeople` prioritizes *usage conventions* over *python conventions*. Specifically, the library *deliberately* switches the intentions behind the __repr__() and __str__() methods: __repr__() will give the pretty printed version and __str__() will give a version of the unit that can be used to recreate the unit. As such, it becomes intuitive to use within any python repl and it really shines when used in a Jupyter Notebook. This also makes it natuarlly compatible with other common python libraries such as `pandas` and `numpy`.

## Examples

```
>>> from forallpeople import *
>>> length = 3 * m
>>> width = 5 * m
>>> height = 2 * m
>>> vol = length * width * height
>>> vol
30.000 m³





