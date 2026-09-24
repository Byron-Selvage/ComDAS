ComDAS
******

ComDAS (Compressed DAS) is a companion package to
`DASCore <https://dascore.org/>`_ for storing and working with compressed
distributed acoustic sensing data.

ComDAS currently provides:

* A NumPy-compatible duck array backed by compressed data.
* A codec interface for adding compression algorithms.
* Lossy, truncated-SVD compression for two-dimensional arrays.
* A codec-agnostic HDF5 format registered with DASCore's I/O system.

.. note::

   ComDAS is under active development. The file format and public API may
   change between releases.

Installation
------------
Install from PyPI:

.. code-block:: bash

   pip install comdas

Install from source:

.. code-block:: bash

   git clone https://github.com/byron-selvage/comdas.git
   cd comdas
   pip install -e .

Quick Start
-----------

Compress an in-memory DASCore patch with a fixed SVD rank:

.. code-block:: python

   import numpy as np
   import dascore as dc
   from comdas import SVDCodec, compress_patch

   patch = dc.get_example_patch()
   compressed = compress_patch(patch, SVDCodec(rank=20))

   # Compressed data supports normal array access and can be materialized.
   subset = compressed.data[:10, :100]
   dense = np.asarray(compressed.data)

Write compressed patches to disk and read them through DASCore:

.. code-block:: python

   import dascore as dc
   from comdas import SVDCodec, write_compressed

   patch = dc.get_example_patch()
   write_compressed(patch, "compressed.h5", SVDCodec(rank=20))

   spool = dc.spool("compressed.h5")
   restored_patch = spool[0]

SVD compression is lossy. Choose a fixed ``rank`` or an ``energy`` fraction
according to the reconstruction quality and storage cost your data requires.

.. toctree::
   :hidden:
   :maxdepth: 2

   codecs
   arrays
   io