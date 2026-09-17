"""
I/O support for ComDAS patches.

Importing this subpackage registers the ``COMDAS`` HDF5 container
format (:class:`~comdas.io.h5_container.ComdasV1`) with DASCore's
FiberIO manager, so ``dc.spool(path)`` / ``dc.read(...)`` / ``dc.write(...)``
work with it directly. :func:`~comdas.io.h5_container.write_compressed`
is a small convenience wrapper for the write side.
"""

from comdas.io.h5_container import (
    ComdasV1,
    FORMAT_NAME,
    FORMAT_VERSION,
    write_compressed,
)

__all__ = ["ComdasV1", "FORMAT_NAME", "FORMAT_VERSION", "write_compressed"]
