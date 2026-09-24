I/O
===

ComDAS provides a codec-agnostic HDF5 container named ``COMDAS``. Installing
the package registers the format with DASCore, so files written by
:func:`comdas.write_compressed` can be opened with :func:`dascore.spool`.

Writing to an existing COMDAS file appends patches. Each patch records its
codec and compression parameters, allowing one container to hold data encoded
with different registered codecs.

.. automodule:: comdas.io.h5_container
    :members:
    :exclude-members: FORMAT_NAME, FORMAT_VERSION