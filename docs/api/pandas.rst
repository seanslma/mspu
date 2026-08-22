.. _api.pandas:

pandas
======

.. currentmodule:: mspu.pandas

Accessors
~~~~~~~~~

.. autosummary::
   :toctree: api/

   PdHt

.. note::
   Registered as ``df.ht(...)`` on any :class:`pandas.DataFrame`
   via :func:`pandas.api.extensions.register_dataframe_accessor`.

Functions
~~~~~~~~~

.. autosummary::
   :toctree: api/
   :nosignatures:

   df_diffs
   create_empty_df
   explode_date_range
   explode_int_range
   pa_mod
