Compressed Arrays
=================

``DuckArray`` presents a compressed payload through NumPy's array protocols.
Reads use the codec's partial decoder when available. Writes use efficient
codec-specific updates or a sparse overlay that is consolidated when its
configured threshold is reached.

Operations unsupported directly by the compressed representation materialize
the data as a NumPy array.

.. automodule:: comdas.arrays.duck_array
   :members:
   :show-inheritance:
