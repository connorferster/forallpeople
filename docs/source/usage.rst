Basic Usage
^^^^^^^^^^^

The basic usage is to import and, optionally, define your units environment.

Imports
=======

There are two ways you can import: the standard method or the "star import" method,
depending on your use case.

For writing scripts that you intended to reuse, the standard import is recommended:

.. code-block:: python
    :linenos:

    import forallpeople as si
    si.environment()

This will load the library and make the SI base units (i.e. :code:'si.m, si.kg, si.s, si.A,
si.cd, si.K, si.mol') available for you to use. The :code:'si.environment()' function
loads the default "derived units" that are part of SI unit system (e.g.
:code:'si.N, si.Pa, si.W', etc.).

See :ref:'usage' for examples.

"Star imports" can also be performed if you do not wish to have a module prefix on
your units: instead of :code:'si.kg', you would prefer to just have to type, :code:'kg'.

The use case for this is for performing quick calculations in Jupyter or IPython,
however, it is not recommended to do this for any permanent calculation scripts
or programs that your write because it has a tendency to clutter the global namespace
with units variables you may not need.

.. code-block:: python
    :linenos:

    from forallpeople import *
    environment()
    from forallpeople import *

Why the "double import"? The first import opens the library. The :code:'environment()'
function call loads the "units environment" into memory and instantiates additional
units objects for use but they are confined to the module namespace. The second import
then loads those instantiated units into your global working namespace for use.

Usage
=====

The SI units are all instances of a single class called, :code:'Physical', as in, a
"Physical quantity" or a "Physical property". The :code:'Physical' class is nothing
more than a :code:'NamedTuple' with additional methods applied.

You assign a value to a :code:'Physical' through multiplication or division:

.. code-block:: python
    :linenos:
    [In]   5.25 * si.kg
    [Out]  5.250 kg

    [In]   2 / si.m
    [Out]  2.000 m⁻¹

**Note: Because each unit is an instance of Physical and Physical is a NamedTuple,
Physical instances are *immutable*, much like ints and floats.**
