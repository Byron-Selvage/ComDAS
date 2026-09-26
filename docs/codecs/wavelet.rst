Wavelet Codec
=============

:class:`~comdas.codecs.wavelet.WaveletCodec` compresses data by transforming it into a wavelet basis and keeping only the largest coefficients.

For background on the method, see the `PyWavelets documentation <https://pywavelets.readthedocs.io/>`__.

Configuration
-------------

Set exactly one of ``keep_fraction`` or ``threshold``.

.. list-table::
   :header-rows: 1
   :widths: 18 18 64

   * - Option
     - Type
     - Meaning
   * - ``wavelet``
     - ``str``
     - PyWavelets wavelet name (default ``"db4"``). Any discrete wavelet from
       ``pywt.wavelist(kind="discrete")``, e.g. ``"haar"``, ``"db2"``,
       ``"sym8"``, ``"coif3"``, ``"bior4.4"``. 
   * - ``mode``
     - ``str``
     - PyWavelets signal extension mode (default ``"symmetric"``). See
       ``pywt.Modes.modes``.
   * - ``keep_fraction``
     - ``float`` in ``(0, 1]``
     - Fraction of all coefficients to keep. Gives a predictable compression
       ratio.
   * - ``threshold``
     - ``float`` ``>= 0``
     - Keep coefficients with magnitude greater than this value. Gives a
       predictable noise floor.

As with all codecs, constructor options act as defaults and can be overridden per call:

.. code-block:: python

   codec = WaveletCodec(wavelet="sym8", keep_fraction=0.05)
   compress_patch(patch, codec)                      # 5% of coefficients
   compress_patch(patch, codec, keep_fraction=0.01)  # 1% for this call only
   compress_patch(patch, codec, wavelet="haar")      # different wavelet


Example
-------

.. code-block:: python

   import numpy as np
   import dascore as dc
   from comdas import WaveletCodec, compress_patch

   patch = dc.get_example_patch("example_event_2")

   for wavelet in ("haar", "db4", "sym8"):
       codec = WaveletCodec(wavelet=wavelet, keep_fraction=0.05)
       compressed = compress_patch(patch, codec)
       error = np.linalg.norm(patch.data - np.asarray(compressed.data))
       error /= np.linalg.norm(patch.data)
       ratio = codec.compression_ratio(compressed.data.payload)
       print(f"{wavelet:5s} ratio={ratio:5.1f}x  relative error={error:.3f}")

API
---

See the :doc:`module reference </api/generated/comdas.codecs.wavelet>`.
