"""
Tests for :class:`~comdas.arrays.duck_array.DuckArray`,
independent of any codec's behavior.

Uses the test class ``DummyCodec`` to test the base behavior.
"""

import numpy as np
import pytest

from comdas.arrays.duck_array import DuckArray

try:
    from _dummy_codec import (
        DummyCodec,
        DummyImmediateWriteCodec,
        DummyPartialWriteCodec,
        DummyPartialWriteWithFallbackCodec,
    )
except ImportError:
    from tests._dummy_codec import (
        DummyCodec,
        DummyImmediateWriteCodec,
        DummyPartialWriteCodec,
        DummyPartialWriteWithFallbackCodec,
    )


def make_array(m=20, n=15, seed=42):
    """
    Generate a deterministic test array.

    :param m: Number of rows.
    :param n: Number of columns.
    :param seed: RNG seed, for reproducibility.
    :returns: An ``(m, n)`` float64 array.
    :rtype: numpy.ndarray
    """
    rng = np.random.default_rng(seed)
    return rng.normal(size=(m, n))


def test_shape_dtype_full_read():
    """
    shape/dtype should reflect the original array, and __array__ should
    match it exactly since DummyCodec is lossless.
    """
    A = make_array()
    codec = DummyCodec()
    ca = DuckArray(codec.encode(A), codec)
    assert ca.shape == A.shape
    assert ca.dtype == A.dtype
    assert np.array_equal(np.asarray(ca), A)


def test_getitem():
    """
    Indexing should match the plain NumPy indexing of the original array.
    """
    A = make_array()
    codec = DummyCodec()
    ca = DuckArray(codec.encode(A), codec)
    assert np.array_equal(ca[3, 4], A[3, 4])
    assert np.array_equal(ca[2:10, 5:12], A[2:10, 5:12])


def test_single_write_via_overlay():
    """
    A single-element write should go to the overlay, not force a consolidation.
    """
    A = make_array()
    codec = DummyCodec()
    ca = DuckArray(codec.encode(A), codec)

    ca[3, 4] = 999.0
    assert ca.overlay_size == 1
    assert ca[3, 4] == 999.0
    assert ca[0, 0] == A[0, 0]
    assert np.asarray(ca)[3, 4] == 999.0


def test_consolidate_clears_overlay():
    """
    consolidate() should consolidate members of the overlay into the payload
    and empty the overlay.
    """
    A = make_array()
    codec = DummyCodec()
    ca = DuckArray(codec.encode(A), codec)

    ca[1, 1] = 42.0
    ca[2, 2] = -7.0
    ca.consolidate()
    assert ca.overlay_size == 0
    assert ca[1, 1] == 42.0
    assert ca[2, 2] == -7.0


def test_large_write_auto_consolidates():
    """
    A write past the overlay threshold should auto-consolidate.
    """
    A = make_array(m=50, n=50)
    codec = DummyCodec()
    ca = DuckArray(codec.encode(A), codec, max_pending_writes=100)

    block = np.full((20, 20), 5.0)
    ca[10:30, 10:30] = block
    assert ca.overlay_size == 0
    assert np.array_equal(np.asarray(ca)[10:30, 10:30], block)


def test_ufunc_fallback():
    """
    Ordinary NumPy ufuncs should work via the fallback.

    NOTE: When codec-specific ufunc handling is implemented, we may need to
    change or expand this test.
    """
    A = make_array()
    codec = DummyCodec()
    ca = DuckArray(codec.encode(A), codec)

    result = ca + 1.0
    assert np.allclose(result, A + 1.0)


def test_threshold_defaults_from_codec():
    """
    Without override, the overlay threshold should come from
    the codec's default max_pending_writes.
    """
    A = make_array()
    codec = DummyCodec()
    ca = DuckArray(codec.encode(A), codec)
    assert ca._max_pending_writes == codec.max_pending_writes


def test_zero_threshold_codec_never_buffers_writes():
    """
    A codec that declares max_pending_writes=0 should consolidate
    immediately on every write.
    """
    A = make_array()
    codec = DummyImmediateWriteCodec()
    ca = DuckArray(codec.encode(A), codec)

    ca[3, 4] = 999.0
    assert ca.overlay_size == 0, (
        "A zero-threshold codec should never buffer writes"
    )
    assert ca[3, 4] == 999.0


def test_partial_write_codec_bypasses_overlay():
    """
    A codec implementing partial_write should write to the payload
    directly without ever using the overlay.
    """
    A = make_array()
    codec = DummyPartialWriteCodec()
    ca = DuckArray(codec.encode(A), codec)

    ca[3, 4] = 999.0
    assert ca.overlay_size == 0
    assert ca[3, 4] == 999.0

    ca[0:2, 0:2] = np.full((2, 2), -1.0)
    assert ca.overlay_size == 0
    assert np.array_equal(np.asarray(ca)[0:2, 0:2], np.full((2, 2), -1.0))


def test_partial_write_fallback_is_per_call():
    """
    A codec whose partial_write only handles some keys should fall
    back to the overlay/threshold path for the keys it can't.
    """
    A = make_array()
    codec = DummyPartialWriteWithFallbackCodec()
    ca = DuckArray(codec.encode(A), codec, max_pending_writes=10)

    # single element: able to be handled by partial_write
    ca[3, 4] = 999.0
    assert ca.overlay_size == 0
    assert ca[3, 4] == 999.0

    # a slice: unable to be handled by this codec's partial_write
    # this should end up in the overlay
    ca[0:2, 0:2] = np.full((2, 2), -1.0)
    assert ca.overlay_size == 4
    assert np.array_equal(np.asarray(ca)[0:2, 0:2], np.full((2, 2), -1.0))

    # Check if the overlay is auto-consolidated and cleared
    ca[10:13, 10:13] = np.full((3, 3), 7.0)
    assert ca.overlay_size == 0
    assert np.array_equal(np.asarray(ca)[10:13, 10:13], np.full((3, 3), 7.0))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
