Codecs
======

Codecs convert dense NumPy arrays into compressed payloads and reconstruct
those arrays on demand. Subclasses of :class:`comdas.Codec` are registered by
their ``name`` so serialized payloads can select the correct decoder.

SVD codec
---------

The included SVD codec supports two-dimensional arrays. Select either a fixed
truncation ``rank`` or a retained ``energy`` fraction in ``(0, 1]``.

.. code-block:: python

   from comdas import SVDCodec

   fixed_rank = SVDCodec(rank=20)
   retained_energy = SVDCodec(energy=0.99)

.. automodule:: comdas.codecs.base
   :members:
   :show-inheritance:

.. automodule:: comdas.codecs.svd
   :members:
   :show-inheritance:
