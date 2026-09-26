Add a Codec
===========

Every compression method in ComDAS is a *codec* implemented as a subclass of :class:`~comdas.codecs.base.Codec` paired with a :class:`~comdas.codecs.base.CompressedPayload` that holds the compressed data.

What a Codec Needs
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Member
     - Purpose
   * - ``name`` (class attribute)
     - Unique string. It's saved in files and used to find the codec when
       reading.
   * - ``version`` (class attribute)
     - Bump this when the payload layout changes incompatibly.
   * - ``encode(array, **kwargs)``
     - Compress a dense NumPy array into a payload.
   * - ``decode(payload)``
     - Reconstruct the dense array.
   * - ``compressed_size_bytes(payload)``
     - Bytes used by the payload. Used by
       :meth:`~comdas.codecs.base.Codec.compression_ratio`.
   * - ``payload_to_group(payload, group)``
     - Write the payload's arrays/attributes into an ``h5py.Group``.
   * - ``payload_from_group(group, *, original_shape, dtype)``
     - Rebuild the payload from that group.

Optional overrides:

* ``decode_partial(payload, key)``: reconstruct only ``array[key]``. The
  default decodes everything and then indexes.
* ``partial_write(payload, key, value)``: apply ``array[key] = value`` directly
  to the payload. Raise :class:`NotImplementedError` for cases you can't handle
  and ComDAS falls back to buffered writes.
* ``max_pending_writes`` (class attribute): how many buffered writes to allow
  before re-compressing (default 10,000).
* ``CompressedPayload.compression_params``: a ``dict`` describing the settings
  used, for inspection.

The file container already stores the original shape, dtype, coordinates, patch attributes, and codec name/version. Only store what your codec needs in ``payload_to_group``.

.. seealso::

   The `source code of the built-in codecs <https://github.com/Byron-Selvage/ComDAS/tree/main/comdas/codecs>`__ for complete examples.

Registration
------------

Defining the subclass registers it under its ``name``. There is nothing else to
call. Because registration happens when the class is defined, **the module
containing your codec must be imported before reading files that use it**.
Built-in codecs are always available. For a custom codec, import it first:

.. code-block:: python

   import my_package.codecs  # registers your custom codec
   import dascore as dc

   # files using your custom codec can now be read
   patch = dc.spool("your_file.h5")[0]

Reading a file whose codec isn't registered raises a :class:`KeyError` listing the known codec names.

Codec constructor arguments
---------------------------

When reading a file, ComDAS instantiates the codec with no arguments. Give every constructor argument a default, and store any setting needed for decoding in the payload rather than on the codec instance.

Contributing a codec
--------------------

To add a codec to ComDAS itself:

#. Add a module under ``comdas/codecs/`` and export the codec and payload from
   ``comdas/codecs/__init__.py`` and ``comdas/__init__.py``.
#. Add tests to ``tests/test_codecs.py`` covering round trips, partial
   decoding, and HDF5 serialization.
#. Add a page to ``docs/codecs/`` following the layout of the existing codec
   pages, and list it in the *Codecs* toctree in ``docs/index.rst``.
#. Open a pull request on GitHub to have your codec included in the main repository.
   Thank you for contributing!

API
---

See the :doc:`module reference </api/generated/comdas.codecs.base>`.
