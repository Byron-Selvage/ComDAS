"""
Utility functions for working with compressed patches.
Includes:
- :func:`compress_patch` Compress an in-memory DASCore patch's data using a specified codec.
"""

from __future__ import annotations

import numpy as np

from comdas.arrays.duck_array import DuckArray
from comdas.codecs.base import Codec


def compress_patch(patch, codec: Codec, **encode_kwargs):
    """
    Return a new ``dascore.Patch`` whose data is compressed with ``codec``.

    Coords and attrs are unchanged. The returned Patch is an ordinary Patch
    (via ``patch.new``) with the internal data replaced by a
    :class:`~comdas.arrays.duck_array.DuckArray`.

    :param patch: The uncompressed source patch.
    :type patch: dascore.Patch
    :param codec: The codec to compress ``patch.data`` with.
    :type codec: Codec
    :param encode_kwargs: Forwarded verbatim to ``codec.encode`.
    :returns: A new Patch with the same coords/attrs, backed by a
        :class:`~comdas.arrays.duck_array.DuckArray`.
    :rtype: dascore.Patch
    """
    dense = np.asarray(patch.data)
    payload = codec.encode(dense, **encode_kwargs)
    compressed_array = DuckArray(payload, codec)
    return patch.new(data=compressed_array)
