"""Compression codec interfaces and implementations."""

from comdas.codecs.base import Codec, CompressedPayload
from comdas.codecs.svd import SVDCodec, SVDPayload
from comdas.codecs.wavelet import WaveletCodec, WaveletPayload

__all__ = [
    "Codec",
    "CompressedPayload",
    "SVDCodec",
    "SVDPayload",
    "WaveletCodec",
    "WaveletPayload",
]
