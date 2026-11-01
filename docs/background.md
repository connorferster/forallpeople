# Background and approach

forallpeople models the SI unit system in a single class,
{class}`~forallpeople.Physical`, as in "a physical quantity".

It is written for people who calculate within one usual set of units, to
ordinary floating point precision: engineers in a single discipline, for
example. Scientists who move between unit contexts, or who need to carry
uncertainties, may be better served by a library such as
[pint](https://pint.readthedocs.io/).

## Assumptions

forallpeople assumes that:

- floating point numbers are precise enough for the calculation, and
- within one context, a quantity of given dimensions always represents the
  same kind of thing.

For example, kg·m²·s⁻² can be a torque (in N·m) or an energy (in J). A
structural engineer's environment would display it as a moment, and a thermal
engineer's as an energy, but no environment means both. This follows the use
of derived units in the [SI Brochure](https://www.bipm.org/en/publications/si-brochure)
(9th edition).

## The data model

A `Physical` has two attributes that describe the quantity:

1. `value`: its magnitude in unscaled SI base units, and
2. `dimensions`: a vector of the powers of the seven SI base units
   (kg, m, s, A, cd, K, mol), as a
   {class}`~forallpeople.dimensions.Dimensions` named tuple.

and three that describe how it is shown:

3. `factor`: the scale to a non-SI unit defined from SI units (e.g. US
   customary units), or `1`,
4. `precision`: the number of decimal places displayed, and
5. `prefixed`: an SI prefix to display it with, or `""` to choose one.

Arithmetic acts on the value and the dimension vector: multiplying two
quantities multiplies their values and adds their dimension vectors. The
vector arithmetic is done by `forallpeople.tuplevector`, a small vector library
built into the package.

## The environment is a lens

A physical quantity is what it is: it does not change when it is described in
other units. So `Physical` instances are immutable, and their value is always
stored in SI units.

What can change is the **representation**. The active
{doc}`environment <guide/environments>` decides which units quantities are
displayed in. Loading a different environment changes how every quantity
looks, but not what any of them are.

## No dimensionless units

Some unit libraries define dimensionless units, such as radians or percent.
forallpeople does not: if the units of a result cancel, the result is a
`float`. This is how a hand calculation works, and it makes trigonometry and
ratios straightforward.

The cost is that some quantities with the same dimensions can't be told apart.
Hertz (cycles per second) and angular velocity (radians per second) both have
dimensions of s⁻¹. The SI Brochure recommends always writing these as Hz or
rad/s, never as s⁻¹. In forallpeople, the environment decides which of them a
quantity of s⁻¹ is shown as.

## Convention over configuration

Quantities are displayed the way an engineer would write them: in a
recognised unit, scaled to a conventional prefix, to three decimal places.
`repr()` gives this readable form rather than a constructor call, so
quantities display well everywhere: in the REPL, in Jupyter, and inside lists,
arrays and DataFrames.
