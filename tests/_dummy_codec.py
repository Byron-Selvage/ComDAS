"""
A dummy lossless codec, used to test the generic Codec and
CompressedArray class behavior.
"""

from dataclasses import dataclass

import numpy as np

from comdas.codecs.base import Codec, CompressedPayload


@dataclass
class DummyPayload(CompressedPayload):
    """
    Stores the original array.

    :ivar data: The unchanged array.
    :vartype data: numpy.ndarray
    """

    data: np.ndarray


class DummyCodec(Codec):
    """
    A dummy lossless Codec.

    Exists for testing the base :class:`~comdas.codecs.base.Codec` interface.
    """

    name = "DUMMY_TEST_CODEC"
    version = "1"

    def encode(self, array: np.ndarray, **kwargs) -> DummyPayload:
        """
        Store ``array`` unchanged.

        :param array: The array to "compress".
        :type array: numpy.ndarray
        :param kwargs: Accepted and ignored.
        :returns: A payload holding an unmodified copy of ``array``.
        :rtype: DummyPayload
        """
        arr = np.asarray(array)
        return DummyPayload(
            original_shape=arr.shape, dtype=arr.dtype, data=arr.copy()
        )

    def decode(self, payload: DummyPayload) -> np.ndarray:
        """
        Return the stored array.

        :param payload: A payload previously produced by :meth:`encode`.
        :type payload: DummyPayload
        :returns: The stored array.
        :rtype: numpy.ndarray
        """
        return payload.data.astype(payload.dtype, copy=False)

    def compressed_size_bytes(self, payload: DummyPayload) -> int:
        """
        Byte size of the stored array.

        :param payload: A payload previously produced by :meth:`encode`.
        :type payload: DummyPayload
        :returns: ``payload.data.nbytes``.
        :rtype: int
        """
        return payload.data.nbytes

    def payload_to_group(self, payload: DummyPayload, group) -> None:
        """
        Write the stored array into ``group`` as a single dataset.

        :param payload: The payload to serialize.
        :type payload: DummyPayload
        :param group: An open, writable ``h5py.Group``.
        :type group: h5py.Group
        """
        group.create_dataset("data", data=payload.data)

    def payload_from_group(
        self, group, *, original_shape: tuple[int, ...], dtype: np.dtype
    ) -> DummyPayload:
        """
        Reconstruct :class:`DummyPayload` from an HDF5 group.

        :param group: An open, readable ``h5py.Group`` previously
            written by :meth:`payload_to_group`.
        :type group: h5py.Group
        :param original_shape: The array shape.
        :type original_shape: tuple[int, ...]
        :param dtype: The array dtype.
        :type dtype: numpy.dtype
        :returns: The reconstructed payload.
        :rtype: DummyPayload
        """
        return DummyPayload(
            original_shape=original_shape, dtype=dtype, data=group["data"][:]
        )


class DummyImmediateWriteCodec(DummyCodec):
    """
    A DummyCodec variant that declares immediate (non-buffered) writes.
    """

    name = "DUMMY_IMMEDIATE_WRITE_TEST_CODEC"
    default_overlay_flush_threshold = 0


class DummyPartialWriteCodec(DummyCodec):
    """
    A DummyCodec variant that implements
    :meth:`~comdas.codecs.base.Codec.partial_write`.

    Allows testing the :meth:`~comdas.codecs.base.Codec.partial_write` and
    :meth:`~comdas.codecs.base.Codec.supports_partial_write` behaviors.
    """

    name = "DUMMY_PARTIAL_WRITE_TEST_CODEC"

    def partial_write(self, payload: DummyPayload, key, value) -> DummyPayload:
        """
        Patch ``payload.data`` directly at ``key``.

        :param payload: The payload before the write.
        :type payload: DummyPayload
        :param key: A NumPy-style index/slice key.
        :param value: The value(s) to write.
        :returns: The same payload, mutated in place.
        :rtype: DummyPayload
        """
        payload.data[key] = value
        return payload


class DummyPartialWriteWithFallbackCodec(DummyCodec):
    """
    A DummyCodec variant whose partial_write only handles single-element
    writes, raising :class:`NotImplementedError` for anything else.

    This allows us to check that the fallback mechanism is applied on a per-call
    basis.
    """

    name = "DUMMY_PARTIAL_WRITE_FALLBACK_TEST_CODEC"

    def partial_write(self, payload: DummyPayload, key, value) -> DummyPayload:
        """
        Patch a single element directly. Error on anything else.

        :param payload: The payload before the write.
        :type payload: DummyPayload
        :param key: A NumPy-style index/slice key.
        :param value: The value(s) to write.
        :returns: The same payload, mutated in place.
        :rtype: DummyPayload
        :raises NotImplementedError: If ``key`` doesn't address exactly
            one element.
        """
        is_single_element = (
            isinstance(key, tuple)
            and len(key) == payload.data.ndim
            and all(isinstance(k, (int, np.integer)) for k in key)
        )
        if not is_single_element:
            raise NotImplementedError(
                "This dummy codec only supports single-element partial writes"
            )
        payload.data[key] = value
        return payload
