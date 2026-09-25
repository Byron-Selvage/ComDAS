"""
Tests for the base :class:`~comdas.codecs.base.Codec` interface.
"""

import numpy as np
import pytest

from comdas.codecs.base import Codec

# Imports are stupid
try:
    from _dummy_codec import DummyCodec, DummyPartialWriteCodec
except ImportError:
    from tests._dummy_codec import DummyCodec, DummyPartialWriteCodec


def test_subclass_self_registers():
    """
    Codec subclasses should be discoverable by name after class creation.
    """
    assert Codec.get_registered("DUMMY_TEST_CODEC") is DummyCodec
    assert (
        Codec.get_registered("DUMMY_PARTIAL_WRITE_TEST_CODEC")
        is DummyPartialWriteCodec
    )


def test_get_registered_unknown_name_raises():
    """
    Looking up an unregistered name should raise a KeyError.
    """
    try:
        Codec.get_registered("They're_taking_the_hobbits_to_Isengard")
    except KeyError:
        pass
    else:
        raise AssertionError("Expected KeyError for an unregistered codec name")


def test_concrete_subclass_without_name_raises():
    """
    A Codec subclass that forgets to set `name` should
    fail at class-definition time.
    """
    try:

        class _Unnamed(Codec):
            def encode(self, array, **kwargs):
                raise NotImplementedError

            def decode(self, payload):
                raise NotImplementedError

            def compressed_size_bytes(self, payload):
                raise NotImplementedError

            def payload_to_group(self, payload, group):
                raise NotImplementedError

            def payload_from_group(self, group, *, original_shape, dtype):
                raise NotImplementedError
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for a nameless Codec subclass"
        )


def test_incomplete_subclass_does_not_register():
    """
    An abstract subclass should raise a TypeError when instantiated.
    """

    class _Incomplete(Codec):
        name = "SHOULD_NOT_REGISTER"

        def encode(self, array, **kwargs):
            raise NotImplementedError

        # decode, compressed_size_bytes, payload_to_group, payload_from_group
        # intentionally left unimplemented

    try:
        _Incomplete()
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Expected TypeError instantiating an incomplete Codec subclass"
        )


def test_compression_ratio():
    """
    compression_ratio should be original_bytes / compressed_size_bytes.
    """
    codec = DummyCodec()
    A = np.zeros((10, 10), dtype=np.float64)
    payload = codec.encode(A)
    # DummyCodec stores the array uncompressed so ratio should be ~1.0
    assert np.isclose(codec.compression_ratio(payload), 1.0)


def test_partial_write_default_raises_not_implemented():
    """
    The base class's default partial_write should always raise a
    NotImplementedError.
    """
    codec = DummyCodec()
    A = np.zeros((3, 3))
    payload = codec.encode(A)
    try:
        codec.partial_write(payload, (0, 0), 1.0)
    except NotImplementedError:
        pass
    else:
        raise AssertionError(
            "Expected NotImplementedError from the default partial_write"
        )


def test_supports_partial_write_reflects_override():
    """
    supports_partial_write should be False for a codec that hasn't
    overridden partial_write, and True for one that has.
    """
    assert DummyCodec().supports_partial_write() is False
    assert DummyPartialWriteCodec().supports_partial_write() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
