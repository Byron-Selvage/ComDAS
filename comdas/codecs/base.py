"""
Base classes for compression codecs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass
class CompressedPayload:
    """
    Base container for a codec's compressed payload (representation of an array).

    Codecs should subclass this to hold the arrays/parameters the method requires.

    :ivar original_shape: The shape of the array before compression.
    :vartype original_shape: tuple[int, ...]
    :ivar dtype: The data type of the array before compression.
    :vartype dtype: numpy.dtype
    """

    original_shape: tuple[int, ...]
    dtype: np.dtype


class Codec(ABC):
    """
    Base class for all codecs.

    A codec is responsible for compressing and decompressing arrays. It knows
    how to turn a dense NumPy array into a :class:`CompressedPayload` and back,
    and how to (de)serialize that payload to/from an HDF5 file.

    Subclasses are auto-registered by name on class creation. This allows
    the reader to automatically recognize and use the appropriate codec by name,
    without having to import every codec.

    :cvar name: Unique, human-readable name for the codec.
    :vartype name: str
    :cvar version: Codec format version, bumped if the codec's payload
        structure changes in a way that is not backward-compatible.
    :vartype version: str
    """

    name: str = ""
    version: str = "1"

    _registry: dict[str, type[Codec]] = {}

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register ``cls`` in the registry under ``cls.name``.

        :param kwargs: Forwarded to :meth:`object.__init_subclass__`.
        :raises ValueError: If a concrete subclass doesn't set a
            non-empty ``name``.
        """
        super().__init_subclass__(**kwargs)
        if getattr(cls, "__abstractmethods__", None):
            return
        if not cls.name:
            raise ValueError(
                f"{cls.__name__} must define a `name` for codec registration."
            )
        Codec._registry[cls.name] = cls

    @classmethod
    def get_registered(cls, name: str) -> type[Codec]:
        """
        Look up a codec class by name.

        :param name: The codec's ``name`` attribute.
        :type name: str
        :returns: The codec class registered under ``name``.
        :rtype: type[Codec]
        :raises KeyError: If no codec is registered under ``name``.
        """
        try:
            return cls._registry[name]
        except KeyError as err:
            raise KeyError(
                f"No codec registered under name {name!r}. Known codecs: {sorted(cls._registry)}"
            ) from err

    @abstractmethod
    def encode(self, array: np.ndarray, **kwargs) -> CompressedPayload:
        """
        Compress ``array`` into a :class:`CompressedPayload`.

        :param array: The dense array to compress.
        :type array: numpy.ndarray
        :param kwargs: Codec-specific compression parameters.
        :returns: The compressed payload.
        :rtype: CompressedPayload
        """

    @abstractmethod
    def decode(self, payload: CompressedPayload) -> np.ndarray:
        """
        Fully decompress the payload.

        :param payload: A payload previously produced by :meth:`encode`.
        :type payload: CompressedPayload
        :returns: The decompressed array.
        :rtype: numpy.ndarray
        """

    def decode_partial(self, payload: CompressedPayload, key) -> np.ndarray:
        """
        Partially decompress the payload, reconstructing only the elements
        addressed by ``key``.

        The default implementation uses a full decode. Codecs that support
        partial decompression or random access read/write should overwrite
        this method.

        :param payload: A payload previously produced by :meth:`encode`.
        :type payload: CompressedPayload
        :param key: A NumPy-style index/slice key.
        :returns: The requested subset of the reconstructed array.
        :rtype: numpy.ndarray
        """
        return self.decode(payload)[key]

    @abstractmethod
    def compressed_size_bytes(self, payload: CompressedPayload) -> int:
        """
        Get the total size, in bytes, of everything stored in ``payload``.

        :param payload: A payload previously produced by :meth:`encode`.
        :type payload: CompressedPayload
        :returns: Total size in bytes of the payload's stored arrays.
        :rtype: int
        """

    def compression_ratio(self, payload: CompressedPayload) -> float:
        """
        Helper to determine the compression ratio of the payload.

        :param payload: A payload previously produced by :meth:`encode`.
        :type payload: CompressedPayload
        :returns: Original bytes divided by compressed bytes.
        :rtype: float
        """
        original_bytes = (
            int(np.prod(payload.original_shape))
            * np.dtype(payload.dtype).itemsize
        )
        return original_bytes / self.compressed_size_bytes(payload)

    @abstractmethod
    def payload_to_group(self, payload: CompressedPayload, group) -> None:
        """
        Write this codec's own arrays/params into an open HDF5 group.

        Only codec-specific data belongs here. The general ``COMDAS``
        container already writes ``original_shape``, ``dtype``,
        ``codec_name``, and ``codec_version`` at the container level
        before calling this. Don't duplicate those fields.

        :param payload: The payload to serialize.
        :type payload: CompressedPayload
        :param group: An open, writable ``h5py.Group`` dedicated to
            this one patch.
        :type group: h5py.Group
        """

    @abstractmethod
    def payload_from_group(
        self, group, *, original_shape: tuple[int, ...], dtype: np.dtype
    ) -> CompressedPayload:
        """
        Reconstruct this codec's payload from an HDF5 group.

        :param group: An open, readable ``h5py.Group`` previously
            written by :meth:`payload_to_group`.
        :type group: h5py.Group
        :param original_shape: The array shape, as already read from
            the container's own (codec-independent) attributes.
        :type original_shape: tuple[int, ...]
        :param dtype: The array dtype, as already read from the
            container's own (codec-independent) attributes.
        :type dtype: numpy.dtype
        :returns: The reconstructed payload.
        :rtype: CompressedPayload
        """
