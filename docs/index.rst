ComDAS
======

ComDAS (Compressed DAS) lets you store and work with compressed distributed acoustic sensing (DAS) data using ordinary `DASCore <https://dascore.org/>`_ tools.

With ComDAS you can:

* **Shrink DAS data in memory.** Compress a DASCore patch and keep using it like any other.
* **Save compressed files.** Write patches, spools, or whole directories of raw data to a compressed HDF5 file or files.
* **Read compressed files with plain DASCore.** Once ComDAS is installed, ``dascore.spool()`` opens compressed files directly without needing to know how the data was compressed.
* **Choose your compression level.** Pick a codec and set how much detail to keep, from near-lossless to aggressive compression.
* **Implement your own algorithm.** Add a new compression method by writing a codec class.

Available Codecs
----------------

.. list-table::
   :header-rows: 1
   :widths: 20 35 45

   * - Codec
     - Main setting
     - Reference
   * - :doc:`SVD <codecs/svd>`
     - ``rank`` or retained ``energy``
     - `Numpy SVD <https://numpy.org/doc/1.22/reference/generated/numpy.linalg.svd.html>`__
   * - :doc:`Wavelet <codecs/wavelet>`
     - ``keep_fraction`` or ``threshold``
     - `PyWavelets <https://doi.org/10.21105/joss.01237>`__;
       `DeVore et al. (1992) <https://doi.org/10.1109/18.119733>`__

.. note::

   ComDAS is under active development. The file format and public API may change between releases.

.. toctree::
   :hidden:
   :caption: Getting started

   installation
   quickstart

.. toctree::
   :hidden:
   :caption: Codecs

   codecs/svd
   codecs/wavelet
   codecs/add_a_codec

.. toctree::
   :hidden:
   :caption: Examples

   examples/compression_comparison

.. toctree::
   :hidden:
   :caption: Reference

   api/index
