"""
Codec tests. Defines a base codec test class for tests all codecs should run and pass.

Each codec should create a concrete test class that inherits from ``CodecContract``,
implement make_codec, and include additional codec-specific tests.
"""

from abc import ABC, abstractmethod

import dascore as dc
import h5py
import numpy as np
import pytest

from comdas import write_compressed
from comdas.arrays.duck_array import DuckArray
from comdas.codecs.base import Codec
from comdas.codecs.svd import SVDCodec


def make_random_matrix(m=40, n=60, seed=42):
    """
    Build a random test matrix.
    """
    return np.random.default_rng(seed).normal(size=(m, n))


class CodecContract(ABC):
    """
    Tests inherited by every concrete codec test class.
    """

    @abstractmethod
    def make_codec(self) -> Codec:
        """
        Return a codec configured to encode the shared test array.
        """

    def test_name_registers(self):
        """
        Check the codec gets registered correctly.
        """
        codec = self.make_codec()
        assert codec.name
        assert Codec.get_registered(codec.name) is type(codec)

    def test_file_roundtrip(self, tmp_path):
        """
        Test that the codec read/writes to a file.
        """
        codec = self.make_codec()
        array = make_random_matrix()
        example = dc.get_example_patch()
        patch = example.new(
            data=array,
            coords={
                dim: example.coords.get_coord(dim)[:length]
                for dim, length in zip(example.dims, array.shape)
            },
        )
        path = tmp_path / "compressed.h5"

        write_compressed(patch, path, codec)
        read_back = list(dc.spool(path))

        assert len(read_back) == 1
        assert isinstance(read_back[0].data, DuckArray)
        assert read_back[0].data.codec.name == codec.name
        np.testing.assert_allclose(
            np.asarray(read_back[0].data), codec.decode(codec.encode(array))
        )

    def test_payload_group_roundtrip(self, tmp_path):
        """
        Test that the codec can write its payload to an HDF5 group and read it back.
        """
        codec = self.make_codec()
        array = make_random_matrix()
        payload = codec.encode(array)
        path = tmp_path / "payload.h5"

        with h5py.File(path, "w") as file:
            group = file.create_group("payload")
            codec.payload_to_group(payload, group)

        with h5py.File(path, "r") as file:
            restored = codec.payload_from_group(
                file["payload"],
                original_shape=payload.original_shape,
                dtype=payload.dtype,
            )

        assert restored.original_shape == array.shape
        assert restored.dtype == array.dtype
        np.testing.assert_allclose(codec.decode(restored), codec.decode(payload))

    def test_decode_partial_matches_full_decode(self):
        """
        If partial decoding is implemented for the codec, check that it returns
        the same values as the full decode.
        """
        codec = self.make_codec()
        if type(codec).decode_partial is Codec.decode_partial:
            pytest.skip("codec does not implement decode_partial")

        payload = codec.encode(make_random_matrix())
        full = codec.decode(payload)
        for key in [
            (3, 4),
            (slice(2, 10), slice(5, 20)),
            (5, slice(None)),
            (slice(None), 7),
        ]:
            np.testing.assert_allclose(codec.decode_partial(payload, key), full[key])


class TestSVDCodec(CodecContract):
    @staticmethod
    def make_low_rank(m=40, n=60, rank=5, seed=42):
        """
        Build a deterministic exactly-rank-``rank`` test matrix.
        """
        rng = np.random.default_rng(seed)
        array = rng.normal(size=(m, rank)) @ rng.normal(size=(rank, n))
        return array.astype(np.float64)

    def make_codec(self) -> SVDCodec:
        return SVDCodec(rank=6)

    def test_encode_requires_2d(self):
        """
        SVD only supports 2D arrays.
        """
        with pytest.raises(ValueError):
            self.make_codec().encode(np.zeros(10))

    def test_encode_requires_exactly_one_of_rank_or_energy(self):
        """
        SVDCodec requires exactly one of 'rank' or 'energy' to be specified.
        """
        codec = SVDCodec()
        array = make_random_matrix()
        with pytest.raises(ValueError):
            codec.encode(array)
        with pytest.raises(ValueError):
            codec.encode(array, rank=5, energy=0.9)

    def test_encode_decode_exact_rank(self):
        """
        Test that the rank 5 compressed version of a rank 5 matrix
        is the original matrix. i.e. that SVD is working correctly.
        """
        array = self.make_low_rank(rank=5)
        codec = SVDCodec(rank=5)
        payload = codec.encode(array)
        np.testing.assert_allclose(array, codec.decode(payload), atol=1e-8)

    def test_energy_truncation_picks_good_rank(self):
        """
        If we give SVD a rank 5 matrix and ask it to retain
        nearly all information, it should pick rank 5.
        """
        codec = SVDCodec(energy=0.999)
        payload = codec.encode(self.make_low_rank(rank=5))
        assert payload.rank <= 5

    def test_decode_partial_falls_back_for_fancy_indexing(self):
        """
        SVD codec falls back to full decoding when fancy indexing is used.
        This should give a warning so that the user is aware of the behavior.
        """
        codec = self.make_codec()
        payload = codec.encode(make_random_matrix())
        rows = np.array([1, 3, 5])
        cols = np.array([2, 4])
        key = np.ix_(rows, cols)
        with pytest.warns(UserWarning):
            partial = codec.decode_partial(payload, key)
        np.testing.assert_allclose(partial, codec.decode(payload)[key])

    def test_duck_array_with_svd_codec(self):
        """
        Test that a DuckArray wrapping an SVD-compressed payload behaves correctly.
        """
        codec = self.make_codec()
        array = make_random_matrix()
        payload = codec.encode(array)
        compressed = DuckArray(payload, codec)

        assert compressed.shape == array.shape
        np.testing.assert_allclose(np.asarray(compressed), codec.decode(payload))
        np.testing.assert_allclose(compressed[3, 4], codec.decode(payload)[3, 4])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
