PyClip API
==========

To support multiple platforms, PyClip's API is composed of several implementations.

Generally, the public API is provided by ``__init__.py``:

``__init__.py``


.. automodule:: pyclip.__init__
   :members:
   :undoc-members:


Here you will find auto-generated API docs for modules contained herein. Loosely,
each platform implementation will have its own module.

The base class from which all implementations are derived is in the :py:mod:`pyclip.base` module.


.. toctree::
   :maxdepth: 3
   :caption: Contents:
   :glob:

   *


Other modules:


``__main__.py``

Simple entrypoint for calling pyclip via ``python -m pyclip``. Uses :py:mod:`pyclip.cli.main` as entrypoint.
