.. forallpeople documentation master file, created by
   sphinx-quickstart on Wed May 15 09:20:02 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Forallpeople: SI Units Library for Daily Calculation Work
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. class:: center
The metric system (now SI system):
*"For all time. For all people."*
- Nicolas de Caritat (Marquis de Condorcet)

Forallpeople is a robust library for performing units-aware calculations in Python.
It has a small code base and favours "convention over configuration", although the
actual units environment you work in is fully customizable.

There are other units packages out there but Forallpeople is designed for fast and
simple daily use: units act as you would expect (they automatically combine and
cancel out), they are labelled as you would expect (e.g. 'm' for meter, 'kg' for
kilogram), unit quantities exist independently (e.g. without a "units registry"),
and are ready-to-go with an import (and optional function call).

Intended users: working engineers, scientists, teachers, and students who want to be
able to check any calculations for dimension errors, print formatted calculation
reports and summaries with Jupyter/IPython, and focus on productivity instead of
fussing with managing units and dimensions.

.. toctree::
   :maxdepth: 2
   :caption: Using the Library
   install
   usage
   examples
   integration_with_other_libraries_numpy_etc

.. toctree::
 :maxdepth: 2
 :caption: Motivation and design
 si_units
 named_tuple
 vector_based
 auto_prefixing


 usage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
