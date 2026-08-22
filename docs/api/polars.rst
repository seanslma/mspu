.. _api.polars:

polars
======

.. currentmodule:: mspu.polars

Accessors
~~~~~~~~~

.. autosummary::
   :toctree: api/

   PlHt

.. note::
   Registered as ``df.ht(...)`` on any :class:`polars.DataFrame`
   via :func:`polars.api.register_dataframe_namespace`.

Functions
~~~~~~~~~

.. autosummary::
   :toctree: api/
   :nosignatures:

   inf_count
   nan_count
   nul_count
   lowercase_polars_df
   to_float32_polars_df
