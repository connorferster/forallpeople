Physical
========

.. currentmodule:: forallpeople

.. autoclass:: Physical
   :members: display, prefix, round, sqrt, split, to, si, to_dict, from_dict, repr
   :no-undoc-members:

   Quantities are usually made by multiplying numbers by units
   (``5 * si.kN``), not by calling the constructor. Instances are immutable.

   .. attribute:: value
      :type: float

      The magnitude of the quantity in SI base units. It does not depend on
      the environment or on how the quantity is displayed.

   .. attribute:: dimensions
      :type: Dimensions

      The powers of the seven SI base units (``kg, m, s, A, cd, K, mol``).

   .. attribute:: factor
      :type: int | float | fractions.Fraction

      The scale from SI base units to a non-SI unit (e.g. ``1/0.3048`` for
      feet), or ``1``.

   .. attribute:: precision
      :type: int

      The number of decimal places displayed. Change it with ``round()``.

   .. attribute:: prefixed
      :type: str

      The SI prefix to display the quantity with (e.g. ``"k"``), or ``""``
      to choose one automatically. Set it with :meth:`prefix`.

   .. property:: latex
      :type: str

      The quantity as LaTeX, e.g. ``322.657\ \mathrm{N}``.

   .. property:: html
      :type: str

      The quantity as HTML.

.. autoclass:: Display
   :no-members:

   How a quantity is displayed, returned by :meth:`Physical.display`.

   .. attribute:: magnitude
      :type: float

      The number shown.

   .. attribute:: unit
      :type: str

      The unit shown, with its prefix, e.g. ``"mm"`` or ``"kip·ft"``.

   .. attribute:: factor
      :type: int | float | fractions.Fraction

      ``magnitude == value * factor``, where ``value`` is the SI value. An
      exact ``Fraction`` for a defined unit or an SI prefix.

.. autoclass:: forallpeople.dimensions.Dimensions
   :no-members:

   The powers of the SI base units of a quantity, in the order
   ``kg, m, s, A, cd, K, mol``.

.. autoexception:: forallpeople.dimensions.DimensionError
