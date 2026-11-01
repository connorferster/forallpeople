Environments
============

.. currentmodule:: forallpeople

.. function:: environment(env_name="", top_level=False)

   Loads the units environment ``env_name``: its units become variables of
   the ``forallpeople`` module (or, with ``top_level=True``, top-level
   variables), and quantities are displayed in its units.

   ``env_name`` is the name of a bundled environment (``"default"``,
   ``"structural"``, ``"us_customary"``, ``"electrical"``, ``"thermal"``) or
   the path to an environment JSON file. A :class:`pathlib.Path`, or a string
   ending in ``.json``, is always treated as a path. With no arguments, prints
   the units that are loaded.

   ``environment`` is the single instance of
   :class:`~forallpeople.environment.Environment`. See :doc:`../guide/environments`.

.. autoclass:: forallpeople.environment.Environment
   :members: parse, parse_tree
   :no-undoc-members:

.. autofunction:: forallpeople.environment.evaluate_factor_expression
