"""Compression codec interfaces and implementations."""

from comdas.codecs.base import Codec, CompressedPayload
from comdas.codecs.svd import SVDCodec, SVDPayload

__all__ = ["Codec", "CompressedPayload", "SVDCodec", "SVDPayload"]
