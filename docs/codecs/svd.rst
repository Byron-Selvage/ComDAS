SVD Codec
=========

:class:`~comdas.codecs.svd.SVDCodec` compresses a 2D patch with a truncated singular value decomposition.

For background on the method, see
`low-rank approximation <https://en.wikipedia.org/wiki/Low-rank_approximation>`__.

Configuration
-------------

Set exactly one of ``rank`` or ``energy``.

.. list-table::
   :header-rows: 1
   :widths: 15 15 70

   * - Option
     - Type
     - Meaning
   * - ``rank``
     - ``int``
     - Number of singular values to keep. Higher ranks keep more detail and
       compress less. Gives a predictable compression ratio.
   * - ``energy``
     - ``float`` in ``(0, 1]``
     - Fraction of the signal energy to keep. Gives a predictable error.

Options given to the constructor act as defaults. They can be overridden for a single call by passing them to :func:`~comdas.utils.compress_patch` or :func:`~comdas.io.h5_container.write_compressed`:

.. code-block:: python

   codec = SVDCodec(rank=20)
   compress_patch(patch, codec)             # rank 20
   compress_patch(patch, codec, rank=5)     # rank 5 for this call only
   compress_patch(patch, codec, energy=0.9) # use energy criterion for this call

Example
-------

.. code-block:: python

   import numpy as np
   import dascore as dc
   from comdas import SVDCodec, compress_patch

   patch = dc.get_example_patch("example_event_2")

   codec = SVDCodec(energy=0.9)
   compressed = compress_patch(patch, codec)
   payload = compressed.data.payload
   error = np.linalg.norm(patch.data - np.asarray(compressed.data))
   error /= np.linalg.norm(patch.data)
   print(
       f"rank={payload.rank:4d}  "
       f"ratio={codec.compression_ratio(payload):6.1f}x  "
       f"relative error={error:.3f}"
   )

Limitations
-----------

* Only 2D data is supported.
* Encoding computes a full SVD, so very large patches may be slow to compress. Decoding is fast.

API
---

See the :doc:`module reference </api/generated/comdas.codecs.svd>`.
