Quick Start
===========

This page explains the three things most users need: compressing a patch, saving a compressed file, and reading it back.

Compress a Patch
----------------

Pick a codec and pass it to :func:`~comdas.utils.compress_patch` with your data. The result is an ordinary DASCore patch whose data is held in compressed form.

.. code-block:: python

   import dascore as dc
   from comdas import SVDCodec, compress_patch

   patch = dc.get_example_patch("example_event_2")
   compressed = compress_patch(patch, SVDCodec(rank=20))

   # Same coordinates, attributes, and DASCore methods as before.
   compressed.viz.waterfall(show=True)
   filtered = compressed.pass_filter(time=(None, 100))

   # How much smaller is it?
   ratio = compressed.data.codec.compression_ratio(compressed.data.payload)
   print(f"Compression ratio: {ratio:.1f}x")

When the codec supports it, reading a slice of the data only reconstructs the part you ask for, so data access stays cheap.

Save a Compressed File
----------------------

:func:`~comdas.io.h5_container.write_compressed` compresses data and writes it to a ``COMDAS`` HDF5 file. The source can be a patch, a spool, or a path to any file or directory DASCore can read.

.. code-block:: python

   import dascore as dc
   from comdas import SVDCodec, WaveletCodec, write_compressed

   # From a patch in memory
   patch = dc.get_example_patch("example_event_2")
   write_compressed(patch, "event_svd.h5", SVDCodec(energy=0.90))

   # From raw files on disk
   write_compressed("raw_data/", "archive.h5", WaveletCodec(keep_fraction=0.05))

Writing to a file that already exists appends patches instead of overwriting them. Patches in the same file may use different codecs.

Read a Compressed File
----------------------

Reading ``COMDAS`` files needs only DASCore. As long as ComDAS is installed in the environment, there is no need to import and no codec to specify:

.. code-block:: python

   import dascore as dc

   spool = dc.spool("event_svd.h5")
   patch = spool[0]

   # Metadata and selection work as with any other format.
   print(dc.scan("event_svd.h5"))
   subset = spool.select(distance=(500, 600))
