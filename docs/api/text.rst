Parsing and JSON
================

.. currentmodule:: forallpeople

Parsing
-------

.. autofunction:: parse

.. autofunction:: parse_tree

.. autoexception:: UnitParseError

JSON
----

.. autofunction:: dumps

.. autofunction:: dump

.. autofunction:: loads

.. autofunction:: load

.. autofunction:: json_default

.. autofunction:: json_object_hook

YMPrint plugin
--------------

See :doc:`../guide/ymprint`. YMPrint calls ``setup()`` through its
``ymprint.plugins`` entry point; the other functions are what it registers.

.. autofunction:: forallpeople.ymprint_plugin.setup

.. autofunction:: forallpeople.ymprint_plugin.serialize

.. autofunction:: forallpeople.ymprint_plugin.decode

.. autofunction:: forallpeople.ymprint_plugin.load_yaml_with_units
