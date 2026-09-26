"""
ComDAS: compressed DAS patches for DASCore.

ComDAS patches work identically to normal ``dascore.Patch`` objects,
but the data they hold is stored compressed in memory
(:class:`~comdas.arrays.compressed_array.CompressedArray`) and
decompressed on access. Compression is controlled via
the :class:`~comdas.codecs.base.Codec` interface. Both the in-memory
array and the on-disk ``COMDAS`` container format
(:mod:`comdas.io.h5_container`) are codec-agnostic, working with any
registered codec by name rather than hardcoding a specific one.
"""

from comdas.codecs.base import Codec, CompressedPayload
from comdas.codecs.svd import SVDCodec, SVDPayload
from comdas.codecs.wavelet import WaveletCodec, WaveletPayload
from comdas.arrays.duck_array import DuckArray

__all__ = [
    "Codec",
    "CompressedPayload",
    "SVDCodec",
    "SVDPayload",
    "WaveletCodec",
    "WaveletPayload",
    "DuckArray",
]

try:
    from comdas.utils import compress_patch  # requires dascore installed
    from comdas.io import write_compressed  # noqa: F401 -- also self-registers the COMDAS FiberIO plugin

    __all__ += ["compress_patch", "write_compressed"]
except ImportError:  # pragma: no cover
    pass
